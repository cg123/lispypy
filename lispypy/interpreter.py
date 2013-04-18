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

from .lispobject import *
from .common import LispError
from .rpytools import JitDriver, purefunction
from . import builtin


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


def location_name(self, sexp):
    if not sexp.loc:
        return '???'
    return sexp.loc.repr()

jitdriver = JitDriver(greens=['self_', 'sexp'], reds=['env'],
                      get_printable_location=location_name)


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
            car = self.evaluate_references(sexp.car, env, to_resolve)
            cdr = self.evaluate_references(sexp.cdr, env, to_resolve)
            return LispObject(T_CONS, car=car, cdr=cdr)
        return sexp

    def evaluate(self, sexp, env):
        jitdriver.jit_merge_point(self_=self, sexp=sexp, env=env)
        if sexp.type_ == T_REF:
            # Evaluate a reference.
            if sexp.val_str is None:
                raise LispError('Lookup of null name', sexp.loc)
            containing = env.find(sexp.val_str)
            if not containing:
                raise LispError('Name "%s" undefined' % (sexp.val_str),
                                sexp.loc)
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
                    try:
                        (var, exp) = a2i_list(sexp.cdr)
                    except ValueError:
                        raise LispError("Wrong number of arguments to define",
                                        sexp.loc)

                    name = self.check_ref(var)
                    env.set(name, self.evaluate(exp, env))
                    return LispObject(T_NIL)

                elif sexp.car.val_str == 'set!':
                    try:
                        (var, exp) = a2i_list(sexp.cdr)
                    except ValueError:
                        raise LispError("Wrong number of arguments to set!",
                                        sexp.loc)

                    name = self.check_ref(var)
                    containing = env.find(name)
                    if not containing:
                        raise LispError('Name "%s" undefined' % (name,),
                                        var.loc)
                    containing.set(name, self.evaluate(exp, env))
                    return LispObject(T_NIL)

                elif sexp.car.val_str == 'begin':
                    expressions = a2i_list(sexp.cdr)
                    val = LispObject(T_NIL)
                    for exp in expressions:
                        val = self.evaluate(exp, env)
                    return val

                elif sexp.car.val_str == 'lambda':
                    try:
                        (args, exp) = a2i_list(sexp.cdr)
                    except ValueError:
                        raise LispError("Wrong number of arguments to lambda",
                                        sexp.loc)
                    return LispObject(T_CLOSURE, car=args, cdr=exp)

                elif sexp.car.val_str == 'defmacro':
                    try:
                        (name, args, exp) = a2i_list(sexp.cdr)
                    except ValueError:
                        raise LispError("Wrong number of arguments to defmacro",
                                        sexp.loc)
                    env.set(self.check_ref(name),
                            LispObject(T_MACRO, val_str=self.check_ref(name),
                                       car=args, cdr=exp))
                    return LispObject(T_NIL)

                elif sexp.car.val_str == 'if':
                    try:
                        (cond, t, f) = a2i_list(sexp.cdr)
                    except ValueError:
                        raise LispError("Wrong number of arguments to if",
                                        sexp.loc)
                    res = self.evaluate(cond, env)
                    if builtin.a2i_bool(res):
                        return self.evaluate(t, env)
                    return self.evaluate(f, env)

            expressions = a2i_list(sexp)
            proc = self.evaluate(expressions.pop(0), env)
            if proc.type_ == T_PROC:
                try:
                    args = [self.evaluate(e, env) for e in expressions]
                    return proc.func(self, args, env)
                except LispError, e:
                    if e.location is None:
                        raise LispError(e.message, sexp.loc)
                    raise
            elif proc.type_ == T_CLOSURE:
                params = [a2i_str(s) for s in a2i_list(proc.car)]
                args = [self.evaluate(ex, env) for ex in expressions]
                return self.evaluate(proc.cdr, Environment(params, args, env))
            elif proc.type_ == T_MACRO:
                params = [self.check_ref(o) for o in a2i_list(proc.car)]
                return self.evaluate(
                    self.evaluate_references(
                        proc.cdr,
                        Environment(params, expressions, env),
                        to_resolve=params),
                    env)
            else:
                raise LispError("Attempt to call %s" % (type_name(proc.type_),),
                                proc.loc)
        else:
            raise LispError('Unknown object type %s' % (sexp.type_,), sexp.loc)

    @purefunction
    def check_int(self, o):
        if o.type_ != T_INT:
            raise LispError('Expected %s, got %s' % (type_name(T_INT),
                                                     type_name(o.type_)), o.loc)
        return o.val_int

    @purefunction
    def check_float(self, o):
        if o.type_ == T_INT:
            return float(o.val_int)
        elif o.type_ == T_FLOAT:
            return o.val_float
        raise LispError('Expected %s, got %s' % (type_name(T_FLOAT),
                                                 type_name(o.type_)), o.loc)

    @purefunction
    def check_str(self, o):
        if o.type_ != T_STR:
            raise LispError('Expected %s, got %s' % (type_name(T_STR),
                                                     type_name(o.type_)), o.loc)
        return o.val_str

    @purefunction
    def check_ref(self, o):
        if o.type_ != T_REF:
            raise LispError('Expected %s, got %s' % (type_name(T_STR),
                                                     type_name(o.type_)), o.loc)
        return o.val_str

    @purefunction
    def check_unique(self, o):
        if o.type_ != T_UNIQUE:
            raise LispError('Expected %s, got %s' % (type_name(T_STR),
                                                     type_name(o.type_)), o.loc)
        return o.val_str

    @purefunction
    def check_cons(self, o):
        if o.type_ != T_CONS:
            raise LispError('Expected %s, got %s' % (type_name(T_CONS),
                                                     type_name(o.type_)), o.loc)
        return o.car, o.cdr
