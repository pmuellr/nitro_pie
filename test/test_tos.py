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

        ctx = self.ctx
        
        self.v_Object = ctx.eval("({})").asJSObjectRef(ctx)
        self.v_NaN    = float("nan")
        
    def tearDown(self):
        self.ctx.release()

    #---------------------------------------------------------------
    def test_toBoolean(self):
        ctx = self.ctx
        
        self.assertEqual(True, self.v_Object.toBoolean(ctx))
        
    #---------------------------------------------------------------
    def test_toNumber(self):
        ctx = self.ctx

        self.assertEqual("nan", str(self.v_Object.toNumber(ctx)))
        
    #---------------------------------------------------------------
    def test_toString(self):
        ctx = self.ctx

        self.assertEqual("[object Object]", self.v_Object.toString(ctx))
        
#-------------------------------------------------------------------
if __name__ == '__main__':
    NitroLogging(True)
    logging(True)
    unittest.main()

