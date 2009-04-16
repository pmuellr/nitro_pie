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
    def test_get_simple_properties(self):

        ctx = JSContext()
        
        result = ctx.evaluateScript("({a: 1, b: '2', c: true, d: null, e: undefined})")
        
        self.assertTrue(JSObject.isJSObject(result))
        
        prop_names = result.getPropertyNames()
        self.assertTrue("a" in prop_names)
        self.assertTrue("b" in prop_names)
        self.assertTrue("c" in prop_names)
        self.assertTrue("d" in prop_names)
        self.assertTrue("e" in prop_names)
        
        self.assertEquals(1,           result.getProperty("a"))
        self.assertEquals('2',         result.getProperty("b"))
        self.assertEquals(True,        result.getProperty("c"))
        self.assertEquals(None,        result.getProperty("d"))
        self.assertEquals(JSUndefined, result.getProperty("e"))
        
        ctx.release()
        
    #---------------------------------------------------------------
    def test_complex_property(self):

        ctx = JSContext()
        
        result = ctx.evaluateScript("({a: {b: 2}})")
        
        self.assertTrue(JSObject.isJSObject(result))
        
        prop_names = result.getPropertyNames()
        self.assertTrue("a" in prop_names)
        
        result_inner = result.getProperty("a")
        self.assertTrue(JSObject.isJSObject(result_inner))
        
        prop_names = result_inner.getPropertyNames()
        self.assertTrue("b" in prop_names)
        
        self.assertEquals(2, result_inner.getProperty("b"))
        
        ctx.release()
        
    #---------------------------------------------------------------
    def test_delete_property(self):

        ctx = JSContext()
        
        o = ctx.evaluateScript("({a: 1, b: 2, c: 3})")
        self.assertTrue(JSObject.isJSObject(o))
        
        for prop in "a b c".split():
            self.assertTrue(o.hasProperty(prop))
        
        self.assertTrue(o.deleteProperty("b"))

        for prop in "a c".split():
            self.assertTrue(o.hasProperty(prop))
        
        self.assertFalse(o.hasProperty("b"))
        
        log("delete property again")
        self.assertTrue(o.deleteProperty("b"))

    #---------------------------------------------------------------
    def test_set_property(self):

        ctx = JSContext()
        
        o = ctx.evaluateScript("({})")
        self.assertTrue(JSObject.isJSObject(o))

        o.setProperty("a", 1)        
        o.setProperty("b", 3.3)        
        o.setProperty("c", True)        
        o.setProperty("d", False)        
        o.setProperty("e", None)        
        o.setProperty("f", JSUndefined)        
        for prop in "a b".split():
            self.assertTrue(o.hasProperty(prop))
        
        self.assertEquals(1,           o.getProperty("a"))
        self.assertEquals(3.3,         o.getProperty("b"))
        self.assertEquals(True,        o.getProperty("c"))
        self.assertEquals(False,       o.getProperty("d"))
        self.assertEquals(None,        o.getProperty("e"))
        self.assertEquals(JSUndefined, o.getProperty("f"))
        
    #---------------------------------------------------------------
    def test_get_array_element(self):

        ctx = JSContext()
        
        o = ctx.evaluateScript("[11,22,33]")
        self.assertTrue(JSObject.isJSObject(o))

        self.assertEquals(11, o.getPropertyAtIndex(0))
        self.assertEquals(22, o.getPropertyAtIndex(1))
        self.assertEquals(33, o.getPropertyAtIndex(2))
        
    #---------------------------------------------------------------
    def test_set_array_element(self):

        ctx = JSContext()
        
        o = ctx.evaluateScript("[]")
        self.assertTrue(JSObject.isJSObject(o))

        o.setPropertyAtIndex(0, 1)        
        o.setPropertyAtIndex(1, 3.3)        
        o.setPropertyAtIndex(2, True)        
        o.setPropertyAtIndex(3, False)        
        o.setPropertyAtIndex(4, None)        
        o.setPropertyAtIndex(5, JSUndefined)        
        
        self.assertEquals(1,           o.getPropertyAtIndex(0))
        self.assertEquals(3.3,         o.getPropertyAtIndex(1))
        self.assertEquals(True,        o.getPropertyAtIndex(2))
        self.assertEquals(False,       o.getPropertyAtIndex(3))
        self.assertEquals(None,        o.getPropertyAtIndex(4))
        self.assertEquals(JSUndefined, o.getPropertyAtIndex(5))
        
#-------------------------------------------------------------------
if __name__ == '__main__':
    NitroLogging(True)
    logging(True)
    unittest.main()

