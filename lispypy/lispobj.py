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
from rpytools import purefunction
from parser import parsable


@parsable(0)
class LispObject(object):
    _typename = 'N/A'

    @purefunction
    def typename(self):
        return self._typename

    def __init__(self, location=None):
        self.location = location

    @staticmethod
    def parse(data):
        raise NotImplementedError("parse() on base LispObject")

    def __repr__(self):
        return self.repr()

    def repr(self):
        return '()'


class LispNil(LispObject):
    _typename = 'Nil'


@parsable(6)
class LispBool(LispObject):
    _typename = 'bool'

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
    _typename = 'reference'

    def __init__(self, name, location=None):
        self.name = name
        self.location = location

    @staticmethod
    def parse(data):
        return LispReference(data)

    def repr(self):
        return self.name


class LispNativeProc(LispObject):
    _typename = 'NativeProc'

    def __init__(self, func, name, evaluate_args=True, location=None):
        self.func = func
        self.name = name
        self.evaluate_args = evaluate_args
        self.location = location

    def repr(self):
        return self.name


class LispClosure(LispObject):
    _typename = 'closure'

    def __init__(self, parameters, expression, env, location=None):
        self.parameters = parameters
        self.expression = expression
        self.location = location
        self.env = env

    def repr(self):
        return '(lambda %s %s)' % (LispCons.wrap([LispReference(s) for s in self.parameters]).repr(),
                                   self.expression.repr())


class LispMacro(LispObject):
    _typename = 'macro'

    def __init__(self, parameters, expression, location=None):
        self.parameters = parameters
        self.expression = expression
        self.location = location

    def repr(self):
        return '(create-macro %s %s)' % (LispCons.wrap([LispReference(s) for s in self.parameters]).repr(),
                                         self.expression.repr())


class LispCons(LispObject):
    _typename = 'cons'

    def __init__(self, car, cdr, location=None):
        self.car = car
        self.cdr = cdr
        self.location = location

    @staticmethod
    def wrap(l):
        if not l:
            return LispCons(LispNil(), LispNil())
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
        if isinstance(self.car, LispNil):
            return []
        elif isinstance(self.cdr, LispNil):
            return [self.car]
        assert isinstance(self.cdr, LispCons)
        return [self.car] + self.cdr.unwrap()

    def repr(self):
        if isinstance(self.cdr, LispCons) or isinstance(self.cdr, LispNil):
            items = self.unwrap()
            return '(' + ' '.join([o.repr() for o in items]) + ')'
        else:
            return '(%s . %s)' % (self.car.repr(), self.cdr.repr())


@parsable(5)
class LispString(LispObject):
    _typename = 'string'

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
