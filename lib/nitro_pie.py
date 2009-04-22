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

#--------------------------------------------------------------------
#
# A Python wrapper for JavaScriptCore (JSC).  JSC is documented here:
#
# http://developer.apple.com/documentation/Carbon/Reference/WebKit_JavaScriptCore_Ref/
#--------------------------------------------------------------------

__author__  = "Patrick Mueller <pmuellr@yahoo.com>"
__date__    = "2009-04-22"
__version__ = "0.5"

import ctypes
import ctypes.util
import inspect
import os

#-------------------------------------------------------------------
# logger
#-------------------------------------------------------------------
_LOGGING = False
def _log(message=""):
    if not _LOGGING: return
    
    caller = inspect.stack()[1]
    (frame, filename, lineNumber, function, context, contextIndex) = caller
    filename = os.path.basename(filename)
    
    print "%s[%d]: %s(): %s" % (filename, lineNumber, function, message)

def NitroLogging(on):
    global _LOGGING
    _LOGGING = on

#-------------------------------------------------------------------
JSUndefined = "{{undefined}}"
"""Represents JavaScript's undefined value"""

#-------------------------------------------------------------------
JSPropertyAttributeNone       = 0
"""Constant used when setting property values with JSObject::setProperty()"""
JSPropertyAttributeReadOnly   = 1 << 1
"""Constant used when setting property values with JSObject::setProperty()"""
JSPropertyAttributeDontEnum   = 1 << 2 
"""Constant used when setting property values with JSObject::setProperty()"""
JSPropertyAttributeDontDelete = 1 << 3 
"""Constant used when setting property values with JSObject::setProperty()"""

#--------------------------------------------------------------------
def _string2jsString(string):
    """Convert a string to a JSString
    
    The result will need to be release()'d when you're done with it.
    
    @rtype:         JSString
    @return:        the JSString coverted from the Python string
    @type  string:  str | unicode
    @param string:  Python string to convert to a JSString
    """
    
    if not string: return None
    
    if isinstance(string, str):
        return _JSStringCreateWithUTF8CString(string)
    
    elif isinstance(string, unicode):
        return _string2jsString(string.encode("utf-8"))
        
    else:
        raise TypeError, "expecting a string"

#--------------------------------------------------------------------
def _jsString2string(jsString):
    """Convert a JSString to a string - always utf8"""
    _log()
    
    if not jsString: return None
    if isinstance(jsString, str): return jsString
    
    len = _JSStringGetMaximumUTF8CStringSize(jsString)
    
    result = ctypes.c_char_p(" " * len)

    _JSStringGetUTF8CString(jsString, result, len)
    
    return result.value

#--------------------------------------------------------------------
class JSContext:
    """Models a Context
    
    A context maintains the variables and environment that a
    script runs in."""

    #----------------------------------------------------------------
    @staticmethod
    def gc():
        """Performs a garbage collection
        
        You do not need to call this to run
        the garbage collector, but you can call if if you
        explicitly want to run it.
        """
        _log()
        
        _JSGarbageCollect(None)
    
    #----------------------------------------------------------------
    def __init__(self, ctx=None):
        """Creates a new JSContext object
        
        @type    ctx:  JSContext
        @param   ctx:  an existing JSContext to base this on; for internal use only
        @rtype:  JSContext
        @return: the new JSContext created
        """
        _log("JSContext() - ctx: %s" % (str(ctx)))
            
        if None == ctx:
            self.ctx = _JSGlobalContextCreate(None)
            self.ref = 1
            return
            
        self.ctx = ctx
        self.ref = 0
        
    #----------------------------------------------------------------
    def __del__(self):
        """Intended for internal use only"""
        _log("JSContext() - ctx: %s" % (str(self.ctx)))
        
        while self.ctx: self.release()
    
    #----------------------------------------------------------------
    def __str__(self):
        """Intended for internal use only
        
        @rtype:  str
        @return: a string representation of this object
        """
        
        return "JSContext{ctx=%s, ref=%d}" % (str(self.ctx), self.ref)
    
    #----------------------------------------------------------------
    def _checkAllocated(self):
        """Check to make sure the context is not released."""
        _log()
        
        if self.ctx: return
       
        raise Exception, "JSContext has been released"
    
    #----------------------------------------------------------------
    def _retain(self):
        """Intended for internal use only"""
        _log()
        
        self._checkAllocated()
        _JSGlobalContextRelease(self.ctx)
        self.ref += 1
        return self
        
    #----------------------------------------------------------------
    def release(self):
        """Releases the context
        
        You should release the context when you are finished
        with it."""
        _log()
        
        if self.ref <= 0: 
            self.ctx = None
            return
        
        self._checkAllocated()
        _JSGlobalContextRelease(self.ctx)
        self.ref -= 1
        
        if not self.ref: self.ctx = None

    #----------------------------------------------------------------
    def checkScriptSyntax(self, 
        script, 
        sourceURL=None, 
        startingLineNumber=1
        ):
        """Checks a script for validity without running it
        
        @rtype:                    boolean
        @return:                   whether the script is syntactically correct
        @type  script:             str | unicode
        @param script:             the source code for the script to check
        @type  sourceURL:          str | unicode
        @param sourceURL:          the URL of the source code
        @type  startingLineNumber: int
        @param startingLineNumber: the line number of the script
        """
        _log()
        
        self._checkAllocated()
        if not script: raise Exception, "script was None"
        
        script_js = _string2jsString(script)
        
        if not sourceURL: 
            sourceURL_js = None
        else:
            sourceURL_js = _string2jsString(sourceURL)

        exception = _JSValueRef(None)
        result = _JSCheckScriptSyntax(self.ctx,
            script_js,
            sourceURL_js,
            startingLineNumber,
            ctypes.byref(exception)
            )
        
        _JSStringRelease(script_js)
        if sourceURL_js: _JSStringRelease(sourceURL_js)
        
        if exception.value: 
            jsObject = JSObject(exception, self.ctx)
            raise JSException, jsObject
            
        return result == 1

    #----------------------------------------------------------------
    def eval(self, 
        script, 
        thisObject=None,
        sourceURL=None, 
        startingLineNumber=1
        ):
        """Execute a script
        
        Executes a script, and returns the result.  For scripts
        which are expressions, this returns the expression value.
        For scripts which contain statements, returns the value of
        executing the final statement.
        
        @rtype:                    JSObject
        @return:                   result of evaluating the script
        @type  script:             str | unicode
        @param script:             the source code for the script to check
        @type  thisObject:         JSObject
        @param thisObject:         the global object when executing the script
        @type  sourceURL:          str | unicode
        @param sourceURL:          the URL of the source code
        @type  startingLineNumber: int
        @param startingLineNumber: the line number of the script
        """
        _log()

        self._checkAllocated()
        if not script: raise Exception, "script was None"
        
        script_js = _string2jsString(script)
        
        if not sourceURL: 
            sourceURL_js = None
        else:
            sourceURL_js = _string2jsString(sourceURL)

        exception = _JSValueRef(None)
        result = _JSEvaluateScript(self.ctx,
            script_js,
            thisObject,
            sourceURL_js,
            startingLineNumber,
            ctypes.byref(exception)
            )
        
        _JSStringRelease(script_js)
        if sourceURL_js: _JSStringRelease(sourceURL_js)
        
        if exception.value: 
            jsObject = JSObject(exception, self.ctx)
            raise JSException, jsObject
            
        return JSObject(result, self.ctx)._toPython()

    #----------------------------------------------------------------
    def getGlobalObject(self):
        """Returns the 'global' object associated with a context
        
        @rtype:   JSObject
        @return:  the global object for this context
        """
        _log()

        self._checkAllocated()
        
        return JSObject(_JSContextGetGlobalObject(self.ctx), self.ctx)
        
    #----------------------------------------------------------------
    def makeConstructorWithCallback(self, callback):
        """Create a new JavaScript constructor
        
        Create a JavaScript constructor implemented with a Python
        function.
        
        @rtype:           JSObject
        @return:          the constructor created
        @type  callback:  function
        @param callback:  the python function to use as the JavaScript constructor
        """
        _log()

        self._checkAllocated()
        
        def callback_py(ctx, function, argCount, args_js, exception):
            args = []
            for i in xrange(0, argCount):
                arg_js = args_js[i]
                arg    = JSObject(arg_js, ctx)._toPython()
                args.append(arg)
            _log("callback(%s,%s,%s,%s,%s)" % (ctx, function, argCount, args, exception))
            jsContext  = JSContext(ctx=ctx)
            jsFunction = JSObject(function, ctx)
            result = callback(jsContext, jsFunction, args)
            _log("callback returns: %s" % result)
            
            return JSObject._fromPython(result, self.ctx)
            
        callback_c = _JSObjectCallAsConstructorCallback(callback_py)
        _log()
        
        result = _JSObjectMakeConstructor(self.ctx, None, callback_c)
        _log()
        
        return JSObject(result, self.ctx)
        
    #----------------------------------------------------------------
    def makeFunctionWithCallback(self, name, callback):
        """Create a new JavaScript function
        
        Create a JavaScript function implemented with a Python
        function.
        
        @rtype:           JSObject
        @return:          the constructor created
        @type  name:      str | unicode 
        @param name:      the name of the function
        @type  callback:  function
        @param callback:  the python function to use as the JavaScript function
        """
        _log()
        
        self._checkAllocated()
        
        def callback_py(ctx, function, thisObject, argCount, args_js, exception):
            args = []
            for i in xrange(0, argCount):
                arg_js = args_js[i]
                arg    = JSObject(arg_js, ctx)._toPython()
                args.append(arg)
            _log("callback(%s,%s,%s,%s,%s,%s)" % (ctx, function, thisObject, argCount, args, exception))
            jsContext  = JSContext(ctx=ctx)
            jsFunction = JSObject(function, ctx)
            jsThis     = JSObject(thisObject, ctx)
            result = callback(jsContext, jsFunction, jsThis, args)
            _log("callback returns: %s" % result)
            
            return JSObject._fromPython(result, self.ctx)
            
        callback_c = _JSObjectCallAsFunctionCallback(callback_py)
        
        name_js = _string2jsString(name)
        
        result = _JSObjectMakeFunctionWithCallback(self.ctx, name_js, callback_c)
        
        _JSStringRelease(name_js)
        
        return JSObject(result, self.ctx)

    #----------------------------------------------------------------
    def _makeBoolean(value):
        """A veneer over JSValueMakeBoolean()"""
        
        self._checkAllocated()
        
        return JSObject(_JSValueMakeBoolean(self.ctx, value))
        
    #----------------------------------------------------------------
    def _makeNull():
        """A veneer over JSValueMakeBoolean()"""
        
        self._checkAllocated()
        
        return JSObject(_JSValueMakeNull(self.ctx))
        
    #----------------------------------------------------------------
    def _makeNumber(value):
        """A veneer over JSValueMakeBoolean()"""
        
        self._checkAllocated()
        
        return JSObject(_JSValueMakeNumber(self.ctx, value))
        
    #----------------------------------------------------------------
    def _makeString(value):
        """A veneer over JSValueMakeBoolean()"""
        
        self._checkAllocated()

        jsString = _string2jsString(value)
        return JSObject(_JSValueMakeString(self.ctx, jsString))
        
    #----------------------------------------------------------------
    def _makeUndefined():
        """A veneer over JSValueMakeBoolean()"""
        
        self._checkAllocated()
        
        return JSObject(_JSValueMakeUndefined(self.ctx))

        
#--------------------------------------------------------------------
class JSObject:
    """Models a JavaScript object
    
    This class is used to represent non-primitive JavaScript
    values such as objects, arrays, and functions.  Primitive
    values including strings, booleans, numbers, null and undefined
    are represented as native Python values.
    
    Most methods of this class take an optional context value
    parameter.  If specified, the operation will occur against that
    context, else it will occur against the context the object was
    created in.
    """

    #--------------------------------------------------------------------
    @staticmethod
    def isJSObject(o):
        """Returns an indication of whether this is a JavaScript object.
        
        Typically used to test a result to see if it's a complex or 
        primitive JavaScript object.
        
        @rtype:    boolean
        @return:   whether the specified object is a JSObject
        @type  o:  any
        @param o:  the object to test to see if it's a JSObject
        """
        return isinstance(o,JSObject)

    #--------------------------------------------------------------------
    @staticmethod
    def _fromPython(pyObject, ctx):
        """Convert to a Python value"""

        if not ctx: raise Exception, "ctx has been released"
       
        if None == pyObject:              return _JSValueMakeNull(ctx)
        if JSUndefined == pyObject:       return _JSValueMakeUndefined(ctx)
        if isinstance(pyObject, bool):    return _JSValueMakeBoolean(ctx, pyObject)
        if isinstance(pyObject, int):     return _JSValueMakeNumber(ctx, pyObject * 1.0)
        if isinstance(pyObject, long):    return _JSValueMakeNumber(ctx, pyObject * 1.0)
        if isinstance(pyObject, float):   return _JSValueMakeNumber(ctx, pyObject)
        if isinstance(pyObject, str):     return _string2jsString(pyObject)
        if JSObject.isJSObject(pyObject): return pyObject.jsRef
        
        raise TypeError("unable to convert object from Python to JavaScript")

    
    #----------------------------------------------------------------
    def __init__(self, jsRef, ctx):
        """Creates a new JSObject.
        
        Intended for internal use only.
        """
        _log("JSObject() - ctx: %s; jsRef: %s" % (str(ctx), str(jsRef)))
        
        self.ctx   = ctx
        self.jsRef = jsRef
        
        _JSValueProtect(ctx, jsRef)
    
    #----------------------------------------------------------------
    def __del__(self):
        """Intended for internal use only."""
        _log("JSObject() - ctx: %s; jsRef: %s" % (str(self.ctx), str(self.jsRef)))
        
        _JSValueUnprotect(self.ctx, self.jsRef)
        
        self.ctx   = None
        self.jsRef = None
    
    #----------------------------------------------------------------
    def __str__(self):
        """Intended for internal use only."""
        
        return "JSObject{ctx=%s, jsRef=%s}" % (str(self.ctx), str(self.jsRef)) 
    
    #----------------------------------------------------------------
    def _checkAllocated(self, ctx):
        """Check to make sure the context is not released."""
        
        if not ctx:        raise Exception, "ctx has been released"
        if not self.jsRef: raise Exception, "jsRef has been released"
    
    #--------------------------------------------------------------------
    def _toPython(self, jsContext=None):
        """Convert to a Python value"""

        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)
        
        if _JSValueIsNull(ctx, self.jsRef):      return None
        if _JSValueIsUndefined(ctx, self.jsRef): return JSUndefined
        if _JSValueIsBoolean(ctx, self.jsRef):   return self.toBoolean(jsContext)
        if _JSValueIsNumber(ctx, self.jsRef):    return self.toNumber(jsContext)
        if _JSValueIsString(ctx, self.jsRef):    return _jsString2string(self.toString())
        
        return self

    #----------------------------------------------------------------
    def isEqual(self, jsObject, jsContext=None):
        """Returns whether the current JSObject is equal to the specified JSObject
        
        @rtype:   boolean
        @return:  whether the specified object is equal to this JSObject
        @type  jsObject:  JSObject
        @param jsObject:  the object to compare against
        """
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)
        
        return 1 == _JSValueIsEqual(ctx, self.jsRef, JSObject._fromPython(jsObject, ctx), None)
        
    #----------------------------------------------------------------
    def isStrictEqual(self, jsObject, jsContext=None):
        """Returns whether the current JSObject is strictly equal to the specified JSObject
        
        @rtype:   boolean
        @return:  whether the specified object is strictly equal to this JSObject
        @type  jsObject:  JSObject
        @param jsObject:  the object to compare against
        """
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)

        return 1 == _JSValueIsStrictEqual(ctx, self.jsRef, JSObject._fromPython(jsObject, ctx))

    #----------------------------------------------------------------
    def isInstanceOf(self, jsConstructor, jsContext=None):
        """Returns whether the current JSObject is an instance of the specified JSObject
        
        @rtype:  boolean
        @return: whether the current JSObject is an instance of the specified JSObject, which should be a constructor
        @type  jsConstructor:  JSObject
        @param jsConstructor:  the constructor to test against
        """
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)

        return 1 == _JSValueIsInstanceOfConstructor(ctx, self.jsRef, JSObject._fromPython(jsConstructor, ctx), None)

    #----------------------------------------------------------------
    def toBoolean(self, jsContext=None):
        """Returns the value of the current JSObject, converted to a boolean
        
        @rtype:  boolean
        @return: the object converted to a boolean value
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)
        
        return _JSValueToBoolean(ctx, self.jsRef)

    #----------------------------------------------------------------
    def toNumber(self, jsContext=None):
        """Returns the value of the current JSObject, converted to a number
        
        @rtype:  float
        @return: the object converted to a number
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)

        exception = _JSValueRef(None)
        
        result = _JSValueToNumber(ctx, self.jsRef, ctypes.byref(exception))

        if exception.value: 
            jsObject = JSObject(exception, self.ctx)
            raise JSException(jsObject)
            
        return result

    #----------------------------------------------------------------
    def toString(self, jsContext=None):
        """Returns the value of the current JSObject, converted to a string
        
        @rtype:  str
        @return: the object converted to a string
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)

        exception = _JSValueRef(None)
        jsString  = _JSValueToStringCopy(ctx, self.jsRef, ctypes.byref(exception))
        
        if exception.value: 
            jsObject = JSObject(exception, self.ctx)
            raise JSException(jsObject)

        return _jsString2string(jsString)
        
    #----------------------------------------------------------------
    def getPropertyNames(self, jsContext=None):
        """Returns the names of the properties of this object
        
        @rtype:  list of str
        @return: the enumerable property names of this object
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)

        jsPropertyNameArray = _JSObjectCopyPropertyNames(ctx, self.jsRef)
        length = _JSPropertyNameArrayGetCount(jsPropertyNameArray)
        result = []
        
        for i in xrange(0,length):
            jsString = _JSPropertyNameArrayGetNameAtIndex(jsPropertyNameArray,i)
            result.append(_jsString2string(jsString))
            
        return result

    #----------------------------------------------------------------
    def deleteProperty(self, propertyName, jsContext=None):
        """Deletes the specified property
        
        @rtype:  boolean
        @return: whether the property could be deleted
        @type  propertyName:  str|unicode
        @param propertyName:  the name of the property to delete
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)

        propertyName_js = _string2jsString(propertyName)
        exception       = _JSValueRef(None)
        result          = _JSObjectDeleteProperty(ctx, self.jsRef, propertyName_js, ctypes.byref(exception))
                
        _JSStringRelease(propertyName_js)
        
        if exception.value: 
            jsObject = JSObject(exception, self.ctx)
            raise JSException(jsObject)
        
        _log("result: %d" % result)
        return result == 1

    #----------------------------------------------------------------
    def getProperty(self, propertyName, jsContext=None):
        """Returns the specified property value
        
        @rtype:  any
        @return: the value of the specified property
        @type  propertyName:  str|unicode
        @param propertyName:  the name of the property to retrieve
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)

        propertyName_js = _string2jsString(propertyName)
        exception       = _JSValueRef(None)
        jsResult        = _JSObjectGetProperty(ctx, self.jsRef, propertyName_js, ctypes.byref(exception))
        
        _JSStringRelease(propertyName_js)
        
        if exception.value: 
            jsObject = JSObject(exception, self.ctx)
            raise JSException(jsObject)
            
        jsObject = JSObject(jsResult, ctx)
        
        return jsObject._toPython(jsContext)

    #----------------------------------------------------------------
    def getPropertyAtIndex(self, propertyIndex, jsContext=None):
        """Returns the specified array element

        @rtype:  any
        @return: the value of the specified array index
        @type  propertyIndex:  int
        @param propertyIndex:  the index of the array element to retrieve
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)

        exception = _JSValueRef(None)
        jsResult  = _JSObjectGetPropertyAtIndex(ctx, self.jsRef, propertyIndex, ctypes.byref(exception))
        
        if exception.value: 
            jsObject = JSObject(exception, self.ctx)
            raise JSException(jsObject)

        jsObject = JSObject(jsResult, ctx)
        return jsObject._toPython(jsContext)
 
    #----------------------------------------------------------------
    def getPrototype(self, jsContext=None):
        """Returns the prototype of this JSObject
        
        @rtype:  any
        @return: the prototype of this JSObject
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)
        
        jsResult = _JSObjectGetPrototype(ctx, self.jsRef)
        jsObject = JSObject(jsResult, ctx)
        return jsObject._toPython(jsContext)

    #----------------------------------------------------------------
    def hasProperty(self, propertyName, jsContext=None):
        """Returns whether this JSObject contains the specified property

        @rtype:  boolean
        @return: whether this JSObject has this property
        @type  propertyName:  str|unicode
        @param propertyName:  the name of the property to delete
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)

        propertyName_js = _string2jsString(propertyName)
        result          = _JSObjectHasProperty(ctx, self.jsRef, propertyName_js)
        
        _JSStringRelease(propertyName_js)
        
        return result == 1

    #----------------------------------------------------------------
    def isConstructor(self, jsContext=None):
        """Returns whether this JSObject is a constructor

        @rtype:  boolean
        @return: whether this JSObject is a constructor
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)
        
        return 1 == _JSObjectIsConstructor(ctx, self.jsRef)

    #----------------------------------------------------------------
    def isFunction(self, jsContext=None):
        """Returns whether this JSObject is a function

        @rtype:  boolean
        @return: whether this JSObject is a function
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)
        
        return 1 == _JSObjectIsFunction(ctx, self.jsRef)

    #----------------------------------------------------------------
    def setProperty(self, propertyName, value, attributes=JSPropertyAttributeNone, jsContext=None):
        """Set the specified property to the specified value
        
        @type  propertyName:  str|unicode
        @param propertyName:  the name of the property to create/set
        @type  value:         any
        @param value:         the value of the property
        @type  attributes:    int
        @param attributes:    attribute values for the property.  Values is a bit ORing of the JSPropertyAttribute* properties of this module.
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)

        propertyName_js = _string2jsString(propertyName)
        exception       = _JSValueRef(None)
        
        value_js = JSObject._fromPython(value, ctx)
            
        _JSObjectSetProperty(ctx, self.jsRef, propertyName_js, value_js, attributes, ctypes.byref(exception))

        _JSStringRelease(propertyName_js)

        if exception.value: 
            jsObject = JSObject(exception, self.ctx)
            raise JSException(jsObject)
        
    #----------------------------------------------------------------
    def setPropertyAtIndex(self, propertyIndex, value, jsContext=None):
        """Set the specified element of this array to the specified value
        
        @type  propertyIndex:  int
        @param propertyIndex:  the array index of the element to set
        @type  value:          any
        @param value:          the value of the array element
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)

        exception       = _JSValueRef(None)
        value_js        = JSObject._fromPython(value, ctx)
        _JSObjectSetPropertyAtIndex(ctx, self.jsRef, propertyIndex, value_js, ctypes.byref(exception))

        if exception.value: 
            jsObject = JSObject(exception, self.ctx)
            raise JSException(jsObject)
        

    #----------------------------------------------------------------
    def setPrototype(self, value, jsContext=None):
        """Set the prototype of this JSObjecto the specified value
        
        @type  value:         any
        @param value:         the new value of the prototype
        """
        _log()
        
        ctx = jsContext.ctx if jsContext else self.ctx
        self._checkAllocated(ctx)
        
        value_js = JSObject._fromPython(value, ctx)
        
        _JSObjectSetPrototype(ctx, self.jsRef, value_js)
        
#--------------------------------------------------------------------
class JSException(Exception):
    """Models a JavaScript exception
    
    When JavaScript exceptions are caught by the API, they are 
    converted Python JSException values, and then raised by the 
    Python code. This class is a subclass of the base Python Exception 
    class.
    
    Exception conditions not related to JavaScript invocation are 
    handled by raising Python Exception values that generally will 
    not need to be caught in well-tested usage of this package.
    
    The C{value} attribute of this object contains the 
    object that was thrown from the JavaScript code. Per 
    JavaScript convention, this may be any object. These 
    objects are converted per the Data Conversion rules. Thus, 
    the C{value} attribute may contain a Python value like a str, 
    or a JSObject value which maps into some JavaScript error 
    value like an Error value.
    """

    #----------------------------------------------------------------
    def __init__(self, value):
        """ """
        self.value = value
        
    #----------------------------------------------------------------
    def __str__(self):
        """ """
        return repr(self.value)
    
#-------------------------------------------------------------------
# simple typedefs
#-------------------------------------------------------------------

_JSClassRef                    = ctypes.c_void_p
_JSContextRef                  = ctypes.c_void_p
_JSGlobalContextRef            = ctypes.c_void_p
_JSObjectRef                   = ctypes.c_void_p
_JSPropertyNameAccumulatorRef  = ctypes.c_void_p
_JSPropertyNameArrayRef        = ctypes.c_void_p
_JSStringRef                   = ctypes.c_void_p
_JSValueRef                    = ctypes.c_void_p
_JSChar                        = ctypes.c_wchar
_JSType                        = ctypes.c_int
_JSClassAttribute              = ctypes.c_int
_JSPropertyAttribute           = ctypes.c_int
_JSClassAttributes             = ctypes.c_uint
_JSPropertyAttributes          = ctypes.c_uint

#-------------------------------------------------------------------
# callback functions
#-------------------------------------------------------------------

#-------------------------------------------------------------------
_JSObjectCallAsConstructorCallback = ctypes.CFUNCTYPE(
    _JSObjectRef,                # result
    _JSContextRef,               # ctx
    _JSObjectRef,                # constructor
    ctypes.c_size_t,             # argumentCount,
    ctypes.POINTER(_JSValueRef), # arguments
    ctypes.POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
_JSObjectCallAsFunctionCallback = ctypes.CFUNCTYPE(
    _JSValueRef,                 # result
    _JSContextRef,               # ctx,
    _JSObjectRef,                # function,
    _JSObjectRef,                # thisObject,
    ctypes.c_size_t,             # argumentCount,
    ctypes.POINTER(_JSValueRef), # arguments
    ctypes.POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
_JSObjectConvertToTypeCallback = ctypes.CFUNCTYPE(
    _JSValueRef,                 # result
    _JSContextRef,               # ctx
    _JSObjectRef,                # object
    _JSType,                     # type
    ctypes.POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
_JSObjectDeletePropertyCallback = ctypes.CFUNCTYPE(
    ctypes.c_int,                # result - bool
    _JSContextRef,               # ctx
    _JSObjectRef,                # object
    _JSStringRef,                # propertyName
    ctypes.POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
_JSObjectFinalizeCallback = ctypes.CFUNCTYPE(
    None,                 # result
    _JSObjectRef,         # object
)

#-------------------------------------------------------------------
_JSObjectGetPropertyCallback = ctypes.CFUNCTYPE(
    _JSValueRef,                 # result
    _JSContextRef,               # ctx
    _JSObjectRef,                # object
    _JSStringRef,                # propertyName
    ctypes.POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
_JSObjectGetPropertyNamesCallback = ctypes.CFUNCTYPE(
    None,                          # result
    _JSContextRef,                 # ctx
    _JSObjectRef,                  # object
    _JSPropertyNameAccumulatorRef, # propertyNames
)

#-------------------------------------------------------------------
_JSObjectHasInstanceCallback = ctypes.CFUNCTYPE(
    ctypes.c_int,                # result - bool
    _JSContextRef,               # ctx
    _JSObjectRef,                # constructor
    _JSValueRef,                 # possibleInstance
    ctypes.POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
_JSObjectHasPropertyCallback = ctypes.CFUNCTYPE(
    ctypes.c_int,         # result - bool
    _JSContextRef,        # ctx
    _JSObjectRef,         # object
    _JSStringRef,         # propertyName
)

#-------------------------------------------------------------------
_JSObjectInitializeCallback = ctypes.CFUNCTYPE(
    None,          # result
    _JSContextRef, # ctx
    _JSObjectRef,  # object
)

#-------------------------------------------------------------------
_JSObjectSetPropertyCallback = ctypes.CFUNCTYPE(
    ctypes.c_int,                # result - bool
    _JSContextRef,               # ctx
    _JSObjectRef,                # object
    _JSStringRef,                # propertyName
    _JSValueRef,                 # value
    ctypes.POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
# structures
#-------------------------------------------------------------------

#-------------------------------------------------------------------
class _JSStaticFunction(ctypes.Structure): pass
_JSStaticFunction._fields_ = [
    ("name",           ctypes.c_char_p), 
    ("callAsFunction", _JSObjectCallAsFunctionCallback),
    ("attributes",     _JSPropertyAttributes),
]

#-------------------------------------------------------------------
class _JSStaticValue(ctypes.Structure): pass
_JSStaticValue._fields_ = [
    ("name",        ctypes.c_char_p), 
    ("getProperty", _JSObjectGetPropertyCallback),
    ("setProperty", _JSObjectSetPropertyCallback),
    ("attributes",  _JSPropertyAttributes),
]

#-------------------------------------------------------------------
class _JSClassDefinition(ctypes.Structure): pass
_JSClassDefinition._fields_ = [
    ("version",           ctypes.c_int),
    ("attributes",        _JSClassAttributes),
    ("className",         ctypes.c_char_p),
    ("parentClass",       _JSClassRef),
    ("staticValues",      ctypes.POINTER(_JSStaticValue)),
    ("staticFunctions",   ctypes.POINTER(_JSStaticFunction)),
    ("initialize",        _JSObjectInitializeCallback),
    ("finalize",          _JSObjectFinalizeCallback),
    ("hasProperty",       _JSObjectHasPropertyCallback),
    ("getProperty",       _JSObjectGetPropertyCallback),
    ("setProperty",       _JSObjectSetPropertyCallback),
    ("deleteProperty",    _JSObjectDeletePropertyCallback),
    ("getPropertyNames",  _JSObjectGetPropertyNamesCallback),
    ("callAsFunction",    _JSObjectCallAsFunctionCallback),
    ("callAsConstructor", _JSObjectCallAsConstructorCallback),
    ("hasInstance",       _JSObjectHasInstanceCallback),
    ("convertToType",     _JSObjectConvertToTypeCallback),
]

#--------------------------------------------------------------------
class JSLibrary:
    """Manages the native JavaScriptCore library
    
    You can set the libraryPath and libraryName class variables
    AFTER importing the module and BEFORE invoking any other
    code in the module.  If the libraryPath variable is set,
    it overrides the libraryName variable.
    """

    libraryName = "JavaScriptCore"
    """Holds the short name of the native JavaScriptCore library
    
    If this variable is set, but the libraryPath variable is not
    set, the library will be searched for in the system via a
    system defined method."""
    
    libraryPath = None
    """Holds the fully qualified name of the JavaScriptCore library
    
    If this library is set, it overrides the libraryName variable
    setting and is used as the complete name of the library.
    """
    
    _library    = None
    
    #----------------------------------------------------------------
    @staticmethod
    def getLibrary():
        """Return the JavaScriptCore library as a CDLL or equivalent
        
        @rtype:  ctypes.CDLL
        @return: the JavaScriptCore library
        """

        if JSLibrary._library: return JSLibrary._library
        
        if not JSLibrary.libraryPath:
            JSLibrary.libraryPath = ctypes.util.find_library(JSLibrary.libraryName)
            
        if not JSLibrary.libraryPath:
            raise Error, "unable to find the JavaScriptCore library"
            
        JSLibrary._library = ctypes.CDLL(JSLibrary.libraryPath)
        return JSLibrary._library

#-------------------------------------------------------------------
def _defineFunction(name, resType, parms):
    """define a function named 'name'
    
    parms should be a sequence of sequences of:
    
    (type, flags, name, defaultValue)
    
    per the ctypes conventions
    """
    
    types      = [ptype      for ptype, pname in parms]
    paramFlags = [(1, pname) for ptype, pname in parms]
    
    library   = JSLibrary.getLibrary()
    prototype = ctypes.CFUNCTYPE(resType, *types)
    function  = prototype((name, library), tuple(paramFlags))
    
    globals()["_" + name] = function

#===================================================================
# _JSBase.h
#===================================================================

#-------------------------------------------------------------------
_defineFunction("JSCheckScriptSyntax", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSStringRef,                     "script"), 
    (_JSStringRef,                     "sourceURL"), 
    (ctypes.c_int32,                   "startingLineNumber"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSEvaluateScript", _JSValueRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSStringRef,                     "script"), 
    (_JSObjectRef,                     "thisObject"),
    (_JSStringRef,                     "sourceURL"),
    (ctypes.c_int,                     "startingLineNumber"),
    (ctypes.POINTER(_JSValueRef),      "exception"),
))

#-------------------------------------------------------------------
_defineFunction("JSGarbageCollect", None, (
    (_JSContextRef,                    "ctx"), 
))

#===================================================================
# _JSContextRef
#===================================================================

#-------------------------------------------------------------------
_defineFunction("JSContextGetGlobalObject", _JSObjectRef, (
    (_JSContextRef,                    "ctx"), 
))

#-------------------------------------------------------------------
_defineFunction("JSGlobalContextCreate", _JSGlobalContextRef, (
    (_JSClassRef,                      "globalObjectClass"), 
))

#-------------------------------------------------------------------
_defineFunction("JSGlobalContextRelease", None, (
    (_JSGlobalContextRef,              "ctx"), 
))

#-------------------------------------------------------------------
_defineFunction("JSGlobalContextRetain", _JSGlobalContextRef, (
    (_JSGlobalContextRef,              "ctx"), 
))

#===================================================================
# _JSObjectRef
#===================================================================

#-------------------------------------------------------------------
_defineFunction("JSClassCreate", _JSClassRef, (
    (ctypes.POINTER(_JSClassDefinition), "definition"), 
))

#-------------------------------------------------------------------
_defineFunction("JSClassRelease", None, (
    (_JSClassRef,                      "jsClass"), 
))

#-------------------------------------------------------------------
_defineFunction("JSClassRetain", None, (
    (_JSClassRef,                      "jsClass"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectCallAsConstructor", _JSObjectRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
    (ctypes.c_size_t,                  "argumentCount"), 
    (ctypes.POINTER(_JSValueRef),      "arguments"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectCallAsFunction", _JSValueRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
    (_JSObjectRef,                     "thisObject"), 
    (ctypes.c_size_t,                  "argumentCount"), 
    (ctypes.POINTER(_JSValueRef),      "arguments"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectCopyPropertyNames", _JSPropertyNameArrayRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectDeleteProperty", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
    (_JSStringRef,                     "propertyName"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectGetPrivate", ctypes.c_void_p, (
    (_JSObjectRef,                     "object"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectGetProperty", _JSValueRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
    (_JSStringRef,                     "propertyName"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectGetPropertyAtIndex", _JSValueRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
    (ctypes.c_uint,                    "propertyIndex"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectGetPrototype", _JSValueRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectHasProperty", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
    (_JSStringRef,                     "propertyName"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectIsConstructor", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectIsFunction", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectMake", _JSObjectRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSClassRef,                      "jsClass"), 
    (ctypes.c_void_p,                  "data"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectMakeConstructor", _JSObjectRef, (
    (_JSContextRef,                      "ctx"), 
    (_JSClassRef,                        "jsClass"), 
    (_JSObjectCallAsConstructorCallback, "callAsConstructor"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectMakeFunction", _JSObjectRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSStringRef,                     "name"), 
    (ctypes.c_uint,                    "parameterCount"), 
    (ctypes.POINTER(_JSStringRef),     "parameterNames"), 
    (_JSStringRef,                     "body"), 
    (_JSStringRef,                     "sourceURL"), 
    (ctypes.c_int,                     "startingLineNumber"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectMakeFunctionWithCallback", _JSObjectRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSStringRef,                     "name"), 
    (_JSObjectCallAsFunctionCallback,  "callAsFunction"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectSetPrivate", ctypes.c_int, (
    (_JSObjectRef,                     "object"), 
    (ctypes.c_void_p,                  "data"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectSetProperty", None, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
    (_JSStringRef,                     "propertyName"), 
    (_JSValueRef,                      "value"), 
    (_JSPropertyAttributes,            "attributes"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectSetPropertyAtIndex", None, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
    (ctypes.c_uint,                    "propertyIndex"), 
    (_JSValueRef,                      "value"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectSetPrototype", None, (
    (_JSContextRef,                    "ctx"), 
    (_JSObjectRef,                     "object"), 
    (_JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSPropertyNameAccumulatorAddName", None, (
    (_JSPropertyNameAccumulatorRef,    "accumulator"), 
    (_JSStringRef,                     "propertyName"), 
))

#-------------------------------------------------------------------
_defineFunction("JSPropertyNameArrayGetCount", ctypes.c_size_t, (
    (_JSPropertyNameArrayRef,          "array"), 
))

#-------------------------------------------------------------------
_defineFunction("JSPropertyNameArrayGetNameAtIndex", _JSStringRef, (
    (_JSPropertyNameArrayRef,          "array"), 
    (ctypes.c_size_t,                  "index"), 
))

#-------------------------------------------------------------------
_defineFunction("JSPropertyNameArrayRelease", None, (
    (_JSPropertyNameArrayRef,          "array"), 
))

#-------------------------------------------------------------------
_defineFunction("JSPropertyNameArrayRetain", _JSPropertyNameArrayRef, (
    (_JSPropertyNameArrayRef,          "array"), 
))

#===================================================================
# _JSStringRef
#===================================================================

#-------------------------------------------------------------------
_defineFunction("JSStringCreateWithCharacters", _JSStringRef, (
    (ctypes.POINTER(_JSChar),          "chars"), 
    (ctypes.c_size_t,                  "numChars"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringCreateWithUTF8CString", _JSStringRef, (
    (ctypes.c_char_p,                  "string"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringGetCharactersPtr", ctypes.POINTER(_JSChar), (
    (_JSStringRef,                     "string"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringGetLength", ctypes.c_int32, (
    (_JSStringRef,                     "string"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringGetMaximumUTF8CStringSize", ctypes.c_size_t, (
    (_JSStringRef,                     "string"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringGetUTF8CString", ctypes.c_size_t, (
    (_JSStringRef,                     "string"), 
    (ctypes.c_char_p,                  "buffer"), 
    (ctypes.c_size_t,                  "bufferSize"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringIsEqual", ctypes.c_int, (
    (_JSStringRef,                     "a"), 
    (_JSStringRef,                     "b"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringIsEqualToUTF8CString", ctypes.c_int, (
    (_JSStringRef,                     "a"), 
    (ctypes.c_char_p,                  "b"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringRelease", None, (
    (_JSStringRef,                     "string"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringRetain", _JSStringRef, (
    (_JSStringRef,                     "string"), 
))

#===================================================================
# _JSValueRef
#===================================================================

#-------------------------------------------------------------------
_defineFunction("JSValueGetType", _JSType, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsBoolean", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsEqual", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "a"), 
    (_JSValueRef,                      "b"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsInstanceOfConstructor", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
    (_JSObjectRef,                     "constructor"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsNull", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsNumber", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsObject", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsObjectOfClass", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
    (_JSClassRef,                      "jsClass"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsStrictEqual", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "a"), 
    (_JSValueRef,                      "b"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsString", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsUndefined", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueMakeBoolean", _JSValueRef, (
    (_JSContextRef,                    "ctx"), 
    (ctypes.c_int,                     "boolean"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueMakeNull", _JSValueRef, (
    (_JSContextRef,                    "ctx"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueMakeNumber", _JSValueRef, (
    (_JSContextRef,                    "ctx"), 
    (ctypes.c_double,                  "number"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueMakeString", _JSValueRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSStringRef,                     "string"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueMakeUndefined", _JSValueRef, (
    (_JSContextRef,                    "ctx"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueProtect", None, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueToBoolean", ctypes.c_int, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueToNumber", ctypes.c_double, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueToObject", _JSObjectRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueToStringCopy", _JSStringRef, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
    (ctypes.POINTER(_JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueUnprotect", None, (
    (_JSContextRef,                    "ctx"), 
    (_JSValueRef,                      "value"), 
))
