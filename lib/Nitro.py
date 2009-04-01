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

__all__ = """
    JSException 
    JSObject 
    JSContext 
    JSLibrary
    JSUndefined
    JSTypeUndefined
    JSTypeNull
    JSTypeBoolean
    JSTypeNumber
    JSTypeString
    JSTypeObject
    JSPropertyAttributeNone
    JSPropertyAttributeReadOnly
    JSPropertyAttributeDontEnum
    JSPropertyAttributeDontDelete
""".split()

# from ctypes import *
# from ctypes.util import find_library

import ctypes
import ctypes.util

#--------------------------------------------------------------------
JSUndefined = object()
"""Used to represent instance of the undefined value in JavaScript"""

#-------------------------------------------------------------------
JSTypeUndefined              = 0
"""Indicates the type of a JavaScript value"""
JSTypeNull                   = 1
"""Indicates the type of a JavaScript value"""
JSTypeBoolean                = 2
"""Indicates the type of a JavaScript value"""
JSTypeNumber                 = 3
"""Indicates the type of a JavaScript value"""
JSTypeString                 = 4
"""Indicates the type of a JavaScript value"""
JSTypeObject                 = 5
"""Indicates the type of a JavaScript value"""

#-------------------------------------------------------------------
JSPropertyAttributeNone       = 0
"""Constant used when setting property values"""
JSPropertyAttributeReadOnly   = 1 << 1
"""Constant used when setting property values"""
JSPropertyAttributeDontEnum   = 1 << 2 
"""Constant used when setting property values"""
JSPropertyAttributeDontDelete = 1 << 3 
"""Constant used when setting property values"""

#-------------------------------------------------------------------
#_JSClassAttributeNone                 = 0
#"""JSClassAttribute"""
#_JSClassAttributeNoAutomaticPrototype = 1 << 1 
#"""JSClassAttribute"""

#--------------------------------------------------------------------
def _string2jsString(string):
    """convert a string to a JSString"""
    if isinstance(string, str):
        return _JSStringCreateWithUTF8CString(string)
    
    elif isinstance(string, unicode):
        return _JSStringCreateWithUTF8CString(string.encode("utf-8"))
        
    else:
        raise TypeError, "expecting a string"

#--------------------------------------------------------------------
def _jsString2string(jsString):
    """convert a JSString to a string - always utf8"""
    len = _JSStringGetMaximumUTF8CStringSize(jsString)
    
    result = ctypes.c_char_p(" " * len)

    _JSStringGetUTF8CString(jsString, result, len)
    
    return result.value

#--------------------------------------------------------------------
class JSContext:
    """Models a Context"""

    #----------------------------------------------------------------
    @staticmethod
    def gc():
        """A veneer over JSGarbageCollect()"""
        _JSGarbageCollect(None)
    
    #----------------------------------------------------------------
    @staticmethod
    def create():
        """A veneer over JSGlobalContextCreate()
        
        Creates a new JSContext which does not need to be
        retain()'d, but does need to be release()'d
        """
        
        ctx = _JSGlobalContextCreate(None)
        return JSContext(ctx)
    
    #----------------------------------------------------------------
    def __init__(self, ctx):
        """Intended for internal use only"""
            
        self.ctx = ctx
        
    #----------------------------------------------------------------
    def _checkNotReleased(self):
        """Check to make sure the context is not released"""
        if self.ctx: return
       
        raise Exception, "JSContext has been released"
    
    #----------------------------------------------------------------
    def retain(self):
        """A veneer over JSGlobalContextRetain()
        
        Returns a new JSContext which should be release()'d
        when you are finished with it.
        """
        self._checkNotReleased()
        
        ctx = _JSGlobalContextRetain(self.ctx)
        return JSContext(ctx)
        
    #----------------------------------------------------------------
    def release(self):
        """A veneer over JSGlobalContextRelease()"""
        self._checkNotReleased()
        
        _JSGlobalContextRelease(self.ctx)
        self.ctx = None

    #----------------------------------------------------------------
    def checkScriptSyntax(self, 
        script, 
        sourceURL=None, 
        startingLineNumber=1
        ):
        """A veneer over JSCheckScriptSyntax()"""
        
        self._checkNotReleased()
        if not script: raise Exception, "script was None"
        
        script = _string2jsString(script)
        if sourceURL: sourceURL = _string2jsString(sourceURL)

        exception = _JSValueRef(None)
        result = _JSCheckScriptSyntax(self.ctx,
            script,
            sourceURL,
            startingLineNumber,
            ctypes.byref(exception)
            )
        
        if exception.value: 
            jsObject = JSObject._fromJSValueRef(exception)
            string = jsObject.toString(self)
            
            raise JSException(string)
            
        return result

    #----------------------------------------------------------------
    def evaluateScript(self, 
        script, 
        thisObject,
        sourceURL=None, 
        startingLineNumber=1
        ):
        """A veneer over JSEvaluateScript()"""
        
        pass

    #----------------------------------------------------------------
    def getGlobalObject():
        """A veneer over JSContextGetGlobalObject()"""
        
        pass
        
    #----------------------------------------------------------------
    def makeConstructorWithCallback(name, callback):
        """A veneer over JSObjectMakeConstructor()"""
        
        pass
        
    #----------------------------------------------------------------
    def makeFunctionWithCallback(name, callback):
        """A veneer over JSObjectMakeFunctionWithCallback()"""
        
        pass
        
#--------------------------------------------------------------------
class JSObject:
    """Models a JavaScript object """
    
    #----------------------------------------------------------------
    @staticmethod
    def _fromJSValueRef(jsValueRef):
        """ """
        result = JSObject()
        result.value = jsValueRef
        return result
    
    #----------------------------------------------------------------
    def __init__(self):
        """ """
        pass
    
    #----------------------------------------------------------------
    def getType(self, jsContext):
        """A veneer over JSValueGetType()"""
        
        pass

    #----------------------------------------------------------------
    def isBoolean(self, jsContext):
        """A veneer over JSValueIsBoolean()"""
        
        pass
        
    #----------------------------------------------------------------
    def isNull(self, jsContext):
        """A veneer over JSValueIsNull()"""
        
        pass
        
    #----------------------------------------------------------------
    def isNumber(self, jsContext):
        """A veneer over JSValueIsNumber()"""
        
        pass
        
    #----------------------------------------------------------------
    def isObject(self, jsContext):
        """A veneer over JSValueIsObject()"""
        
        pass
        
    #----------------------------------------------------------------
    def isString(self, jsContext):
        """A veneer over JSValueIsString()"""
        
        pass
        
    #----------------------------------------------------------------
    def isUndefined(self, jsContext):
        """A veneer over JSValueIsUndefined()"""
        
        pass
        
    #----------------------------------------------------------------
    def isEqual(self, jsContext, object):
        """A veneer over JSValueIsEqual()"""
        
        pass
        
    #----------------------------------------------------------------
    def isStrictEqual(self, jsContext, object):
        """A veneer over JSValueisStrictEqual()"""
        
        pass
        
    #----------------------------------------------------------------
    def isInstanceOf(self, jsContext, constructor):
        """A veneer over JSValueIsInstanceOfConstructor()"""
        
        pass
        
    #----------------------------------------------------------------
    def protect(self, jsContext):
        """A veneer over JSVakueProtect()"""
        
        pass
        
    #----------------------------------------------------------------
    def unprotect(self, jsContext):
        """A veneer over JSValueUnprotect()"""
        
        pass
        
    #----------------------------------------------------------------
    def toString(self, jsContext):
        """A veneer over JSValueToStringCopy()"""
        
        jsString = _JSValueToStringCopy(jsContext.ctx, self.value, None)
        return _jsString2string(jsString)
        
    #----------------------------------------------------------------
    def callAsConstructor(self, jsContext, arguments):
        """A veneer over JSObjectCallAsConstructor()"""
        
        pass

    #----------------------------------------------------------------
    def callAsFunction(self, jsContext, thisObject, arguments):
        """A veneer over JSObjectCallAsFunction()"""
        
        pass
        
    #----------------------------------------------------------------
    def getPropertyNames(self, jsContext):
        """A veneer over JSObjectCopyPropertyNames()"""
        
        pass

    #----------------------------------------------------------------
    def deleteProperty(jself, sContext, propertyName):
        """A veneer over JSObjectDeleteProperty()"""
        
        pass

    #----------------------------------------------------------------
    def getProperty(self, jsContext, propertyName):
        """A veneer over JSObjectGetProperty()"""
        
        pass

    #----------------------------------------------------------------
    def getPropertyAtIndex(self, jsContext, propertyIndex):
        """A veneer over JSGetPropertyAtIndex()"""
        
        pass

    #----------------------------------------------------------------
    def getPrototype(self, jsContext):
        """A veneer over JSObjectGetPrototype()"""
        
        pass

    #----------------------------------------------------------------
    def hasProperty(self, jsContext, propertyName):
        """A veneer over JSObjectHasProperty()"""
        
        pass

    #----------------------------------------------------------------
    def isConstructor(self, jsContext):
        """A veneer over JSObjectIsConstructor()"""
        
        pass

    #----------------------------------------------------------------
    def isFunction(self, jsContext):
        """A veneer over JSObjectIsFunction()"""
        
        pass

    #----------------------------------------------------------------
    def setProperty(self, jsContext, propertyName, value, attributes):
        """A veneer over JSObjectSetProperty()"""
        
        pass

    #----------------------------------------------------------------
    def setPropertyAtIndex(self, jsContext, propertyIndex, value):
        """A veneer over JSObjectSetPropertyAtIndex()"""
        
        pass

    #----------------------------------------------------------------
    def setPrototype(self, jsContext, value):
        """A veneer over JSObjectSetPrototype()"""
        
        pass
        
#--------------------------------------------------------------------
class JSFunction(JSObject):
    """Models a JavaScript function"""
    
    pass

#--------------------------------------------------------------------
class JSArray(JSObject):
    """Models a JavaScript array"""
    
    pass

#--------------------------------------------------------------------
class JSException(Exception):
    """Models a JavaScript exception
    
    When JavaScript exceptions are caught by the API, they are 
    converted Python JSException values, and then raised by the 
    Python code. This class is a subclass of the JSObject class, 
    as well as the base Python Exception class.
    
    Exception conditions not related to JavaScript invocation are 
    handled by raising Python Exception values that generally will 
    not need to be caught in well-tested usage of this package.
    
    This class is a subclass of the JSObject class as well as the 
    base Python Exception class. The args attribute contains the 
    object that was thrown from the JavaScript code. Per 
    JavaScript convention, this may be any object. These 
    objects are converted per the Data Conversion rules. Thus, 
    the args attribute may contain a Python value like a str, 
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
    """Holds the fully qualified name of the JavaScriptCore library"""
    
    _library    = None
    
    #----------------------------------------------------------------
    @staticmethod
    def getLibrary():
        """Return the JavaScriptCore library as a CDLL or equivalent"""

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
_defineFunction("JSValueMakeUndefined", None, (
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
