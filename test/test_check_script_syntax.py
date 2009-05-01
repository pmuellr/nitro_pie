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

#-------------------------------------------------------------------
class Test(unittest.TestCase):
    
    #---------------------------------------------------------------
    def setUp(self):
        self.ctx = JSGlobalContextRef.create()
        
    def tearDown(self):
        self.ctx.release()

    #---------------------------------------------------------------
    def test_valid_syntax(self):
        ctx = self.ctx
        
        script = "a = 1"
        
        result = ctx.checkScriptSyntax(script)
        self.assertEqual(1, result)
        
    #---------------------------------------------------------------
    def test_invalid_syntax(self):
        ctx = self.ctx
        
        script = "var 1a = 1"
        
        threw  = 0
        try:
            result = ctx.checkScriptSyntax(script, "<testing>")
        except JSException, e:
            e = e.value.asJSObjectRef()
            props = e.getPropertyNames(ctx)
            
            name    = e.getProperty(ctx,"name")    if e.hasProperty(ctx,"name")    else None
            message = e.getProperty(ctx,"message") if e.hasProperty(ctx,"message") else None
            line    = e.getProperty(ctx,"line")    if e.hasProperty(ctx,"line")    else None
            
            self.assertEqual("SyntaxError", name.toString(ctx))
            self.assertEqual("Parse error", message.toString(ctx))
            self.assertEqual(1,             line.toNumber(ctx))
            
            threw = 1
            
        self.assertEqual(1, threw, "exception not thrown")
        
#-------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

