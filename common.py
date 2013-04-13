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

# Lisp interpreter error
class LispError(Exception):
	def __init__(self, message, location):
		self.message = message
		self.location = location

# Type constants
T_NIL, T_CONS, T_INT, T_FLOAT, T_STR, T_REF, T_PROC, T_CLOSURE, T_UNIQUE, T_MACRO = range(10)


_type2name = dict(zip([T_NIL, T_CONS, T_INT, T_FLOAT, T_STR, T_REF, T_PROC, T_CLOSURE, T_UNIQUE, T_MACRO],
	['T_NIL', 'T_CONS', 'T_INT', 'T_FLOAT', 'T_STR', 'T_REF', 'T_PROC', 'T_CLOSURE', 'T_UNIQUE', 'T_MACRO']))
def type_name(t):
	return _type2name[t]

# RPython imports
try:
	from rpython.rlib.jit import JitDriver, purefunction
	from rpython.rlib.objectmodel import enforceargs
	from rpython.rlib.rarithmetic import r_uint
	from rpython.rlib.rbigint import rbigint
except ImportError:
	class JitDriver(object):
		def __init__(self, *args, **kw): pass
		def jit_merge_point(self, *args, **kw): pass
		def can_enter_jit(self, *args, **kw): pass
	def purefunction(f): return f
	def enforceargs(*a, **kw): return lambda f: f
	r_uint = int
	class rbigint(long):
		@staticmethod
		def fromint(i): return rbigint(i)
		def fromdecimalstr(s): return rbigint(s)
		def repr(self): return repr(self)

@purefunction
def i2a_list(l):
	res = LispObject(T_CONS, car=l.pop(0))
	leaf = res
	while l:
		leaf.cdr = LispObject(T_CONS, car=l.pop(0))
		leaf = leaf.cdr
	leaf.cdr = LispObject(T_NIL)
	return res

@purefunction
def a2i_list(l):
	res = []
	node = l
	while node.type_ == T_CONS:
		res.append(node.car)
		node = node.cdr
	if node.type_ != T_NIL:
		res.append(node)
	return res

@purefunction
def i2a_str(s):
	return LispObject(T_STR, val_str=s)
@purefunction
def a2i_str(s):
	if s.type_ not in (T_STR, T_REF):
		raise TypeError(s)
	return s.val_str