#!/usr/bin/env python

#--------------------------------------------------------------------
# The MIT License
# 
# Copyright (c) 2009 Patrick Mueller
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#--------------------------------------------------------------------

__author__  = "Patrick Mueller <pmuellr@yahoo.com>"
__date__    = "2009-03-25"
__version__ = "0.1"

from ctypes import *

import JavaScriptCoreRaw as JSC

#--------------------------------------------------------------------
# convert a string to a JSString
#--------------------------------------------------------------------
def string2jsString(string):
    if isinstance(string, str):
        return JSC.JSStringCreateWithUTF8CString(string)
    
    elif isinstance(string, unicode):
        return JSC.JSStringCreateWithUTF8CString(string.encode("utf-8"))
        
    else:
        raise TypeError, "expecting a string"

#--------------------------------------------------------------------
# convert a JSString to a string - always utf8
#--------------------------------------------------------------------
def jsString2string(jsString):
    len = JSC.JSStringGetMaximumUTF8CStringSize(jsString)
    
    result = c_char_p(" " * len)

    JSC.JSStringGetUTF8CString(jsString, result, len)
    
    return result.value

#--------------------------------------------------------------------
# 
#--------------------------------------------------------------------
class JSException(Exception):

    #----------------------------------------------------------------
    #
    #----------------------------------------------------------------
    def __init__(self, value):
        self.value = value
        
    #----------------------------------------------------------------
    #
    #----------------------------------------------------------------
    def __str__(self, value):
        return repr(self.value)
    
#--------------------------------------------------------------------
# 
#--------------------------------------------------------------------
class JSObject:
    
    #----------------------------------------------------------------
    #
    #----------------------------------------------------------------
    @staticmethod
    def fromJSValueRef(jsValueRef):
        result = JSObject()
        result.value = jsValueRef
        return result
    
    #----------------------------------------------------------------
    #
    #----------------------------------------------------------------
    def __init__(self):
        pass
    
    #----------------------------------------------------------------
    #
    #----------------------------------------------------------------
    def toString(self, jsContext):
        print "JSC.JSValueToStringCopy(%s, %s, None)" % (jsContext, self.value)
        jsString = JSC.JSValueToStringCopy(jsContext.ctx, self.value, None)
        return jsString2string(jsString)
    
    
        
#--------------------------------------------------------------------
# models a Context
#--------------------------------------------------------------------
class JSContext:

    #----------------------------------------------------------------
    # Run a garbage collect
    #----------------------------------------------------------------
    @staticmethod
    def gc():
        JSC.JSGarbageCollect(None)
    
    #----------------------------------------------------------------
    # create a new context
    #----------------------------------------------------------------
    def __init__(self, ctx=None):
        if None == ctx:
            ctx = JSC.JSGlobalContextCreate(None)
            
        self.ctx = ctx
        
    #----------------------------------------------------------------
    # check to make sure not released
    #----------------------------------------------------------------
    def checkNotReleased(self):
       if self.ctx: return
       
       raise Exception, "JSContext has been released"
    
    #----------------------------------------------------------------
    # retain a context, returning a new one
    #----------------------------------------------------------------
    def retain(self):
        self.checkNotReleased()
        
        ctx = JSC.JSGlobalContextRetain(self.ctx)
        return JSContext(ctx=ctx)
        
    #----------------------------------------------------------------
    # release a context
    #----------------------------------------------------------------
    def release(self):
        self.checkNotReleased()
        
        JSC.JSGlobalContextRelease(self.ctx)
        self.ctx = None

    #----------------------------------------------------------------
    # check a script's syntax
    #----------------------------------------------------------------
    def checkScriptSyntax(self, 
        script, 
        sourceURL=None, 
        startingLineNumber=1
        ):
        
        self.checkNotReleased()
        if not script: raise Exception, "script was None"
        
        script = string2jsString(script)
        if sourceURL: sourceURL = string2jsString(sourceURL)

        exception = JSC.JSValueRef(None)
        print "JSCheckScriptSyntax(%s, %s, %s, %d, %s)" % (str(self), jsString2string(script), str(sourceURL), startingLineNumber, str(exception))
        result = JSC.JSCheckScriptSyntax(self.ctx,
            script,
            sourceURL,
            startingLineNumber,
            byref(exception)
            )
        print "JSCheckScriptSyntax(): %d; exception: %s" % (result, str(exception))
        
        if exception.value: 
            jsObject = JSObject.fromJSValueRef(exception)
            string = jsObject.toString(self)
            
            raise JSException(string)
            
        return result