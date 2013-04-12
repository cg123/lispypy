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

from lispobject import *
from common import *

true = LispObject(T_UNIQUE, val_str='#t')
false = LispObject(T_UNIQUE, val_str='#f')

def i2a_bool(b):
	if b:
		return true
	else:
		return false
def a2i_bool(b):
	if b.type_ == T_UNIQUE:
		if b.val_str not in ('#t', '#f'):
			raise LispError("Expected bool - %s not valid" % b.repr_lisp(), None)
		return b.val_str == '#t'
	raise LispError("Expected bool, got %s" % b.repr_lisp(), None)

def op_add(interp, args, env):
	lh = args[0]
	rh = args[1]
	if lh.type_ == T_INT:
		if rh.type_ == T_INT:
			return LispObject(T_INT, val_int=lh.val_int + rh.val_int)
		elif rh.type_ == T_FLOAT:
			return LispObject(T_FLOAT, val_float=lh.val_int + rh.val_float)
	elif lh.type_ == T_FLOAT:
		if rh.type_ == T_INT:
			return LispObject(T_FLOAT, val_float=lh.val_float + rh.val_int)
		elif rh.type_ == T_FLOAT:
			return LispObject(T_FLOAT, val_float=lh.val_float + rh.val_float)
	else:
		raise LispError("Can't add types %s and %s" % (lh, rh), None)

def op_sub(interp, args, env):
	lh = args[0]
	rh = args[1]
	if lh.type_ == T_INT:
		if rh.type_ == T_INT:
			return LispObject(T_INT, val_int=lh.val_int - rh.val_int)
		elif rh.type_ == T_FLOAT:
			return LispObject(T_FLOAT, val_float=lh.val_int - rh.val_float)
	elif lh.type_ == T_FLOAT:
		if rh.type_ == T_INT:
			return LispObject(T_FLOAT, val_float=lh.val_float - rh.val_int)
		elif rh.type_ == T_FLOAT:
			return LispObject(T_FLOAT, val_float=lh.val_float - rh.val_float)
	else:
		raise LispError("Can't subtract types %s and %s" % (lh, rh), None)

def op_mul(interp, args, env):
	lh = args[0]
	rh = args[1]
	if lh.type_ == T_INT:
		if rh.type_ == T_INT:
			return LispObject(T_INT, val_int=lh.val_int * rh.val_int)
		elif rh.type_ == T_FLOAT:
			return LispObject(T_FLOAT, val_float=lh.val_int * rh.val_float)
	elif lh.type_ == T_FLOAT:
		if rh.type_ == T_INT:
			return LispObject(T_FLOAT, val_float=lh.val_float * rh.val_int)
		elif rh.type_ == T_FLOAT:
			return LispObject(T_FLOAT, val_float=lh.val_float * rh.val_float)
	else:
		raise LispError("Can't multiply types %s and %s" % (lh, rh), None)

def op_div(interp, args, env):
	if len(args) != 2:
		raise LispError("Expected 2 arguments, got %d" % len(args), None)
	lh = args[0]
	rh = args[1]
	try:
		if lh.type_ == T_INT:
			if rh.type_ == T_INT:
				return LispObject(T_FLOAT, val_float=lh.val_int / float(rh.val_int))
			elif rh.type_ == T_FLOAT:
				return LispObject(T_FLOAT, val_float=lh.val_int / rh.val_float)
		elif lh.type_ == T_FLOAT:
			if rh.type_ == T_INT:
				return LispObject(T_FLOAT, val_float=lh.val_float / rh.val_int)
			elif rh.type_ == T_FLOAT:
				return LispObject(T_FLOAT, val_float=lh.val_float / rh.val_float)
		else:
			raise LispError("Can't divide types %s and %s" % (lh, rh), None)
	except ZeroDivisionError:
		raise LispError("Division by zero", None)

def op_lt(interp, args, env):
	try:
		(lh, rh) = args
	except ValueError:
		raise LispError("Wrong number of arguments to op_lt", None)

	res = False
	if lh.type_ == T_INT:
		if rh.type_ == T_INT:
			res = lh.val_int < rh.val_int
		elif rh.type_ == T_FLOAT:
			res = lh.val_int < rh.val_float
	elif lh.type_ == T_FLOAT:
		if rh.type_ == T_INT:
			res = lh.val_float < rh.val_int
		elif rh.type_ == T_FLOAT:
			res = lh.val_float < rh.val_float

	return i2a_bool(res)

def op_gt(interp, args, env):
	try:
		(lh, rh) = args
	except ValueError:
		raise LispError("Wrong number of arguments to op_gt", None)

	lh_val = 0.0
	if lh.type_ == T_INT:
		lh_val = float(lh.val_int)
	else:
		lh_val = interp.check_float(lh)

	rh_val = 0.0
	if rh.type_ == T_INT:
		rh_val = float(rh.val_int)
	else:
		rh_val = interp.check_float(rh)

	return i2a_bool(lh_val > rh_val)



def equal(interp, args, env):
	try:
		(lh, rh) = args
	except ValueError:
		raise LispError("Wrong number of arguments to equal", None)
	# Either evaluate references or skip if they're the same
	if lh.type_ == T_REF:
		if rh.type_ == T_REF:
			return i2a_bool(lh.val_str == rh.val_str)
		else:
			return equal(interp, [interp.evaluate(lh, env), rh], env)
	elif rh.type_ == T_REF:
		return equal(interp, [lh, interp.evaluate(rh, env)], env)

	# Numeric comparison
	if lh.type_ == T_INT:
		if rh.type_ == T_INT:
			return i2a_bool(lh.val_int == rh.val_int)
		elif rh.type_ == T_FLOAT:
			return i2a_bool(float(lh.val_int) == rh.val_float)
	elif lh.type_ == T_FLOAT:
		if rh.type_ == T_INT:
			return i2a_bool(float(lh.val_int) == rh.val_float)
		elif rh.type_ == T_FLOAT:
			return i2a_bool(lh.val_float == rh.val_float)

	# String comparison
	if lh.type_ == T_STR:
		if rh.type_ == T_STR:
			return i2a_bool(lh.val_str == rh.val_str)

	# 'Unique' comparison
	if lh.type_ == T_UNIQUE:
		if rh.type_ == T_UNIQUE:
			return i2a_bool(lh.val_str == rh.val_str)

	# Nil comparison
	if lh.type_ == T_NIL:
		return i2a_bool(rh.type_ == T_NIL)

	raise LispError("Can't compare %s and %s" % (type_name(lh.type_), type_name(rh.type_)), None)

def display(interp, args, env):
	for o in args:
		if o.type_ == T_STR:
			print o.val_str,
		else:
			print o.repr_lisp(),
	print
	return LispObject(T_NIL)

def car(interp, args, env):
	if len(args) != 1:
		raise LispError("Too many arguments to car()", None)
	return interp.check_cons(args[0])[0]
def cdr(interp, args, env):
	if len(args) != 1:
		raise LispError("Too many arguments to cdr()", None)
	return interp.check_cons(args[0])[1]

def repr_(interp, args, env):
	if len(args) != 1:
		raise LispError("Too many arguments to repr()", None)
	return LispObject(T_STR, val_str=args[0].repr_py())

def get_all():
	return [
		LispObject(T_PROC, func=op_add, val_str='+'),
		LispObject(T_PROC, func=op_sub, val_str='-'),
		LispObject(T_PROC, func=op_mul, val_str='*'),
		LispObject(T_PROC, func=op_div, val_str='/'),
		LispObject(T_PROC, func=equal, val_str='equal'),
		LispObject(T_PROC, func=display, val_str='display'),
		LispObject(T_PROC, func=repr_, val_str='repr'),
		LispObject(T_PROC, func=car, val_str='car'),
		LispObject(T_PROC, func=cdr, val_str='cdr'),
		LispObject(T_PROC, func=op_lt, val_str='<'),
		LispObject(T_PROC, func=op_gt, val_str='>'),
	]
