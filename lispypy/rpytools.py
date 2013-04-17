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

# If true, print debug information about RPython imports.
DEBUG_RPYTHON = True
if DEBUG_RPYTHON:
    import os

    def debug_info(success, name):
        msg = '%s %s\n' % (('X' if success else '-'), name)
        os.write(2, msg)
else:
    def debug_info(success, name):
        pass


# enforceargs
import_success = True
try:
    from rpython.rlib.objectmodel import enforceargs
except ImportError:
    import_success = False

    # Return a dummy decorator
    def enforceargs(*a, **kw):
        return lambda f: f
debug_info(import_success, 'rpython.rlib.objectmodel.enforceargs')

# JitDriver
import_success = True
try:
    from rpython.rlib.jit import JitDriver
except ImportError:
    import_success = False

    # Stubbed out dummy JitDriver
    class JitDriver(object):
        def __init__(self, *args, **kw):
            pass

        def jit_merge_point(self, *args, **kw):
            pass

        def can_enter_jit(self, *args, **kw):
            pass
debug_info(import_success, 'rpython.rlib.jit.JitDriver')

# purefunction
import_success = True
try:
    from rpython.rlib.jit import purefunction
except ImportError:
    import_success = False

    # Dummy decorator
    def purefunction(f):
        return f
debug_info(import_success, 'rpython.rlib.jit.purefunction')

# r_uint
import_success = True
try:
    from rpython.rlib.rarithmetic import r_uint
except ImportError:
    import_success = False
    r_uint = int
debug_info(import_success, 'rpython.rlib.rarithmetic.r_uint')

# ovfcheck
import_success = True
try:
    from rpython.rlib.rarithmetic import ovfcheck
except ImportError:
    import_success = False
    ovfcheck = lambda x: x
debug_info(import_success, 'rpython.rlib.rarithmetic.ovfcheck')

# rbigint
import_success = True
try:
    from rpython.rlib.rbigint import rbigint
except ImportError:
    import_success = False

    class rbigint(long):
        @staticmethod
        def fromint(i):
            return rbigint(i)

        def fromdecimalstr(s):
            return rbigint(s)

        def repr(self):
            return repr(self)
debug_info(import_success, 'rpython.rlib.rbigint.rbigint')
