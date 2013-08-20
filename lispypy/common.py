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


from .rpytools import ovfcheck, purefunction


# Lisp interpreter error
class LispError(Exception):
    def __init__(self, message, location=None):
        self.message = message
        self.location = location


hexdigits = '0123456789ABCDEF'
hex2dec = dict(zip('0123456789ABCDEFabcdef', range(16) + [10, 11, 12, 13, 14, 15]))


@purefunction
def bytetohex(b):
    assert(abs(b) < 256)
    d1 = (b % 16)
    d2 = (b / 16) % 16
    return hexdigits[d2] + hexdigits[d1]


@purefunction
def shorttohex(s):
    assert(s == s & 0xFFFF)
    d1 = (s % 16)
    d2 = (s / 16) % 16
    d3 = (s / 256) % 16
    d4 = (s / 4096) % 16
    return hexdigits[d4] + hexdigits[d3] + hexdigits[d2] + hexdigits[d1]


@purefunction
def hexchartoint(h):
    if h not in hex2dec:
        raise SyntaxError("Invalid hex character")
    return hex2dec[h]


@purefunction
def strtod(s):
    '''
    Parse a decimal string into an int.
    '''
    if s == '-':
        raise ValueError("This is just a minus sign.")
    res = 0
    sign = 1
    if s[0] == '-':
        sign = -1
        s = s[1:]
    for c in s:
        if c not in '0123456789':
            raise ValueError("Invalid character in int literal")
        try:
            res = ovfcheck((res * 10) + (ord(c) - ord('0')))
        except OverflowError:
            raise
    return res * sign
