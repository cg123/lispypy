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
from .common import *
from .rpytools import purefunction, rbigint


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

    res = False
    if isinstance(lh, LispInt):
        if isinstance(rh, LispInt):
            res = lh.val_int < rh.val_int
        elif isinstance(rh, LispFloat):
            res = float(lh.val_int) < rh.val_float
        elif isinstance(rh, LispBigint):
            res = rbigint.fromint(lh.val_int).lt(rh.val_bigint)
        else:
            raise LispError("Can't compare types")
    elif isinstance(lh, LispFloat):
        if isinstance(rh, LispInt):
            res = lh.val_float < float(rh.val_int)
        elif isinstance(rh, LispFloat):
            res = lh.val_float < rh.val_float
        elif isinstance(rh, LispBigint):
            res = lh.val_float < rh.val_bigint.tofloat()
        else:
            raise LispError("Can't compare types")
    elif isinstance(lh, LispBigint):
        if isinstance(rh, LispInt):
            res = lh.val_bigint.lt(rbigint.fromint(rh.val_int))
        elif isinstance(rh, LispFloat):
            res = lh.val_bigint.tofloat() < rh.val_float
        elif isinstance(rh, LispBigint):
            res = lh.val_bigint.lt(rh.val_bigint)
        else:
            raise LispError("Can't compare types")
    else:
        raise LispError("Can't compare types")
    return LispBool(res)


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
        LispNativeProc(func=op_add, name='+'),
        LispNativeProc(func=op_sub, name='-'),
        LispNativeProc(func=op_mul, name='*'),
        LispNativeProc(func=op_div, name='/'),
        LispNativeProc(func=display, name='display'),
        LispNativeProc(func=repr_, name='repr'),
        LispNativeProc(func=car, name='car'),
        LispNativeProc(func=cdr, name='cdr'),
        LispNativeProc(func=op_lt, name='<')
    ]
