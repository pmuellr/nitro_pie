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
    def test_get_set(self):
        ctx = self.ctx
        
        p1 = ctx.eval("({a: 111, b: 222})").asJSObjectRef(ctx)
        o  = ctx.eval("({})").asJSObjectRef(ctx)

        self.assertFalse(o.hasProperty(ctx, "a"))
        self.assertFalse(o.hasProperty(ctx, "b"))
        
        o.setPrototype(ctx, p1)

        self.assertTrue(o.hasProperty(ctx, "a"))
        self.assertTrue(o.hasProperty(ctx, "b"))
        
        p2 = o.getPrototype(ctx).asJSObjectRef(ctx)
        
        self.assertEquals(111, p1.getProperty(ctx, "a").toNumber(ctx))
        self.assertEquals(222, p1.getProperty(ctx, "b").toNumber(ctx))

        self.assertEquals(111,  o.getProperty(ctx, "a").toNumber(ctx))
        self.assertEquals(222,  o.getProperty(ctx, "b").toNumber(ctx))

        self.assertEquals(111, p2.getProperty(ctx, "a").toNumber(ctx))
        self.assertEquals(222, p2.getProperty(ctx, "b").toNumber(ctx))

        o.setProperty(ctx, "a", ctx.makeNumber(333))
        self.assertEquals(333,  o.getProperty(ctx, "a").toNumber(ctx))
        self.assertEquals(111, p1.getProperty(ctx, "a").toNumber(ctx))
        
#-------------------------------------------------------------------
if __name__ == '__main__':
    NitroLogging(not True)
    logging(not True)
    unittest.main()

