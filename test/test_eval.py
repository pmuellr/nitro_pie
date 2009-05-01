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
    def test_number(self):
        ctx = self.ctx
        
        script = "1"
        
        result = ctx.eval(script).toNumber(ctx)
        self.assertEqual(1, result)
        
    #---------------------------------------------------------------
    def test_boolean(self):
        ctx = self.ctx
        
        script = "true"
        
        result = ctx.eval(script).toBoolean(ctx)
        self.assertEqual(True, result)
        
    #---------------------------------------------------------------
    def test_string(self):
        ctx = self.ctx
        
        script = "'xyz'"
        
        result = ctx.eval(script).toString(ctx)
        self.assertEqual("xyz", result)
        
    #---------------------------------------------------------------
    def test_null(self):
        ctx = self.ctx
        
        script = "null"
        
        result = ctx.eval(script)
        self.assertTrue(result.isNull(ctx))
        
    #---------------------------------------------------------------
    def test_undefined(self):
        ctx = self.ctx
        
        script = "undefined"
        
        result = ctx.eval(script)
        self.assertTrue(result.isUndefined(ctx))
        
    #---------------------------------------------------------------
    def test_object(self):
        ctx = self.ctx
        
        script = "({x:1, y:2})"
        
        try:
            result = ctx.eval(script).asJSObjectRef()
        except JSException, e:
            _log(e.value.toString())
            raise JSException, e
        
        props = result.getPropertyNames(ctx)
        self.assertEqual(2, len(props))
        
        prop = result.getProperty(ctx,"x").toNumber(ctx)
        self.assertEqual(1, prop)
        
        prop = result.getProperty(ctx,"y").toNumber(ctx)
        self.assertEqual(2, prop)
        
        prop = result.getProperty(ctx,"z")
        self.assertTrue(prop.isUndefined(ctx))
        
    #---------------------------------------------------------------
    def test_array(self):
        ctx = self.ctx
        
        script = "[4,5,6]"
        
        try:
            result = ctx.eval(script).asJSObjectRef()
        except JSException, e:
            _log(e.value.toString())
            raise JSException, e
        
        prop = result.getProperty(ctx,"length").toNumber(ctx)
        self.assertEqual(3, prop)
        
        prop = result.getPropertyAtIndex(ctx,0).toNumber(ctx)
        self.assertEqual(4, prop)
        
        prop = result.getPropertyAtIndex(ctx,1).toNumber(ctx)
        self.assertEqual(5, prop)
        
        prop = result.getPropertyAtIndex(ctx,2).toNumber(ctx)
        self.assertEqual(6, prop)
    
        prop = result.getPropertyAtIndex(ctx,3)
        self.assertTrue(prop.isUndefined(ctx))
        
    #---------------------------------------------------------------
    def test_invalid_syntax(self):
        ctx = self.ctx
        
        script = "var 1a = 1"
        
        threw  = 0
        try:
            result = ctx.eval(script)
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

