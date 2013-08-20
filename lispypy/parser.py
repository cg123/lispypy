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

from .tokenizer import Characters
from .rpytools import purefunction
from .common import LispError

parse_list = []


def parsable(priority):
    def decorator(fn):
        parse_list.append((priority, fn))
        parse_list.sort(key=lambda t: -t[0])
        return fn
    return decorator


def parse_object(token):
    for (p, cls) in parse_list:
        try:
            res = cls.parse(token.value)
            res.location = token.location
            return res
        except:
            continue
    raise SyntaxError(token)


from . import lispobj


@purefunction
def parse(tokens):
    '''
    Transform a list of tokens into a S-expression.
    '''
    if not tokens:
        raise EOFError()
    token = tokens.pop(0)
    if token.value == Characters.SEXP_OPEN:
        res = lispobj.LispCons(car=lispobj.LispNil(),
                               cdr=lispobj.LispNil(),
                               location=token.location)
        leaf = res
        last_loc = leaf.location
        try:
            while tokens[0].value != Characters.SEXP_CLOSE:
                try:
                    leaf.car = parse(tokens)
                except EOFError:
                    raise LispError("Unexpected EOF while parsing", last_loc)
                if tokens[0].value != Characters.SEXP_CLOSE:
                    leaf.cdr = lispobj.LispCons(car=lispobj.LispNil(),
                                                cdr=lispobj.LispNil(),
                                                location=tokens[0].location)
                else:
                    leaf.cdr = lispobj.LispNil()
                leaf = leaf.cdr
                if not isinstance(leaf, lispobj.LispNil) and leaf.cdr:
                    last_loc = leaf.location
        except IndexError:
            raise LispError("Unclosed parentheses", last_loc)
        tokens.pop(0)
        return res
    elif token.value == Characters.SEXP_CLOSE:
        raise LispError("Unexpected %s" % Characters.SEXP_CLOSE, token.location)
    elif token.value == Characters.QUOTE:
        tail = lispobj.LispCons(car=parse(tokens), cdr=lispobj.LispNil(),
                                location=token.location)
        return lispobj.LispCons(car=lispobj.LispReference('quote',
                                                          token.location),
                                cdr=tail, location=token.location)
    return parse_object(token)


def parse_all(tokens):
    res = []
    while tokens:
        res.append(parse(tokens))
    return res
