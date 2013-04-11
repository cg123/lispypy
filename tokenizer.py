# Copyright (c) 2013, Charles O. Goddard
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os

from common import JitDriver, enforceargs, r_uint

class Characters(object):
	TOKEN_VALID = (
		'abcdefghijklmnopqrstuvwxyz'+
		'ABCDEFGHIJKLMNOPQRSTUVWXYZ'+
		'`~!@#$%^&*[]=+-_{}\|,.<>/?'+
		'0123456789:')
	IGNORE = ' \t\r\n'
	ENDLINE = '\n'
	PACKAGE_MARKER = ':'
	SEXP_OPEN = '('
	SEXP_CLOSE = ')'
	COMMENT = ';'
	STRING_MARKER = '"'
	QUOTE = "'"
	ESCAPE = '\\'

jitdriver = JitDriver(greens=['state','c'], reds=['fp','tokens','current_token'])

class Location(object):
	'''
	Represents the location of a parsed token.
	'''
	@enforceargs(None, str, r_uint, r_uint)
	def __init__(self, filename, line, character):
		self.filename = filename
		self.line = line
		self.character = character

	def repr(self):
		return ("<%s: line %d, column %d>" %
			(self.filename, self.line, self.character))
	__repr__ = repr

class Token(object):
	'''
	Represents a parsed token, encoding its value and location.
	'''
	def __init__(self, value, location):
		self.value = value
		self.location = location

	def repr(self):
		return "Token('%s', %s)" % (self.value, self.location.repr())
	__repr__ = repr

def tokenize(fp, filename, eof=True):
	'''
	Tokenize a LISP script from a file descriptor.
	'''
	S_DEFAULT, S_COMMENT, S_TOKEN, S_STRING = (0, 1, 2, 3)

	cur_line = r_uint(1)
	cur_char = r_uint(1)

	tokens = []
	state = S_DEFAULT
	in_token = False
	in_comment = False
	current_token = []
	token_start = Location(filename, 0, 0)
	c = os.read(fp, 1)
	while len(c) > 0:
		jitdriver.jit_merge_point(state=state, c=c, fp=fp, tokens=tokens, current_token=current_token)
		if state == S_COMMENT:
			# We're in a comment. Do nothing.
			if c in Characters.ENDLINE:
				# The line ended.
				# We are no longer in a comment.
				state = S_DEFAULT
		elif state == S_TOKEN:
			# We are in the midst of processing a token.
			if c not in Characters.TOKEN_VALID:
				# The token has ended. Add it to the list.
				state = S_DEFAULT
				tokens.append(Token(''.join(current_token), token_start))
				# Don't skip the character - process it again.
				continue
			current_token.append(c)
		elif state == S_STRING:
			# We are processing a string literal.
			if c in Characters.ESCAPE:
				# Take the next character
				current_token.append(c)
				current_token.append(os.read(fp, 1))
			current_token.append(c)
			if c in Characters.STRING_MARKER:
				tokens.append(Token(''.join(current_token), token_start))
				state = S_DEFAULT
		else:
			# We are floating in a void.
			token_start = Location(filename, cur_line, cur_char)
			if c in Characters.COMMENT:
				state = S_COMMENT
			elif c in Characters.STRING_MARKER:
				state = S_STRING
				current_token = [c]
			elif c in Characters.TOKEN_VALID:
				state = S_TOKEN
				current_token = [c]
			elif c not in Characters.IGNORE:
				tokens.append(Token(c, token_start))
		cur_char = cur_char + 1
		if c == '\n':
			cur_char = 1
			cur_line = cur_line + 1
			if not eof:
				break
		c = os.read(fp, 1)
	return tokens