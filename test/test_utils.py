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
import inspect

lib_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "../lib"))
if lib_path not in sys.path: sys.path.insert(0, lib_path)

from nitro_pie import *

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

#-------------------------------------------------------------------
def dump_exception(e, context):
    
    type = e.value.getType(context)
    if type != JSValueRef.kJSTypeObject:
        print "Exception thrown: value=%s" % e.value.toString(context)
        return
    
    e = e.value.asJSObjectRef(context)
    
    def getDefault(context, obj, property, default):
        if not obj.hasProperty(context, property):
            return default
            
        val = obj.getProperty(context, property)
        return val.toString(context)
    
    name      = getDefault(context, e, "name",      "???")
    message   = getDefault(context, e, "message",   "???") 
    sourceURL = getDefault(context, e, "sourceURL", "???")
    line      = getDefault(context, e, "line",      "???")

    print "Exception thrown: %s: %s: at %s[%s]" % (name, message, sourceURL, line)

    props = e.getPropertyNames(context)
    knownProps = "name message sourceURL line".split()
    for prop in props:
        if prop in knownProps: continue

        val = e.getProperty(context, prop)
        valStr = val.toString(context)
        
        print "   %s: %s" % (prop, valStr)
        
    print
    