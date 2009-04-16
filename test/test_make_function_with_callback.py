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

from Nitro import *

#-------------------------------------------------------------------
def sum_callback(ctx, function, thisObject, argCount, args, exception):
    log()
    sum = 0
    for arg in args:
        sum += arg
        log("sum: %s" % str(sum))
#        log("sum: %d" % sum)
        
    log("returning: %s" % str(sum))
    return sum

#-------------------------------------------------------------------
class Test(unittest.TestCase):
    
    #---------------------------------------------------------------
    def setUp(self): pass
    def tearDown(self): pass

    #---------------------------------------------------------------
    def test_function_as_callback(self):
#        NitroLogging(True)
#        logging(True)
#       print

        ctx = JSContext()
        
        function = ctx.makeFunctionWithCallback("sum", sum_callback)
        log("function: %s" % function)
        
        globalObject = ctx.getGlobalObject()
        globalObject.setProperty("sum", function, JSPropertyAttributeNone)
        
        try:
            result = ctx.evaluateScript("sum(1,2,3,4,5)")
        except JSException, e:
            log(get_js_props(e.value))
            self.fail()
#           raise JSException, e
            
        log("result: %s" % result)
        self.assertEquals(15, result)
        
        ctx.release()
        
#-------------------------------------------------------------------
if __name__ == '__main__':
    NitroLogging(True)
    logging(True)
    unittest.main()

