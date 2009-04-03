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
    def test_valid_syntax(self):
        script = "a = 1"
        
        ctx = JSContext()
        
        result = ctx.checkScriptSyntax(script)
        self.assertEqual(1, result)
        
        ctx.release()
        
    #---------------------------------------------------------------
    def test_invalid_syntax(self):
        script = "var 1a = 1"
        
        ctx = JSContext()
        
        threw  = 0
        try:
            result = ctx.checkScriptSyntax(script, "<testing>")
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

