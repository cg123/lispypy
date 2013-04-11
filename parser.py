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


try:
	from rpython.rlib.jit import purefunction
except ImportError:
	def purefunction(f): return f

from tokenizer import Characters
import interpreter

@purefunction
def parse_string(token):
	parts = [c for c in token]
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
				return ''.join(res)
		res.append(c)

@purefunction
def atom(token, location):
	try:
		ival = int(token.value)
		return interpreter.LispObject(interpreter.T_INT, val_int=ival, loc=location)
	except ValueError:
		pass
	try:
		fval = float(token.value)
		return interpreter.LispObject(interpreter.T_FLOAT, val_float=fval, loc=location)
	except ValueError:
		pass
	try:
		sval = parse_string(token.value)
		return interpreter.LispObject(interpreter.T_STR, val_str=sval, loc=location)
	except ValueError:
		pass
	return interpreter.LispObject(interpreter.T_REF, val_str=token.value, loc=location)

@purefunction
def parse(tokens):
	'''
	Transform a list of tokens into a S-expression.
	'''
	if not tokens:
		raise SyntaxError("Unexpected EOF while parsing.")
	token = tokens.pop(0)
	if token.value == Characters.SEXP_OPEN:
		if tokens[0].value == Characters.SEXP_CLOSE:
			tokens.pop(0)
			return interpreter.LispObject(interpreter.T_NIL, loc=token.location)
		
		res = interpreter.LispObject(interpreter.T_CONS, loc=token.location)
		leaf = res
		try:
			while tokens[0].value != Characters.SEXP_CLOSE:
				leaf.car = parse(tokens)
				if tokens[0].value != Characters.SEXP_CLOSE:
					leaf.cdr = interpreter.LispObject(interpreter.T_CONS, loc=tokens[0].location)
				else:
					leaf.cdr = interpreter.LispObject(interpreter.T_NIL)
				leaf = leaf.cdr
		except IndexError:
			raise SyntaxError("Unclosed parentheses")
		tokens.pop(0)
		return res
	elif token.value == Characters.SEXP_CLOSE:
		raise SyntaxError("Unexpected %s" % Characters.SEXP_CLOSE)
	elif token.value == Characters.QUOTE:
		return interpreter.LispObject(interpreter.T_CONS,
			car=atom('quote'), cdr=parse(tokens), loc=token.location)
	return atom(token, token.location)

def parse_all(tokens):
	res = []
	while tokens:
		res.append(parse(tokens))
	return res
