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

class Characters(object):
	TOKEN_VALID = (
		'abcdefghijklmnopqrstuvwxyz'+
		'ABCDEFGHIJKLMNOPQRSTUVWXYZ'+
		'`~!@#$%^&*[]=+-_{}\|,.<>/?')
	IGNORE = ' \t\r\n'
	ENDLINE = '\n'
	PACKAGE_MARKER = ':'
	SEXP_OPEN = '('
	SEXP_CLOSE = ')'
	COMMENT = ';'


def tokenize(fp):
	'''
	Tokenize a LISP script from a file descriptor.
	'''
	tokens = []
	in_token = False
	in_comment = False
	current_token = []
	c = os.read(fp, 1)
	while len(c) > 0:
		if in_comment:
			# We're in a comment. Do nothing.
			if c in Characters.ENDLINE:
				# The line ended.
				# We are no longer in a comment.
				in_comment = False
		elif in_token:
			# We are in the midst of processing a token.
			if c not in Characters.TOKEN_VALID:
				# The token has ended. Add it to the list.
				in_token = False
				tokens.append(''.join(current_token))
				# Don't skip the character - process it again.
				continue
			current_token.append(c)
		else:
			# We are floating in a void.
			if c in Characters.COMMENT:
				in_comment = True
			elif c in Characters.TOKEN_VALID:
				in_token = True
				current_token = [c]
			elif c not in Characters.IGNORE:
				tokens.append(c)
		c = os.read(fp, 1)
	return tokens

import os
import sys

def entry_point(argv):
	try:
		fp = os.open(argv[1], os.O_RDONLY, 0777)
	except IndexError:
		print "Usage: %s file" % argv[0]
		return 1
	else:
		print(list(tokenize(fp)))
	return 0

def target(*args):
	return entry_point, None

if __name__=='__main__':
	sys.exit(entry_point(sys.argv))
