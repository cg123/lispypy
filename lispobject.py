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

# Type constants
T_NIL, T_CONS, T_INT, T_FLOAT, T_STR, T_REF, T_PROC, T_CLOSURE, T_UNIQUE, T_MACRO = range(10)


_type2name = dict(zip([T_NIL, T_CONS, T_INT, T_FLOAT, T_STR, T_REF, T_PROC, T_CLOSURE, T_UNIQUE, T_MACRO],
	['T_NIL', 'T_CONS', 'T_INT', 'T_FLOAT', 'T_STR', 'T_REF', 'T_PROC', 'T_CLOSURE', 'T_UNIQUE', 'T_MACRO']))
def type_name(t):
	return _type2name[t]


class LispObject(object):
	def __init__(self, type_=T_NIL,
		val_int=0, val_float=0, val_str=None, car=None, cdr=None, func=None):
		self.type_ = type_

		self.val_int = val_int
		self.val_float = val_float
		self.val_str = val_str
		self.car = car
		self.cdr = cdr
		self.func = func

	def repr_lisp_str(self):
		res = ['"']
		for c in self.val_str:
			if c in '"\\':
				res.append('\\')
			res.append(c)
		res.append('"')
		return ''.join(res)

	def repr_lisp(self):
		# Nil
		if self.type_ == T_NIL:
			return "()"
		elif self.type_ == T_CONS:
			# We're either a linked list or an ugly cons thing.
			if self.cdr.type_ in (T_CONS, T_NIL):
				# Special case: stringify a list.
				return '(' + ' '.join([o.repr_lisp() for o in a2i_list(self)]) + ')'
			else:
				# We just have a two-cons.
				return "(%s . %s)" % (self.car.repr_lisp(), self.cdr.repr_lisp())
		elif self.type_ == T_INT:
			return str(self.val_int)
		elif self.type_ == T_FLOAT:
			return str(self.val_float)
		elif self.type_ == T_STR:
			return self.repr_lisp_str()
		elif self.type_ in (T_REF, T_UNIQUE):
			return self.val_str
		elif self.type_ == T_CLOSURE:
			return "(lambda %s %s)" % (self.car.repr_lisp(), self.cdr.repr_lisp())
		elif self.type_ == T_PROC:
			return "(proc:%s)" % (self.val_str)
		elif self.type_ == T_MACRO:
			return "(defmacro %s %s %s)" % (self.repr_lisp_str(), self.car.repr_lisp(), self.cdr.repr_lisp())


	def repr_py(self):
		head = 'LispObject'
		if self.type_ == T_NIL:
			return head + "(T_NIL)"
		elif self.type_ == T_CONS:
			return head + "(T_CONS, car=%s, cdr=%s)" % (self.car.repr_py(), self.cdr.repr_py())
		elif self.type_ == T_INT:
			return head + "(T_INT, val_int=%s)" % (self.val_int)
		elif self.type_ == T_FLOAT:
			return head + "(T_FLOAT, val_float=%s)" % (self.val_float)
		elif self.type_ == T_STR:
			return head + "(T_STR, val_str='%s')" % (self.repr_lisp_str())
		elif self.type_ == T_REF:
			return head + "(T_REF, val_str='%s')" % (self.repr_lisp_str())
		elif self.type_ == T_CLOSURE:
			return head + "(T_CLOSURE, car=%s, cdr=%s)" % (self.car.repr_py(), self.cdr.repr_py())
		elif self.type_ == T_PROC:
			return "(proc:%s)" % (self.val_str)
		elif self.type_ == T_MACRO:
			return head + "(T_MACRO, val_str=%s, car=%s, cdr=%s)" % (self.repr_lisp_str(), self.car.repr_py(), self.cdr.repr_py())
	def __repr__(self):
		return self.repr_py()

def i2a_list(l):
	res = LispObject(T_CONS, car=l.pop(0))
	leaf = res
	while l:
		leaf.cdr = LispObject(T_CONS, car=l.pop(0))
		leaf = leaf.cdr
	leaf.cdr = LispObject(T_NIL)
	return res

def a2i_list(l):
	res = []
	node = l
	while node.type_ == T_CONS:
		res.append(node.car)
		node = node.cdr
	if node.type_ != T_NIL:
		res.append(node)
	return res

def i2a_str(s):
	return LispObject(T_STR, val_str=s)
def a2i_str(s):
	if s.type_ not in (T_STR, T_REF):
		raise TypeError(s)
	return s.val_str