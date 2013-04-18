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

from .lispobj import LispObject
from .rpytools import rbigint, ovfcheck
from .parser import parsable
from .common import strtod


class LispNumber(LispObject):
    _typename = 'number'

    def op_add(self, rhs):
        raise NotImplementedError("operation on base LispNumber")

    def op_sub(self, rhs):
        raise NotImplementedError("operation on base LispNumber")

    def op_mul(self, rhs):
        raise NotImplementedError("operation on base LispNumber")

    def op_div(self, rhs):
        raise NotImplementedError("operation on base LispNumber")


@parsable(4)
class LispInt(LispNumber):
    _typename = 'int'

    def __init__(self, val, location=None):
        self.val_int = val
        self.location = location

    def op_add(self, rhs):
        if isinstance(rhs, LispInt):
            # int + int
            try:
                # regular addition
                return LispInt(ovfcheck(self.val_int + rhs.val_int))
            except OverflowError:
                # overflow - return as a bigint
                return LispBigint(rbigint.fromint(self.val_int).add(
                                  rbigint.fromint(rhs.val_int)))
        elif isinstance(rhs, LispBigint):
            # int + bigint
            return LispBigint(
                rbigint.fromint(self.val_int).add(rhs.val_bigint))
        elif isinstance(rhs, LispFloat):
            # int + float
            return LispFloat(float(self.val_int) + rhs.val_float)
        raise TypeError(rhs)

    def op_sub(self, rhs):
        if isinstance(rhs, LispInt):
            # int - int
            try:
                # regular subtraction
                return LispInt(ovfcheck(self.val_int - rhs.val_int))
            except OverflowError:
                # overflow - return as a bigint
                return LispBigint(rbigint.fromint(self.val_int).sub(
                                  rbigint.fromint(rhs.val_int)))
        elif isinstance(rhs, LispBigint):
            # int - bigint
            return LispBigint(
                rbigint.fromint(self.val_int).sub(rhs.val_bigint))
        elif isinstance(rhs, LispFloat):
            # int - float
            return LispFloat(float(self.val_int) - rhs.val_float)
        raise TypeError(rhs)

    def op_mul(self, rhs):
        if isinstance(rhs, LispInt):
            # int * int
            try:
                # regular multiplication
                return LispInt(ovfcheck(self.val_int * rhs.val_int))
            except OverflowError:
                # overflow - return as a bigint
                return LispBigint(rbigint.fromint(self.val_int).mul(
                                  rbigint.fromint(rhs.val_int)))
        elif isinstance(rhs, LispBigint):
            # int * bigint
            return LispBigint(
                rbigint.fromint(self.val_int).mul(rhs.val_bigint))
        elif isinstance(rhs, LispFloat):
            # int * float
            return LispFloat(float(self.val_int) * rhs.val_float)
        raise TypeError(rhs)

    def op_div(self, rhs):
        if isinstance(rhs, LispInt):
            # int / int
            try:
                # regular division
                return LispInt(ovfcheck(self.val_int / rhs.val_int))
            except OverflowError:
                # overflow - return as a bigint
                return LispBigint(rbigint.fromint(self.val_int).div(
                                  rbigint.fromint(rhs.val_int)))
        elif isinstance(rhs, LispBigint):
            # int / bigint
            return LispBigint(
                rbigint.fromint(self.val_int).div(rhs.val_bigint))
        elif isinstance(rhs, LispFloat):
            # int / float
            return LispFloat(float(self.val_int) / rhs.val_float)
        raise TypeError(rhs)

    @staticmethod
    def parse(data):
        return LispInt(strtod(data))

    def repr(self):
        return '%s' % self.val_int


@parsable(3)
class LispBigint(LispNumber):
    _typename = 'bigint'

    def __init__(self, val, location=None):
        self.val_bigint = val
        self.location = location

    def op_add(self, rhs):
        if isinstance(rhs, LispInt):
            # bigint + int
            return LispBigint(
                self.val_bigint.add(rbigint.fromint(rhs.val_int)))
        elif isinstance(rhs, LispBigint):
            # bigint + bigint
            return LispBigint(self.val_bigint.add(rhs.val_bigint))
        elif isinstance(rhs, LispFloat):
            # bigint + float
            return LispFloat(self.val_bigint.tofloat() + rhs.val_float)
        raise TypeError(rhs)

    def op_sub(self, rhs):
        if isinstance(rhs, LispInt):
            # bigint - int
            return LispBigint(
                self.val_bigint.sub(rbigint.fromint(rhs.val_int)))
        elif isinstance(rhs, LispBigint):
            # bigint - bigint
            return LispBigint(self.val_bigint.sub(rhs.val_bigint))
        elif isinstance(rhs, LispFloat):
            # bigint - float
            return LispFloat(self.val_bigint.tofloat() - rhs.val_float)
        raise TypeError(rhs)

    def op_mul(self, rhs):
        if isinstance(rhs, LispInt):
            # bigint * int
            return LispBigint(
                self.val_bigint.mul(rbigint.fromint(rhs.val_int)))
        elif isinstance(rhs, LispBigint):
            # bigint * bigint
            return LispBigint(self.val_bigint.mul(rhs.val_bigint))
        elif isinstance(rhs, LispFloat):
            # bigint * float
            return LispFloat(self.val_bigint.tofloat() * rhs.val_float)
        raise TypeError(rhs)

    def op_div(self, rhs):
        if isinstance(rhs, LispInt):
            # bigint / int
            return LispBigint(
                self.val_bigint.div(rbigint.fromint(rhs.val_int)))
        elif isinstance(rhs, LispBigint):
            # bigint / bigint
            return LispBigint(self.val_bigint.div(rhs.val_bigint))
        elif isinstance(rhs, LispFloat):
            # bigint / float
            return LispFloat(self.val_bigint.tofloat() / rhs.val_float)
        raise TypeError(rhs)

    @staticmethod
    def parse(data):
        for c in data:
            if c not in '0123456789':
                raise ValueError('Invalid bigint literal')
        return LispBigint(rbigint.fromdecimalstr(data))

    def repr(self):
        return self.val_bigint.repr()


@parsable(2)
class LispFloat(LispNumber):
    _typename = 'float'

    def __init__(self, val, location=None):
        self.val_float = val
        self.location = location

    def op_add(self, rhs):
        if isinstance(rhs, LispInt):
            # float + int
            return LispFloat(self.val_float + float(rhs.val_int))
        elif isinstance(rhs, LispBigint):
            # float + bigint
            return LispFloat(self.val_float + rhs.val_bigint.tofloat())
        elif isinstance(rhs, LispFloat):
            # float + float
            return LispFloat(self.val_float + rhs.val_float)
        raise TypeError(rhs)

    def op_sub(self, rhs):
        if isinstance(rhs, LispInt):
            # float - int
            return LispFloat(self.val_float - float(rhs.val_int))
        elif isinstance(rhs, LispBigint):
            # float - bigint
            return LispFloat(self.val_float - rhs.val_bigint.tofloat())
        elif isinstance(rhs, LispFloat):
            # float - float
            return LispFloat(self.val_float - rhs.val_float)
        raise TypeError(rhs)

    def op_mul(self, rhs):
        if isinstance(rhs, LispInt):
            # float * int
            return LispFloat(self.val_float * float(rhs.val_int))
        elif isinstance(rhs, LispBigint):
            # float * bigint
            return LispFloat(self.val_float * rhs.val_bigint.tofloat())
        elif isinstance(rhs, LispFloat):
            # float * float
            return LispFloat(self.val_float * rhs.val_float)
        raise TypeError(rhs)

    def op_div(self, rhs):
        if isinstance(rhs, LispInt):
            # float / int
            return LispFloat(self.val_float / float(rhs.val_int))
        elif isinstance(rhs, LispBigint):
            # float / bigint
            return LispFloat(self.val_float / rhs.val_bigint.tofloat())
        elif isinstance(rhs, LispFloat):
            # float / float
            return LispFloat(self.val_float / rhs.val_float)
        raise TypeError(rhs)

    @staticmethod
    def parse(data):
        return LispFloat(float(data))

    def repr(self):
        return '%f' % self.val_float
