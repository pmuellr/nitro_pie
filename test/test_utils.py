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
import inspect

#-------------------------------------------------------------------
# logger
#-------------------------------------------------------------------
LOGGING = False

def logging(bool):  
    global LOGGING
    LOGGING = bool
    
def log(message="", args=None):
    if not LOGGING: return
    
    caller = inspect.stack()[1]
    (frame, filename, lineNumber, function, context, contextIndex) = caller
    filename = os.path.basename(filename)
    
    if args:
        args    = [str(arg) for arg in args]
        message = message % tuple(args)
        
    message = message.replace("$f", function)
    message = message.replace("\n", "\\n")
    
    print "%s[%4d]: %s" % (filename, lineNumber, message)

#-------------------------------------------------------------------
def get_js_props(jsObject):

    names = jsObject.getPropertyNames()
    
    result = {}
    for name in names:
        val = jsObject.getProperty(name)
        result[name] = val

    return result
