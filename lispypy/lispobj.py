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

from .common import bytetohex, shorttohex, hexchartoint, strtod
from rpytools import rbigint, ovfcheck


parse_list = []


def parsable(priority):
    def decorator(fn):
        parse_list.append((priority, fn))
        parse_list.sort(key=lambda t: -t[0])
        return fn
    return decorator


def parse(token):
    for (p, cls) in parse_list:
        try:
            res = cls.parse(token.value)
            res.location = token.location
            return res
        except:
            continue
    raise SyntaxError(token)


@parsable(0)
class LispObject(object):
    @staticmethod
    def typename():
        return 'LispObject'

    def __init__(self, location=None):
        self.location = location

    @staticmethod
    def parse(data):
        raise NotImplementedError("parse() on base LispObject")

    def __repr__(self):
        return self.repr()

    def repr(self):
        return '()'
    #__repr__ = repr


class LispNil(LispObject):
    @staticmethod
    def typename():
        return 'Nil'
    pass


@parsable(6)
class LispBool(LispObject):
    @staticmethod
    def typename():
        return 'bool'

    def __init__(self, value, location=None):
        self.value = value
        self.location = location

    def repr(self):
        if self.value:
            return '#t'
        return '#f'

    @staticmethod
    def parse(data):
        if data == '#t':
            return LispBool(True)
        elif data == '#f':
            return LispBool(False)
        raise ValueError("Invalid boolean literal")


@parsable(1)
class LispReference(LispObject):
    @staticmethod
    def typename():
        return 'ref'

    def __init__(self, name, location=None):
        self.name = name
        self.location = location

    @staticmethod
    def parse(data):
        return LispReference(data)

    def repr(self):
        return self.name


class LispNativeProc(LispObject):
    @staticmethod
    def typename():
        return 'NativeProc'

    def __init__(self, func, name, location=None):
        self.func = func
        self.name = name
        self.location = location

    def repr(self):
        return self.name


class LispClosure(LispObject):
    @staticmethod
    def typename():
        return 'closure'

    def __init__(self, parameters, expression, location=None):
        self.parameters = parameters
        self.expression = expression
        self.location = location

    def repr(self):
        return '(lambda %s %s)' % (LispCons.wrap([LispReference(s) for s in self.parameters]).repr(),
                                   self.expression.repr())


class LispMacro(LispObject):
    @staticmethod
    def typename():
        return 'macro'

    def __init__(self, parameters, expression, location=None):
        self.parameters = parameters
        self.expression = expression
        self.location = location

    def repr(self):
        return '(create-macro %s %s)' % (LispCons.wrap([LispReference(s) for s in self.parameters]).repr(),
                                         self.expression.repr())


class LispCons(LispObject):
    @staticmethod
    def typename():
        return 'cons'

    def __init__(self, car, cdr, location=None):
        self.car = car
        self.cdr = cdr
        self.location = location

    @staticmethod
    def wrap(l):
        head = LispCons(None, None)
        node = head
        while l:
            node.car = l.pop(0)
            if l:
                node.cdr = LispCons(None, None)
                node = node.cdr
        node.cdr = LispNil()
        return head

    def unwrap(self):
        if isinstance(self.cdr, LispNil):
            return [self.car]
        assert isinstance(self.cdr, LispCons)
        return [self.car] + self.cdr.unwrap()

    def repr(self):
        if isinstance(self.cdr, LispCons) or isinstance(self.cdr, LispNil):
            items = self.unwrap()
            return '(' + ' '.join([o.repr() for o in items]) + ')'
        else:
            return '(%s . %s)' % (self.car.repr(), self.cdr.repr())


class LispNumber(LispObject):
    @staticmethod
    def typename():
        return 'number'

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
    @staticmethod
    def typename():
        return 'int'

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
    #__repr__ = repr


@parsable(3)
class LispBigint(LispNumber):
    @staticmethod
    def typename():
        return 'bigint'

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
    #__repr__ = repr


@parsable(2)
class LispFloat(LispNumber):
    @staticmethod
    def typename():
        return 'float'

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
    #__repr__ = repr


@parsable(5)
class LispString(LispObject):
    @staticmethod
    def typename():
        return 'string'

    def __init__(self, val, location=None):
        self.val_str = val
        self.location = location

    @staticmethod
    def parse(data):
        '''
        Parse a string in LISP source text form.
        '''
        S_BEG, S_CHR, S_ESC, S_HEX, S_END = range(5)

        chunks = []
        state = S_BEG
        digits_left = 0
        codepoint = 0

        for c in data:
            # Default state - beginning of token
            if state == S_BEG:
                if c == '"':
                    state = S_CHR
                else:
                    raise SyntaxError("Not a string literal")

            # Final state - should have read all characters by now
            elif state == S_END:
                raise SyntaxError("Trailing characters after string literal")

            # Inside a string literal
            elif state == S_CHR:
                if c == '\\':
                    state = S_ESC
                elif c == '"':
                    state = S_END
                else:
                    chunks.append(c)

            # Processing an escape sequence
            elif state == S_ESC:
                if c == 'x':
                    state = S_HEX
                    codepoint = 0
                    digits_left = 2
                elif c == '':
                    state = S_HEX
                    codepoint = 0
                    digits_left = 4
                elif c == '':
                    state = S_HEX
                    codepoint = 0
                    digits_left = 8
                elif c == 'n':
                    chunks.append('\n')
                    state = S_CHR
                elif c == 'r':
                    chunks.append('\r')
                    state = S_CHR
                elif c == 't':
                    chunks.append('\t')
                    state = S_CHR
                elif c in '\\"':
                    chunks.append(c)
                    state = S_CHR
                else:
                    raise SyntaxError("Unknown escape sequence")

            # Processing a hex codepoint
            elif state == S_HEX:
                codepoint = (codepoint << 4) + hexchartoint(c)
                digits_left = digits_left - 1
                if not digits_left:
                    chunks.append(chr(codepoint))
                    state = S_CHR
        if state != S_END:
            raise SyntaxError("Unterminated string literal")
        return LispString(''.join(chunks))

    def repr(self):
        '''
        Produce a LISP source representation of the string.
        '''
        res = ['"']
        for c in self.val_str:
            ucp = ord(c)
            if ucp < ord(' '):
                # Non-printable ASCII character. Output it as hex.
                res.append('\\x' + bytetohex(ucp))
            elif ucp < 0x7F:
                # Printable ASCII. Does it need to be escaped?
                if c in '"\\':
                    res.append('\\')
                res.append(c)
            elif ucp <= 0xFF:
                # High non-printable. Again, hex time.
                res.append('\\x' + bytetohex(ucp))
            elif ucp <= 0xFFFF:
                # Unicode shenanigans. Hrmgasdkmf.
                res.append('\\' + shorttohex(ucp))
            else:
                # GRBgldmfsdmbvbasdf.
                res.append('\\' + shorttohex((ucp / 0x10000) & 0xFFFF) + shorttohex(ucp & 0xFFFF))
        res.append('"')
        return ''.join(res)
    #__repr__ = repr
