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

#-------------------------------------------------------------------
# logger
#-------------------------------------------------------------------
_LOGGING = True
def _log(message):
    if not _LOGGING: return
    
    caller = inspect.stack()[1]
    (frame, filename, lineNumber, function, context, contextIndex) = caller
    filename = os.path.basename(filename)
    
    print "%s[%d]: %s(): %s" % (filename, lineNumber, function, message)

#-------------------------------------------------------------------
class Test(unittest.TestCase):
    
    #---------------------------------------------------------------
    def setUp(self): pass
    def tearDown(self): pass

    #---------------------------------------------------------------
    def test_number(self):
        script = "1"
        
        ctx = JSContext()
        
        result = ctx.evaluateScript(script)
        self.assertEqual(1, result)
        
        ctx.release()
        
    #---------------------------------------------------------------
    def test_boolean(self):
        script = "true"
        
        ctx = JSContext()
        
        result = ctx.evaluateScript(script)
        self.assertEqual(True, result)
        
        ctx.release()
        
    #---------------------------------------------------------------
    def test_string(self):
        script = "'xyz'"
        
        ctx = JSContext()
        
        result = ctx.evaluateScript(script)
        self.assertEqual("xyz", result)
        
        ctx.release()
        
    #---------------------------------------------------------------
    def test_null(self):
        script = "null"
        
        ctx = JSContext()
        
        result = ctx.evaluateScript(script)
        self.assertEqual(None, result)
        
        ctx.release()
        
    #---------------------------------------------------------------
    def test_undefined(self):
        script = "undefined"
        
        ctx = JSContext()
        
        result = ctx.evaluateScript(script)
        self.assertEqual(JSUndefined, result)
        
        ctx.release()
        
    #---------------------------------------------------------------
    def test_object(self):
        script = "({x:1, y:2})"
        
        ctx = JSContext()
        
        try:
            result = ctx.evaluateScript(script)
        except JSException, e:
            _log(e.value.toString())
            raise JSException, e
        
        self.assertEqual(True, result.isObject())
        
        props = result.getPropertyNames()
        self.assertEqual(2, len(props))
        
        prop = result.getProperty("x")
        self.assertEqual(1, prop)
        
        prop = result.getProperty("y")
        self.assertEqual(2, prop)
        
        prop = result.getProperty("z")
        self.assertEqual(JSUndefined, prop)
        
        ctx.release()
        
    #---------------------------------------------------------------
    def test_array(self):
        script = "[4,5,6]"
        
        ctx = JSContext()
        
        try:
            result = ctx.evaluateScript(script)
        except JSException, e:
            _log(e.value.toString())
            raise JSException, e
        
        self.assertEqual(True, result.isObject())
        
        prop = result.getProperty("length")
        self.assertEqual(3, prop)
        
        prop = result.getPropertyAtIndex(0)
        self.assertEqual(4, prop)
        
        prop = result.getPropertyAtIndex(1)
        self.assertEqual(5, prop)
        
        prop = result.getPropertyAtIndex(2)
        self.assertEqual(6, prop)
    
        prop = result.getPropertyAtIndex(3)
        self.assertEqual(JSUndefined, prop)
        
        ctx.release()
        
    #---------------------------------------------------------------
    def test_invalid_syntax(self):
        script = "var 1a = 1"
        
        ctx = JSContext()
        
        threw  = 0
        try:
            result = ctx.evaluateScript(script)
        except JSException, e:
            e = e.value
            props = e.getPropertyNames()
            
            name    = e.getProperty("name")    if e.hasProperty("name")    else None
            message = e.getProperty("message") if e.hasProperty("message") else None
            line    = e.getProperty("line")    if e.hasProperty("line")    else None
            
            self.assertEqual("SyntaxError", name)
            self.assertEqual("Parse error", message)
            self.assertEqual(1,             line)
            
            threw = 1
            
        self.assertEqual(1, threw, "exception not thrown")
        
        ctx.release()
        
#-------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

