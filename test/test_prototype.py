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

from Nitro import *
from test_utils import *

#-------------------------------------------------------------------
class Test(unittest.TestCase):
    
    #---------------------------------------------------------------
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    #---------------------------------------------------------------
    def test_get_set(self):

        ctx = JSContext()
        
        p1 = ctx.eval("({a: 111, b: 222})")
        o  = ctx.eval("({})")

        self.assertFalse(o.hasProperty("a"))
        self.assertFalse(o.hasProperty("b"))
        
        o.setPrototype(p1)

        self.assertTrue(o.hasProperty("a"))
        self.assertTrue(o.hasProperty("b"))
        
        p2 = o.getPrototype()
        
        self.assertEquals(111, p1.getProperty("a"))
        self.assertEquals(222, p1.getProperty("b"))

        self.assertEquals(111,  o.getProperty("a"))
        self.assertEquals(222,  o.getProperty("b"))

        self.assertEquals(111, p2.getProperty("a"))
        self.assertEquals(222, p2.getProperty("b"))

        o.setProperty("a", 333)
        self.assertEquals(333,  o.getProperty("a"))
        self.assertEquals(111, p1.getProperty("a"))
        
        ctx.release()
               
        
#-------------------------------------------------------------------
if __name__ == '__main__':
    NitroLogging(True)
    logging(True)
    unittest.main()

