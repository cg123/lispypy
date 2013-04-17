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

from .common import bytetohex, shorttohex, hexchartoint
from rpytools import rbigint, ovfcheck


class LispObject(object):
    @classmethod
    def parse(cls):
        raise NotImplementedError("parse() on base LispObject")

    def repr(self):
        return '()'


class LispNumber(LispObject):
    def op_add(self, rhs):
        raise NotImplementedError("operation on base LispNumber")

    def op_sub(self, rhs):
        raise NotImplementedError("operation on base LispNumber")

    def op_mul(self, rhs):
        raise NotImplementedError("operation on base LispNumber")

    def op_div(self, rhs):
        raise NotImplementedError("operation on base LispNumber")


class LispInt(LispObject):
    def __init__(self, val=0):
        self.val_int = val

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

    @classmethod
    def parse(cls, data):
        return LispInt(int(data))

    def repr(self):
        return '%s' % self.val_int
    __repr__ = repr


class LispBigint(LispObject):
    def __init__(self, val=rbigint.fromint(0)):
        self.val_bigint = val

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

    @classmethod
    def parse(cls, data):
        return LispBigint(rbigint.fromdecimalstr(data))

    def repr(self):
        return self.val_bigint.repr()
    __repr__ = repr


class LispFloat(LispObject):
    def __init__(self, val=0.0):
        self.val_float = val

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

    def repr(self):
        return '%f' % self.val_float
    __repr__ = repr


class LispString(LispObject):
    def __init__(self, val=u''):
        self.val_str = unicode(val)

    @classmethod
    def parse(cls, data):
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
                if c == u'"':
                    state = S_CHR
                else:
                    raise SyntaxError("Not a string literal")

            # Final state - should have read all characters by now
            elif state == S_END:
                raise SyntaxError("Trailing characters after string literal")

            # Inside a string literal
            elif state == S_CHR:
                if c == u'\\':
                    state = S_ESC
                elif c == u'"':
                    state = S_END
                else:
                    chunks.append(unicode(c))

            # Processing an escape sequence
            elif state == S_ESC:
                if c == u'x':
                    state = S_HEX
                    codepoint = 0
                    digits_left = 2
                elif c == u'u':
                    state = S_HEX
                    codepoint = 0
                    digits_left = 4
                elif c == u'U':
                    state = S_HEX
                    codepoint = 0
                    digits_left = 8
                elif c == u'n':
                    chunks.append(u'\n')
                    state = S_CHR
                elif c == u'r':
                    chunks.append(u'\r')
                    state = S_CHR
                elif c == u't':
                    chunks.append(u'\t')
                    state = S_CHR
                elif c in u'\\"':
                    chunks.append(unicode(c))
                    state = S_CHR
                else:
                    raise SyntaxError("Unknown escape sequence")

            # Processing a hex codepoint
            elif state == S_HEX:
                codepoint = (codepoint << 4) + hexchartoint(c)
                digits_left = digits_left - 1
                if not digits_left:
                    chunks.append(unichr(codepoint))
                    state = S_CHR
        if state != S_END:
            raise SyntaxError("Unterminated string literal")
        return LispString(u''.join(chunks))

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
                res.append('\\u' + shorttohex(ucp))
            else:
                # GRBgldmfsdmbvbasdf.
                res.append('\\U' + shorttohex((ucp / 0x10000) & 0xFFFF) + shorttohex(ucp & 0xFFFF))
        res.append('"')
        return ''.join(res)
    __repr__ = repr
