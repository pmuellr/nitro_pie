#!/usr/bin/env python

#-------------------------------------------------------------------
# The MIT License
# 
# Copyright (c) 2009 Patrick Mueller
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#-------------------------------------------------------------------

import os
import sys
import subprocess

import unittest

lib_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "../lib"))
if lib_path not in sys.path: sys.path.insert(0, lib_path)

from nitro_pie import *
from test_utils import *

#-------------------------------------------------------------------
class Test(unittest.TestCase):
    
    #---------------------------------------------------------------
    def setUp(self):
        self.ctx = JSGlobalContextRef.create()
        
    def tearDown(self):
        self.ctx.release()

    #---------------------------------------------------------------
    def test_simple(self):
        baseName = "simple"

        ofilename1 = "__test__%s__1__.js" % baseName
        
        ofile = open(ofilename1,"w")
        ofile.write("exports.a = 11")
        ofile.close()

        ctx = self.ctx
        ctx.addBuiltins()

        script = """
mod = require('%s')
result = mod.a
""" % (ofilename1)
        
        try:
            val = ctx.eval(script, None, "test_%s" % baseName).toNumber(ctx)
        except JSException, e:
            dump_exception(e, ctx)
            self.assertTrue(False)

        self.assertTrue(11, val)

        os.remove(ofilename1)        
        
    #---------------------------------------------------------------
    def test_simple2(self):
        baseName = "simple2"

        ofilename1 = "__test__%s__1__.js" % baseName
        ofilename2 = "__test__%s__2__.js" % baseName

        ofile = open(ofilename1,"w")
        ofile.write("other = require('%s')\n" % ofilename2)
        ofile.write("exports.a = 11\n")
        ofile.write("exports.b = other.b\n")
        ofile.close()

        ofile = open(ofilename2,"w")
        ofile.write("exports.b = 22")
        ofile.close()

        ctx = self.ctx
        ctx.addBuiltins()

        script = """
mod = require('%s')
result = mod.b
""" % (ofilename1)

        try:
            val = ctx.eval(script, None, "test_%s" % baseName).toNumber(ctx)
        except JSException, e:
            dump_exception(e, ctx)
            self.assertTrue(False)

        self.assertTrue(22, val)

        os.remove(ofilename1)        
        os.remove(ofilename2)        

    #---------------------------------------------------------------
    def test_recurse(self):
        baseName = "recurse"

        ofilename1 = "__test__%s__1__.js" % baseName
        ofilename2 = "__test__%s__2__.js" % baseName

        ofile = open(ofilename1,"w")
        ofile.write("other = require('%s')\n" % ofilename2)
        ofile.write("exports.a = 11\n")
        ofile.write("exports.b = other.b\n")
        ofile.close()

        ofile = open(ofilename2,"w")
        ofile.write("other = require('%s')\n" % ofilename1)
        ofile.write("exports.a = other.a\n")
        ofile.write("exports.b = 22\n")
        ofile.close()

        ctx = self.ctx
        ctx.addBuiltins()

        script = """
mod1 = require('%s')
mod2 = require('%s')
result = [mod1.a, mod1.b, mod2.a, mod2.b]
""" % (ofilename1, ofilename2)

        try:
            val = ctx.eval(script, None, "test_%s" % baseName).asJSObjectRef(ctx)
        except JSException, e:
            dump_exception(e, ctx)
            self.assertTrue(False)

        self.assertTrue(11, val.getPropertyAtIndex(ctx,0).toNumber(ctx))
        self.assertTrue(22, val.getPropertyAtIndex(ctx,1).toNumber(ctx))
        self.assertTrue(11, val.getPropertyAtIndex(ctx,2).toNumber(ctx))
        self.assertTrue(22, val.getPropertyAtIndex(ctx,3).toNumber(ctx))

        os.remove(ofilename1)        
        os.remove(ofilename2)        

    #---------------------------------------------------------------
    def test_recurse_change(self):
        baseName = "recurse_change"

        ofilename1 = "__test__%s__1__.js" % baseName
        ofilename2 = "__test__%s__2__.js" % baseName

        ofile = open(ofilename1,"w")
        ofile.write("other = require('%s')\n" % ofilename2)
        ofile.write("exports.a = 1\n")
        ofile.write("exports.b = other.b\n")
        ofile.close()

        ofile = open(ofilename2,"w")
        ofile.write("other = require('%s')\n" % ofilename1)
        ofile.write("exports.a = other.a\n")
        ofile.write("exports.b = 2\n")
        ofile.close()

        ctx = self.ctx
        ctx.addBuiltins()

        script = """
mod1 = require('%s')
mod2 = require('%s')
mod1.a = 33
result = mod2.a
""" % (ofilename1, ofilename2)

        try:
            val = ctx.eval(script, None, "test_%s" % baseName)
        except JSException, e:
            dump_exception(e, ctx)
            self.assertTrue(False)

        self.assertTrue(33, val.toNumber(ctx))

        os.remove(ofilename1)        
        os.remove(ofilename2)        

#-------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

