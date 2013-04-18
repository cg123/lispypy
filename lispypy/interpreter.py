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

from .lispobj import (LispObject, LispCons, LispClosure, LispReference,
                      LispString, LispNil, LispMacro, LispBool, LispNativeProc)
from .number import LispNumber, LispInt
from .common import LispError
from .rpytools import JitDriver, purefunction, enforceargs
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
    if not sexp.location:
        return '???'
    return sexp.location.repr()

jitdriver = JitDriver(greens=['self_', 'sexp'], reds=['env'],
                      get_printable_location=location_name)


class Interpreter(object):
    '''
    A LISP interpreter and its associated state.
    '''
    def __init__(self):
        builtins = builtin.get_all()
        self.root = Environment([b.name for b in builtins], builtins)

    def evaluate_references(self, sexp, env, to_resolve=()):
        if isinstance(sexp, LispReference):
            if (not to_resolve) or (sexp.name in to_resolve):
                return self.evaluate(sexp, env)
        elif isinstance(sexp, LispCons):
            car = self.evaluate_references(sexp.car, env, to_resolve)
            cdr = self.evaluate_references(sexp.cdr, env, to_resolve)
            return LispCons(car=car, cdr=cdr, location=sexp.location)
        return sexp

    def evaluate(self, sexp, env):
        jitdriver.jit_merge_point(self_=self, sexp=sexp, env=env)
        if isinstance(sexp, LispReference):
            # Evaluate a reference.
            containing = env.find(sexp.name)
            if not containing:
                raise LispError('Name "%s" undefined' % (sexp.name),
                                sexp.location)
            return containing.get(sexp.name)
        elif (isinstance(sexp, LispNil) or
              isinstance(sexp, LispNumber) or
              isinstance(sexp, LispString)):
            # Constant literal.
            return sexp
        elif isinstance(sexp, LispCons):
            # The expression is a cons. What to do?
            if isinstance(sexp.car, LispReference):
                # Sanity check
                if not isinstance(sexp.cdr, LispCons):
                    raise LispError("Expected list of arguments", sexp.location)

                if sexp.car.name == 'quote':
                    # It's a quote. Just return that sucker unevaluated.
                    return sexp.cdr
                elif sexp.car.name == 'define':
                    # We're defining a variable.
                    try:
                        (var, exp) = sexp.cdr.unwrap()
                    except ValueError:
                        raise LispError("Wrong number of arguments to define",
                                        sexp.location)

                    name = self.check_ref(var)
                    env.set(name, self.evaluate(exp, env))
                    return LispNil()

                elif sexp.car.name == 'set!':
                    try:
                        (var, exp) = sexp.cdr.unwrap()
                    except ValueError:
                        raise LispError("Wrong number of arguments to set!",
                                        sexp.location)

                    name = self.check_ref(var)
                    containing = env.find(name)
                    if not containing:
                        raise LispError('Name "%s" undefined' % (name,),
                                        var.location)
                    containing.set(name, self.evaluate(exp, env))
                    return LispNil()

                elif sexp.car.name == 'begin':
                    expressions = sexp.cdr.unwrap()
                    val = LispNil()
                    for exp in expressions:
                        val = self.evaluate(exp, env)
                    return val

                elif sexp.car.name == 'lambda':
                    try:
                        (args, exp) = sexp.cdr.unwrap()
                    except ValueError:
                        raise LispError("Wrong number of arguments to lambda",
                                        sexp.location)
                    arg_names = [self.check_ref(n) for n in self.check_cons(args)]
                    return LispClosure(parameters=arg_names, expression=exp)

                elif sexp.car.name == 'create-macro':
                    try:
                        (args, exp) = sexp.cdr.unwrap()
                    except ValueError:
                        raise LispError("Wrong number of arguments to create-macro",
                                        sexp.location)
                    arg_names = [self.check_ref(n) for n in self.check_cons(args)]
                    return LispMacro(parameters=arg_names, expression=exp)

                elif sexp.car.name == 'if':
                    try:
                        (cond, t, f) = sexp.cdr.unwrap()
                    except ValueError:
                        raise LispError("Wrong number of arguments to if",
                                        sexp.location)
                    res = self.evaluate(cond, env)
                    if self.check_bool(res):
                        return self.evaluate(t, env)
                    return self.evaluate(f, env)

            expressions = sexp.unwrap()
            proc = self.evaluate(expressions.pop(0), env)
            if isinstance(proc, LispNativeProc):
                try:
                    args = [self.evaluate(e, env) for e in expressions]
                    return proc.func(self, args, env)
                except LispError, e:
                    if e.location is None:
                        raise LispError(e.message, sexp.location)
                    raise
            elif isinstance(proc, LispClosure):
                args = [self.evaluate(ex, env) for ex in expressions]
                return self.evaluate(proc.expression,
                                     Environment(proc.parameters, args, env))
            elif isinstance(proc, LispMacro):
                return self.evaluate(
                    self.evaluate_references(
                        proc.expression,
                        Environment(proc.parameters, expressions, env),
                        to_resolve=proc.parameters),
                    env)
            else:
                raise LispError("Attempt to call %s" % (proc.typename(),),
                                proc.location)
        else:
            raise LispError("I don't understand %s" % (sexp.typename(),), sexp.location)

    @purefunction
    def check_str(self, s):
        return self.check_value(s, LispString).val_str

    @purefunction
    def check_ref(self, s):
        return self.check_value(s, LispReference).name

    @purefunction
    def check_bool(self, s):
        return self.check_value(s, LispBool).value

    @purefunction
    def check_int(self, s):
        return self.check_value(s, LispInt).val_int

    @purefunction
    def check_cons(self, s):
        return self.check_value(s, LispCons).unwrap()

    @purefunction
    def check_value(self, v, cls):
        if not isinstance(v, cls):
            raise LispError('Expected %s, got %s' % (cls._typename, v.typename()), v.location)
        return v
