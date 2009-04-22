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
        self.ctx = JSContext()
        
    def tearDown(self):
        self.ctx.release()

    #---------------------------------------------------------------
    def test_isEqual(self):
        ctx = self.ctx
        
        o1 = ctx.eval("({})")
        o2 = ctx.eval("({})")
        
        self.assertTrue( o1.isEqual(o1))
        self.assertTrue( o2.isEqual(o2))
        self.assertFalse(o1.isEqual(o2))
        
    #---------------------------------------------------------------
    def test_isStrictEqual(self):
        ctx = self.ctx
        
        o1 = ctx.eval("({})")
        o2 = ctx.eval("({})")
        
        self.assertTrue( o1.isStrictEqual(o1))
        self.assertTrue( o2.isStrictEqual(o2))
        self.assertFalse(o1.isStrictEqual(o2))
        
    #---------------------------------------------------------------
    def test_isInstanceOf(self):
        ctx = self.ctx

        a     = ctx.eval("[]")
        array = ctx.eval("Array")
        
        self.assertTrue(a.isInstanceOf(array))
        
    #---------------------------------------------------------------
    def test_isFunction(self):
        ctx = self.ctx

        a = ctx.eval("[]")
        f = ctx.eval("(function() {})")
        
        self.assertFalse(a.isFunction())
        self.assertTrue(f.isFunction())
        
    #---------------------------------------------------------------
    def test_isConstructor(self):
        ctx = self.ctx

        a     = ctx.eval("[]")
        f     = ctx.eval("(function() {})")
        array = ctx.eval("Array")
        
        self.assertFalse(a.isConstructor())
        self.assertTrue(f.isConstructor())
        self.assertTrue(array.isConstructor())
        self.assertTrue(array.isFunction())
        
#-------------------------------------------------------------------
if __name__ == '__main__':
    NitroLogging(True)
    logging(True)
    unittest.main()

