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
    def test_get_simple_properties(self):
        ctx = self.ctx
        
        result = ctx.eval("({a: 1, b: '2', c: true, d: null, e: undefined})").asJSObjectRef()
        
        self.assertTrue(result.isObject(ctx))
        
        prop_names = result.getPropertyNames(ctx)
        self.assertTrue("a" in prop_names)
        self.assertTrue("b" in prop_names)
        self.assertTrue("c" in prop_names)
        self.assertTrue("d" in prop_names)
        self.assertTrue("e" in prop_names)
        
        self.assertEquals(1,           result.getProperty(ctx, "a").toNumber(ctx))
        self.assertEquals('2',         result.getProperty(ctx, "b").toString(ctx))
        self.assertEquals(True,        result.getProperty(ctx, "c").toBoolean(ctx))
        self.assertTrue(result.getProperty(ctx, "d").isNull(ctx))
        self.assertTrue(result.getProperty(ctx, "e").isUndefined(ctx))
        
    #---------------------------------------------------------------
    def test_complex_property(self):
        ctx = self.ctx

        result = ctx.eval("({a: {b: 2}})").asJSObjectRef()
        
        self.assertTrue(result.isObject(ctx))
        
        prop_names = result.getPropertyNames(ctx)
        self.assertTrue("a" in prop_names)
        
        result_inner = result.getProperty(ctx, "a").asJSObjectRef()
        self.assertTrue(result_inner.isObject(ctx))
        
        prop_names = result_inner.getPropertyNames(ctx)
        self.assertTrue("b" in prop_names)
        
        self.assertEquals(2, result_inner.getProperty(ctx, "b").toNumber(ctx))
        
    #---------------------------------------------------------------
    def test_delete_property(self):
        ctx = self.ctx

        o = ctx.eval("({a: 1, b: 2, c: 3})").asJSObjectRef()
        self.assertTrue(o.isObject(ctx))
        
        for prop in "a b c".split():
            self.assertTrue(o.hasProperty(ctx, prop))
        
        self.assertTrue(o.deleteProperty(ctx, "b"))

        for prop in "a c".split():
            self.assertTrue(o.hasProperty(ctx, prop))
        
        self.assertFalse(o.hasProperty(ctx, "b"))
        
        log("delete property again")
        self.assertTrue(o.deleteProperty(ctx, "b"))

    #---------------------------------------------------------------
    def test_set_property(self):
        ctx = self.ctx

        o = ctx.eval("({})").asJSObjectRef()
        self.assertTrue(o.isObject(ctx))

        o.setProperty(ctx, "a", JSValueRef.makeNumber(ctx,1))        
        o.setProperty(ctx, "b", JSValueRef.makeNumber(ctx,3.3))        
        o.setProperty(ctx, "c", JSValueRef.makeBoolean(ctx,True))
        o.setProperty(ctx, "d", JSValueRef.makeBoolean(ctx,False))
        o.setProperty(ctx, "e", JSValueRef.makeNull(ctx))
        o.setProperty(ctx, "f", JSValueRef.makeUndefined(ctx))        
        for prop in "a b".split():
            self.assertTrue(o.hasProperty(ctx, prop))
        
        self.assertEquals(1,           o.getProperty(ctx, "a").toNumber(ctx))
        self.assertEquals(3.3,         o.getProperty(ctx, "b").toNumber(ctx))
        self.assertEquals(True,        o.getProperty(ctx, "c").toBoolean(ctx))
        self.assertEquals(False,       o.getProperty(ctx, "d").toBoolean(ctx))
        self.assertTrue(o.getProperty(ctx, "e").isNull(ctx))
        self.assertTrue(o.getProperty(ctx, "f").isUndefined(ctx))

    #---------------------------------------------------------------
    def test_set_property_compound(self):
        ctx = self.ctx

        p1 = ctx.eval("[1,2]")
        p2 = ctx.eval("({a:11, b:22})")

        o = ctx.eval("({})").asJSObjectRef()
        o.setProperty(ctx, "x", p1)
        o.setProperty(ctx, "y", p2)

        for prop in "x y".split():
            self.assertTrue(o.hasProperty(ctx, prop))
        
        t1 = o.getProperty(ctx, "x").asJSObjectRef()
        t2 = o.getProperty(ctx, "y").asJSObjectRef()
        
        self.assertEquals(2, t1.getProperty(ctx, "length").toNumber(ctx))
        self.assertEquals(1, t1.getPropertyAtIndex(ctx, 0).toNumber(ctx))
        self.assertEquals(2, t1.getPropertyAtIndex(ctx, 1).toNumber(ctx))

        self.assertEquals(11, t2.getProperty(ctx, "a").toNumber(ctx))
        self.assertEquals(22, t2.getProperty(ctx, "b").toNumber(ctx))

    #---------------------------------------------------------------
    def test_get_array_element(self):
        ctx = self.ctx

        o = ctx.eval("[11,22,33]").asJSObjectRef()
        self.assertTrue(o.isObject(ctx))

        self.assertEquals(11, o.getPropertyAtIndex(ctx, 0).toNumber(ctx))
        self.assertEquals(22, o.getPropertyAtIndex(ctx, 1).toNumber(ctx))
        self.assertEquals(33, o.getPropertyAtIndex(ctx, 2).toNumber(ctx))

    #---------------------------------------------------------------
    def test_set_array_element(self):
        ctx = self.ctx

        o = ctx.eval("[]").asJSObjectRef()
        self.assertTrue(o.isObject(ctx))

        o.setPropertyAtIndex(ctx, 0, JSValueRef.makeNumber(ctx,1))        
        o.setPropertyAtIndex(ctx, 1, JSValueRef.makeNumber(ctx,3.3))        
        o.setPropertyAtIndex(ctx, 2, JSValueRef.makeBoolean(ctx,True))
        o.setPropertyAtIndex(ctx, 3, JSValueRef.makeBoolean(ctx,False))        
        o.setPropertyAtIndex(ctx, 4, JSValueRef.makeNull(ctx))        
        o.setPropertyAtIndex(ctx, 5, JSValueRef.makeUndefined(ctx))        
        
        self.assertEquals(1,           o.getPropertyAtIndex(ctx, 0).toNumber(ctx))
        self.assertEquals(3.3,         o.getPropertyAtIndex(ctx, 1).toNumber(ctx))
        self.assertEquals(True,        o.getPropertyAtIndex(ctx, 2).toBoolean(ctx))
        self.assertEquals(False,       o.getPropertyAtIndex(ctx, 3).toBoolean(ctx))
        self.assertTrue(o.getPropertyAtIndex(ctx, 4).isNull(ctx))
        self.assertTrue(o.getPropertyAtIndex(ctx, 5).isUndefined(ctx))

    #---------------------------------------------------------------
    def test_attribute_read_only(self):
        ctx = self.ctx

        o = ctx.eval("({})").asJSObjectRef()
        
        o.setProperty(ctx, "x", JSValueRef.makeNumber(ctx, 111), kJSPropertyAttributeReadOnly)
        self.assertEquals(111, o.getProperty(ctx, "x").toNumber(ctx))
        
        o.setProperty(ctx, "x", JSValueRef.makeNumber(ctx, 222))
        self.assertEquals(111, o.getProperty(ctx, "x").toNumber(ctx))
        
        self.assertTrue(ctx, "x" in o.getPropertyNames(ctx))
        
        o.deleteProperty(ctx, "x")
        self.assertTrue("x" not in o.getPropertyNames(ctx))
        
        
    #---------------------------------------------------------------
    def test_attribute_dont_enum(self):
        ctx = self.ctx

        o = ctx.eval("({})").asJSObjectRef()

        o.setProperty(ctx, "x", JSValueRef.makeNumber(ctx, 111), kJSPropertyAttributeDontEnum)
        self.assertEquals(111, o.getProperty(ctx, "x").toNumber(ctx))
        
        o.setProperty(ctx, "x", JSValueRef.makeNumber(ctx, 222))
        self.assertEquals(222, o.getProperty(ctx, "x").toNumber(ctx))
        
        self.assertTrue("x" not in o.getPropertyNames(ctx))
        
        o.deleteProperty(ctx, "x")
        self.assertTrue("x" not in o.getPropertyNames(ctx))

    #---------------------------------------------------------------
    def test_attribute_dont_delete(self):
        ctx = self.ctx

        o = ctx.eval("({})").asJSObjectRef()
        o.setProperty(ctx, "x", JSValueRef.makeNumber(ctx, 111), kJSPropertyAttributeDontDelete)
        self.assertEquals(111, o.getProperty(ctx, "x").toNumber(ctx))
        
        o.setProperty(ctx, "x", JSValueRef.makeNumber(ctx, 222))
        self.assertEquals(222, o.getProperty(ctx, "x").toNumber(ctx))
        
        self.assertTrue("x" in o.getPropertyNames(ctx))
        
        o.deleteProperty(ctx, "x")
        self.assertTrue("x" in o.getPropertyNames(ctx))

        
#-------------------------------------------------------------------
if __name__ == '__main__':
    NitroLogging(not True)
    logging(not True)
    unittest.main()

