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

from test_utils import *

lib_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "../lib"))
if lib_path not in sys.path: sys.path.insert(0, lib_path)

import unittest

from nitro_pie import *

#-------------------------------------------------------------------
def sum_callback(ctx, function, thisObject, args):
    sum = 0
    
    for arg in args:
        sum += arg.toNumber(ctx)
        
    result = JSValueRef.makeNumber(ctx,sum)
    
    return result

#-------------------------------------------------------------------
def array_callback(ctx, function, thisObject, args):
    arr = ctx.eval("[]").asJSObjectRef()
    
    for i, v in enumerate(args):
        arr.setPropertyAtIndex(ctx, i, v)
        
    return arr

#-------------------------------------------------------------------
def ox_callback(ctx, function, args):
    result = ctx.eval("({})")
    
    val = args[0] if len(args) else None

    result.setProperty("x", val)
        
    return result

#-------------------------------------------------------------------
class Test(unittest.TestCase):
    
    #---------------------------------------------------------------
    def setUp(self):
        self.ctx = JSGlobalContextRef.create()
        
    def tearDown(self):
        self.ctx.release()

    #---------------------------------------------------------------
    def test_function_as_callback_sum(self):
        log()
        ctx = self.ctx
        
        function = ctx.makeFunction("sum", sum_callback)
        
        globalObject = ctx.getGlobalObject()
        globalObject.setProperty(ctx, "sum", function)
        
        try:
            result = ctx.eval("sum(1,2,3,4,5)")
        except JSException, e:
            log(get_js_props(e.value))
            self.fail()
            
        self.assertEquals(15, result.toNumber(ctx))
        
    #---------------------------------------------------------------
    def test_function_as_callback_arr(self):
        ctx = self.ctx
        
        function = ctx.makeFunction("arr", array_callback)
        
        globalObject = ctx.getGlobalObject()
        globalObject.setProperty(ctx, "arr", function)
        
        try:
            result = ctx.eval("arr(66,44,22)").asJSObjectRef()
        except JSException, e:
            log(get_js_props(e.value))
            self.fail()
            
        self.assertEquals(3,  result.getProperty(ctx, "length").toNumber(ctx))
        self.assertEquals(66, result.getPropertyAtIndex(ctx,0).toNumber(ctx))
        self.assertEquals(44, result.getPropertyAtIndex(ctx,1).toNumber(ctx))
        self.assertEquals(22, result.getPropertyAtIndex(ctx,2).toNumber(ctx))
        
    #---------------------------------------------------------------
    def dont_test_constructor_as_callback_ox(self):
        ctx = self.ctx
        
        function = ctx.makeConstructorWithCallback(ox_callback)
        
        globalObject = ctx.getGlobalObject()
        globalObject.setProperty("ox", function, JSPropertyAttributeNone)
        
        try:
            result = ctx.eval("new ox(55)")
        except JSException, e:
            log(get_js_props(e.value))
            self.fail()
            
        self.assertEquals(55, result.getProperty("x"))
        
#-------------------------------------------------------------------
if __name__ == '__main__':
    logging(not True)
    unittest.main()

