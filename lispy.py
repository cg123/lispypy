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

try:
	from rpython.rlib.jit import JitDriver, purefunction
	from rpython.rlib.objectmodel import enforceargs
except ImportError:
	class JitDriver(object):
		def __init__(self, *args, **kw): pass
		def jit_merge_point(self, *args, **kw): pass
		def can_enter_jit(self, *args, **kw): pass
	def purefunction(f): return f

class Characters(object):
	TOKEN_VALID = (
		'abcdefghijklmnopqrstuvwxyz'+
		'ABCDEFGHIJKLMNOPQRSTUVWXYZ'+
		'`~!@#$%^&*[]=+-_{}\|,.<>/?'+
		'0123456789')
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

def tokenize(fp):
	'''
	Tokenize a LISP script from a file descriptor.
	'''
	S_DEFAULT, S_COMMENT, S_TOKEN, S_STRING = (0, 1, 2, 3)

	tokens = []
	state = S_DEFAULT
	in_token = False
	in_comment = False
	current_token = []
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
				tokens.append(''.join(current_token))
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
				tokens.append(''.join(current_token))
				state = S_DEFAULT
		else:
			# We are floating in a void.
			if c in Characters.COMMENT:
				state = S_COMMENT
			elif c in Characters.STRING_MARKER:
				state = S_STRING
				current_token = [c]
			elif c in Characters.TOKEN_VALID:
				state = S_TOKEN
				current_token = [c]
			elif c not in Characters.IGNORE:
				tokens.append(c)
		c = os.read(fp, 1)
	return tokens

@purefunction
def parse_string(token):
	parts = list(token)
	if parts.pop(0) != '"':
		raise ValueError("Not a string literal")

	res = []
	while parts:
		c = parts.pop(0)
		if c in Characters.ESCAPE:
			res.append(parts.pop(0))
		elif c in Characters.STRING_MARKER:
			if parts:
				raise ValueError("Trailing characters in string literal")
			else:
				return LispString(''.join(res))
		res.append(c)

@purefunction
def parse(tokens):
	'''
	Transform a list of tokens into a S-expression.
	'''
	if not tokens:
		raise SyntaxError("Unexpected EOF while parsing.")
	token = tokens.pop(0)
	if token == Characters.SEXP_OPEN:
		contents = []
		try:
			while tokens[0] != Characters.SEXP_CLOSE:
				contents.append(parse(tokens))
		except IndexError:
			raise SyntaxError("Unclosed parenthesis")
		tokens.pop(0)
		return contents
	elif token == Characters.SEXP_CLOSE:
		raise SyntaxError("Unexpected %s" % Characters.SEXP_CLOSE)
	elif token == Characters.QUOTE:
		return ['quote', parse(tokens)]
	return token

def parse_all(tokens):
	res = []
	while tokens:
		res.append(parse(tokens))
	return res

def entry_point(argv):
	try:
		fp = os.open(argv[1], os.O_RDONLY, 0777)
	except IndexError:
		print "Usage: %s file" % argv[0]
		return 1
	else:
		print(parse_all(tokenize(fp)))
	return 0

import sys

if __name__ == '__main__':
	sys.exit(entry_point(sys.argv))
