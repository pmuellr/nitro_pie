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

lib_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "../lib"))
if lib_path not in sys.path: sys.path.insert(0, lib_path)

import unittest

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
    def test_isEqual(self):
        ctx = self.ctx
        
        o1 = ctx.eval("({})")
        o2 = ctx.eval("({})")
        
        self.assertTrue( o1.isEqual(ctx,o1))
        self.assertTrue( o2.isEqual(ctx,o2))
        self.assertFalse(o1.isEqual(ctx,o2))
        
    #---------------------------------------------------------------
    def test_isStrictEqual(self):
        ctx = self.ctx
        
        o1 = ctx.eval("({})")
        o2 = ctx.eval("({})")
        
        self.assertTrue( o1.isStrictEqual(ctx,o1))
        self.assertTrue( o2.isStrictEqual(ctx,o2))
        self.assertFalse(o1.isStrictEqual(ctx,o2))
        
    #---------------------------------------------------------------
    def test_isInstanceOf(self):
        ctx = self.ctx

        a     = ctx.eval("[]")
        array = ctx.eval("Array").asJSObjectRef(ctx)
        
        self.assertTrue(a.isInstanceOf(ctx,array))
        
    #---------------------------------------------------------------
    def test_isFunction(self):
        ctx = self.ctx

        a = ctx.eval("[]").asJSObjectRef(ctx)
        f = ctx.eval("(function() {})").asJSObjectRef(ctx)
        
        self.assertFalse(a.isFunction(ctx))
        self.assertTrue(f.isFunction(ctx))
        
    #---------------------------------------------------------------
    def test_isConstructor(self):
        ctx = self.ctx

        a     = ctx.eval("[]").asJSObjectRef(ctx)
        f     = ctx.eval("(function() {})").asJSObjectRef(ctx)
        array = ctx.eval("Array").asJSObjectRef(ctx)
        
        self.assertFalse(a.isConstructor(ctx))
        self.assertTrue(f.isConstructor(ctx))
        self.assertTrue(array.isConstructor(ctx))
        self.assertTrue(array.isFunction(ctx))
        
#-------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

