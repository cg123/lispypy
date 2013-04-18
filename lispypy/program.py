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

import os
from . import tokenizer, parser, interpreter, common, lispobj


def main(argv):
    try:
        if argv[1] == '-':
            fd = 0
        else:
            fd = os.open(argv[1], os.O_RDONLY, 0777)
    except IndexError:
        print "Usage: %s file" % argv[0]
        return 1
    else:
        interp = interpreter.Interpreter()
        if fd == 0:
            try:
                while True:
                    os.write(1, '> ')
                    try:
                        tokens = tokenizer.tokenize(fd, 'stdin', eof=False)
                        exps = parser.parse_all(tokens)
                        for exp in exps:
                            res = interp.evaluate(exp, interp.root)
                            if not isinstance(res, lispobj.LispNil):
                                print res.repr()
                    except common.LispError, e:
                        print '!! At %s:\n\t%s' % (e.location.repr(),
                                                   e.message)
            except KeyboardInterrupt:
                pass
        else:
            try:
                tokens = tokenizer.tokenize(fd, argv[1])
                for o in parser.parse_all(tokens):
                    interp.evaluate(o, interp.root)
            except interpreter.LispError, e:
                print '!! At %s:\n\t%s' % (e.location.repr(), e.message)
    return 0
