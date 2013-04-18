# Copyright (c) 2013, Charles O. Goddard
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from .lispobj import *
from .number import *
from .common import *
from .rpytools import purefunction, rbigint


def define(interp, args, env):
    try:
        (name, exp) = args
    except ValueError:
        raise LispError("Wrong number of arguments to define")
    name_str = interp.check_ref(name)
    value = interp.evaluate(exp, env)
    env.set(name_str, value)
    return LispNil()


def quote(interp, args, env):
    if len(args) != 1:
        raise LispError("Wrong number of arguments to quote")
    return args[0]


def setbang(interp, args, env):
    try:
        (name, exp) = args
    except ValueError:
        raise LispError("Wrong number of arguments to set!")
    name_str = interp.check_ref(name)
    value = interp.evaluate(exp, env)
    containing = env.find(name_str)
    if not containing:
        raise LispError('Name "%s" undefined' % (name_str,))
    containing.set(name_str, value)
    return LispNil()


def lambda_(interp, args, env):
    try:
        (argrefs, exp) = args
    except ValueError:
        raise LispError("Wrong number of arguments to lambda",
                        sexp.location)
    arg_names = [interp.check_ref(n) for n in interp.check_cons(argrefs)]
    return LispClosure(parameters=arg_names, expression=exp, env=env)


def createmacro(interp, args, env):
    try:
        (argrefs, exp) = args
    except ValueError:
        raise LispError("Wrong number of arguments to create-macro",
                        sexp.location)
    arg_names = [interp.check_ref(n) for n in interp.check_cons(argrefs)]
    return LispMacro(parameters=arg_names, expression=exp)


@purefunction
def op_add(interp, args, env):
    try:
        (lh, rh) = [interp.check_value(v, LispNumber) for v in args]
    except ValueError:
        raise LispError("Wrong number of operands")
    return lh.op_add(rh)


@purefunction
def op_sub(interp, args, env):
    try:
        (lh, rh) = [interp.check_value(v, LispNumber) for v in args]
    except ValueError:
        raise LispError("Wrong number of operands")
    return lh.op_sub(rh)


@purefunction
def op_mul(interp, args, env):
    try:
        (lh, rh) = [interp.check_value(v, LispNumber) for v in args]
    except ValueError:
        raise LispError("Wrong number of operands")
    return lh.op_mul(rh)


@purefunction
def op_div(interp, args, env):
    try:
        (lh, rh) = [interp.check_value(v, LispNumber) for v in args]
    except ValueError:
        raise LispError("Wrong number of operands")
    return lh.op_div(rh)


@purefunction
def op_lt(interp, args, env):
    try:
        (lh, rh) = [interp.check_value(v, LispNumber) for v in args]
    except ValueError:
        raise LispError("Wrong number of operands")

    typematch = True
    res = False
    if isinstance(lh, LispInt):
        if isinstance(rh, LispInt):
            res = lh.val_int < rh.val_int
        elif isinstance(rh, LispFloat):
            res = float(lh.val_int) < rh.val_float
        elif isinstance(rh, LispBigint):
            res = rbigint.fromint(lh.val_int).lt(rh.val_bigint)
        else:
            typematch = False
    elif isinstance(lh, LispFloat):
        if isinstance(rh, LispInt):
            res = lh.val_float < float(rh.val_int)
        elif isinstance(rh, LispFloat):
            res = lh.val_float < rh.val_float
        elif isinstance(rh, LispBigint):
            res = lh.val_float < rh.val_bigint.tofloat()
        else:
            typematch = False
    elif isinstance(lh, LispBigint):
        if isinstance(rh, LispInt):
            res = lh.val_bigint.lt(rbigint.fromint(rh.val_int))
        elif isinstance(rh, LispFloat):
            res = lh.val_bigint.tofloat() < rh.val_float
        elif isinstance(rh, LispBigint):
            res = lh.val_bigint.lt(rh.val_bigint)
        else:
            typematch = False
    if not typematch:
        raise LispError("Can't compare %s and %s" % (lh.typename(),
                                                     rh.typename()))
    return LispBool(res)


@purefunction
def op_gt(interp, args, env):
    try:
        (lh, rh) = [interp.check_value(v, LispNumber) for v in args]
    except ValueError:
        raise LispError("Wrong number of operands")

    typematch = True
    res = False
    if isinstance(lh, LispInt):
        if isinstance(rh, LispInt):
            res = lh.val_int > rh.val_int
        elif isinstance(rh, LispFloat):
            res = float(lh.val_int) > rh.val_float
        elif isinstance(rh, LispBigint):
            res = rbigint.fromint(lh.val_int).gt(rh.val_bigint)
        else:
            typematch = False
    elif isinstance(lh, LispFloat):
        if isinstance(rh, LispInt):
            res = lh.val_float > float(rh.val_int)
        elif isinstance(rh, LispFloat):
            res = lh.val_float > rh.val_float
        elif isinstance(rh, LispBigint):
            res = lh.val_float > rh.val_bigint.tofloat()
        else:
            typematch = False
    elif isinstance(lh, LispBigint):
        if isinstance(rh, LispInt):
            res = lh.val_bigint.gt(rbigint.fromint(rh.val_int))
        elif isinstance(rh, LispFloat):
            res = lh.val_bigint.tofloat() > rh.val_float
        elif isinstance(rh, LispBigint):
            res = lh.val_bigint.gt(rh.val_bigint)
        else:
            typematch = False
    if not typematch:
        raise LispError("Can't compare %s and %s" % (lh.typename(),
                                                     rh.typename()))
    return LispBool(res)


@purefunction
def _equal(interp, env, lh, rh):
    # Check for the easy way out
    if lh is rh:
        return True

    if isinstance(lh, LispReference):
        if not isinstance(rh, LispReference):
            return False
        return lh.name == rh.name
    elif isinstance(lh, LispNumber):
        # Numeric comparison. Dear lord.
        if isinstance(lh, LispInt):
            if isinstance(rh, LispInt):
                return lh.val_int == rh.val_int
            elif isinstance(rh, LispBigint):
                return rbigint.fromint(lh.val_int).eq(rh.val_bigint)
            elif isinstance(rh, LispFloat):
                return float(lh.val_int) == rh.val_float
        elif isinstance(lh, LispFloat):
            if isinstance(rh, LispInt):
                return lh.val_float == float(rh.val_int)
            elif isinstance(rh, LispBigint):
                return lh.val_float == rh.val_bigint.tofloat()
            elif isinstance(rh, LispFloat):
                return lh.val_float == rh.val_float
        elif isinstance(lh, LispBigint):
            if isinstance(rh, LispInt):
                return lh.val_bigint.eq(rbigint.fromint(rh.val_int))
            elif isinstance(rh, LispBigint):
                return lh.val_bigint.eq(rh.val_bigint)
            elif isinstance(rh, LispFloat):
                return lh.val_bigint.tofloat() == rh.val_float
    elif isinstance(lh, LispString):
        if not isinstance(rh, LispString):
            return False
        return lh.val_str == rh.val_str
    elif isinstance(lh, LispBool):
        if not isinstance(rh, LispBool):
            return False
        return lh.value == rh.value
    elif isinstance(lh, LispNil):
        return isinstance(rh, LispNil)
    elif isinstance(lh, LispCons):
        if not isinstance(rh, LispCons):
            return False
        nl, nr = (lh, rh)
        while isinstance(nl, LispCons):
            if not _equal(interp, env, nl.car, nr.car):
                return False
            nl, nr = (nl.cdr, nr.cdr)
        return _equal(interp, env, nl, nr)
    raise LispError("Can't compare %s and %s" % (lh.typename(),
                                                 rh.typename()))


@purefunction
def equal(interp, args, env):
    try:
        (lh, rh) = args
    except ValueError:
        raise LispError("Wrong number of operands")
    return LispBool(_equal(interp, env, lh, rh))


def display(interp, args, env):
    for o in args:
        if isinstance(o, LispString):
            print o.val_str,
        else:
            print o.repr(),
    print
    return LispNil()


@purefunction
def car(interp, args, env):
    if len(args) != 1:
        raise LispError("Too many arguments to car()")
    return interp.check_value(args[0], LispCons).car


@purefunction
def cdr(interp, args, env):
    if len(args) != 1:
        raise LispError("Too many arguments to cdr()")
    return interp.check_value(args[0], LispCons).cdr


@purefunction
def repr_(interp, args, env):
    if len(args) != 1:
        raise LispError("Too many arguments to repr()")
    return LispString(args[0].repr())


@purefunction
def get_all():
    return [
        LispNativeProc(func=define, name='define', evaluate_args=False),
        LispNativeProc(func=quote, name='quote', evaluate_args=False),
        LispNativeProc(func=setbang, name='set!', evaluate_args=False),
        LispNativeProc(func=lambda_, name='lambda', evaluate_args=False),
        LispNativeProc(func=createmacro, name='create-macro', evaluate_args=False),
        LispNativeProc(func=op_add, name='+'),
        LispNativeProc(func=op_sub, name='-'),
        LispNativeProc(func=op_mul, name='*'),
        LispNativeProc(func=op_div, name='/'),
        LispNativeProc(func=display, name='display'),
        LispNativeProc(func=repr_, name='repr'),
        LispNativeProc(func=car, name='car'),
        LispNativeProc(func=cdr, name='cdr'),
        LispNativeProc(func=op_lt, name='<'),
        LispNativeProc(func=op_gt, name='>'),
        LispNativeProc(func=equal, name='equal')
    ]
