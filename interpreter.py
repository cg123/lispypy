# Copyright (c) 2013, Charles O. Goddard
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must lispobject.a2ioduce the above copyright notice,
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

from lispobject import *
import builtin

try:
	from rpython.rlib.objectmodel import r_dict, _hash_string
except ImportError:
	class r_dict(dict):
		def __init__(self, key_eq, key_hash, force_non_null=False): super(r_dict, self).__init__()
	_hash_string = None
	pass

try:
	from rpython.rlib.jit import JitDriver
except ImportError:
	class JitDriver(object):
		def __init__(self, *args, **kw): pass
		def jit_merge_point(self, *args, **kw): pass
		def can_enter_jit(self, *args, **kw): pass

class Environment(object):
	'''
	Represents a scope in the LISP environment.
	'''
	def __init__(self, parms=[], args=[], outer=None):
		self.dict = {}
		for i in range(len(parms)):
			self.dict[parms[i]] = args[i]
		self.outer = outer

	def get(self, key):
		return self.dict[key]
	def set(self, key, value):
		self.dict[key] = value

	def keys(self):
		return self.dict.keys()

	def find(self, var):
		if var in self.dict:
			return self
		elif not self.outer:
			return None
		return self.outer.find(var)

jitdriver = JitDriver(greens=['sexp'], reds=['env'])

class Interpreter(object):
	'''
	A LISP interpreter and its associated state.
	'''
	def __init__(self):
		builtins = builtin.get_all()
		self.root = Environment([b.val_str for b in builtins], builtins)

	def evaluate_references(self, sexp, env, to_resolve=()):
		if sexp.type_ == T_REF:
			if (not to_resolve) or (sexp.val_str in to_resolve):
				return self.evaluate(sexp, env)
		elif sexp.type_ == T_CONS:
			return LispObject(T_CONS,
				car=self.evaluate_references(sexp.car, env, to_resolve),
				cdr=self.evaluate_references(sexp.cdr, env, to_resolve))
		return sexp

	def evaluate(self, sexp, env):
		jitdriver.jit_merge_point(sexp=sexp, env=env)
		if sexp.type_ == T_REF:
			# Evaluate a reference.
			if sexp.val_str is None:
				raise ValueError('Lookup of null name')
			containing = env.find(sexp.val_str)
			if not containing:
				raise NameError('Name "%s" undefined' % sexp.val_str)
			return containing.get(sexp.val_str)
		elif sexp.type_ in (T_NIL, T_INT, T_FLOAT, T_STR):
			# Constant literal.
			return sexp
		elif sexp.type_ == T_CONS:
			# The expression is a cons. What to do?
			if sexp.car.type_ == T_REF:
				if sexp.car.val_str == 'quote':
					# It's a quote. Just return that sucker unevaluated.
					return sexp.cdr
				elif sexp.car.val_str == 'define':
					# We're defining a variable.
					(var, exp) = a2i_list(sexp.cdr)
					name = self.check_ref(var)
					env.set(name, self.evaluate(exp, env))
					return LispObject(T_NIL)
				elif sexp.car.val_str == 'set!':
					(var, exp) = a2i_list(sexp.cdr)
					name = self.check_ref(var)
					containing = env.find(name)
					if not containing:
						raise NameError(name)
					containing.set(name, self.evaluate(exp, env))
					return LispObject(T_NIL)
				elif sexp.car.val_str == 'begin':
					expressions = a2i_list(sexp.cdr)
					val = LispObject(T_NIL)
					for exp in expressions:
						val = self.evaluate(exp, env)
					return val
				elif sexp.car.val_str == 'lambda':
					(args, exp) = a2i_list(sexp.cdr)
					return LispObject(T_CLOSURE, car=args, cdr=exp)
				elif sexp.car.val_str == 'defmacro':
					(name, args, exp) = a2i_list(sexp.cdr)
					env.set(self.check_ref(name), LispObject(T_MACRO, val_str=self.check_ref(name),
						car=args, cdr=exp))
					return LispObject(T_NIL)
			expressions = a2i_list(sexp)
			proc = self.evaluate(expressions.pop(0), env)
			if proc.type_ == T_PROC:
				return proc.func(self, [self.evaluate(e, env) for e in expressions], env)
			elif proc.type_ == T_CLOSURE:
				return self.evaluate(proc.cdr, Environment([a2i_str(s) for s in a2i_list(proc.car)], [self.evaluate(e, env) for e in expressions], env))
			elif proc.type_ == T_MACRO:
				params = [self.check_ref(o) for o in a2i_list(proc.car)]
				return self.evaluate_references(proc.cdr, Environment([a2i_str(s) for s in a2i_list(proc.car)], expressions, env), to_resolve=params)
			else:
				raise TypeError(proc.type_)
		else:
			raise RuntimeError('Unknown object type %s' % sexp.type_)

	def check_int(self, o):
		if o.type_ != T_INT:
			raise TypeError('Expected %s, got %s' % (type_name(T_INT), type_name(o.type_)))
		return o.val_int
	def check_float(self, o):
		if o.type_ == T_INT:
			return float(o.val_int)
		elif o.type_ == T_FLOAT:
			return o.val_float
		raise TypeError('Expected %s, got %s' % (type_name(T_FLOAT), type_name(o.type_)))
	def check_str(self, o):
		if o.type_ != T_STR:
			raise TypeError('Expected %s, got %s' % (type_name(T_STR), type_name(o.type_)))
		return o.val_str
	def check_ref(self, o):
		if o.type_ != T_REF:
			raise TypeError('Expected %s, got %s' % (type_name(T_STR), type_name(o.type_)))
		return o.val_str
	def check_unique(self, o):
		if o.type_ != T_UNIQUE:
			raise TypeError('Expected %s, got %s' % (type_name(T_STR), type_name(o.type_)))
		return o.val_str
	def check_cons(self, o):
		if o.type_ != T_CONS:
			raise TypeError('Expected %s, got %s' % (type_name(T_CONS), type_name(o.type_)))
		return o.car, o.cdr

	def add_builtins(self):
		pass
