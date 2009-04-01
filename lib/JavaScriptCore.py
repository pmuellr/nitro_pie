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
from ctypes.util import find_library

#--------------------------------------------------------------------
def string2jsString(string):
    """convert a string to a JSString"""
    if isinstance(string, str):
        return _JSC.JSStringCreateWithUTF8CString(string)
    
    elif isinstance(string, unicode):
        return _JSC.JSStringCreateWithUTF8CString(string.encode("utf-8"))
        
    else:
        raise TypeError, "expecting a string"

#--------------------------------------------------------------------
def jsString2string(jsString):
    """convert a JSString to a string - always utf8"""
    len = _JSC.JSStringGetMaximumUTF8CStringSize(jsString)
    
    result = c_char_p(" " * len)

    _JSC.JSStringGetUTF8CString(jsString, result, len)
    
    return result.value

#--------------------------------------------------------------------
class JSException(Exception):
    """ """

    #----------------------------------------------------------------
    def __init__(self, value):
        """ """
        self.value = value
        
    #----------------------------------------------------------------
    def __str__(self, value):
        """ """
        return repr(self.value)
    
#--------------------------------------------------------------------
class JSObject:
    """ """
    
    #----------------------------------------------------------------
    @staticmethod
    def fromJSValueRef(jsValueRef):
        """ """
        result = JSObject()
        result.value = jsValueRef
        return result
    
    #----------------------------------------------------------------
    def __init__(self):
        """ """
        pass
    
    #----------------------------------------------------------------
    def toString(self, jsContext):
        """ """
        print "JSC.JSValueToStringCopy(%s, %s, None)" % (jsContext, self.value)
        jsString = _JSC.JSValueToStringCopy(jsContext.ctx, self.value, None)
        return jsString2string(jsString)
    
    
        
#--------------------------------------------------------------------
class JSContext:
    """models a Context"""

    #----------------------------------------------------------------
    @staticmethod
    def gc():
        """Run a garbage collect"""
        _JSC.JSGarbageCollect(None)
    
    #----------------------------------------------------------------
    def __init__(self, ctx=None):
        """create a new context"""
        if None == ctx:
            ctx = _JSC.JSGlobalContextCreate(None)
            
        self.ctx = ctx
        
    #----------------------------------------------------------------
    def checkNotReleased(self):
        """check to make sure not released"""
        if self.ctx: return
       
        raise Exception, "JSContext has been released"
    
    #----------------------------------------------------------------
    def retain(self):
        """retain a context, returning a new one"""
        self.checkNotReleased()
        
        ctx = _JSC.JSGlobalContextRetain(self.ctx)
        return JSContext(ctx=ctx)
        
    #----------------------------------------------------------------
    def release(self):
        """release a context"""
        self.checkNotReleased()
        
        _JSC.JSGlobalContextRelease(self.ctx)
        self.ctx = None

    #----------------------------------------------------------------
    def checkScriptSyntax(self, 
        script, 
        sourceURL=None, 
        startingLineNumber=1
        ):
        """check a script's syntax"""
        
        self.checkNotReleased()
        if not script: raise Exception, "script was None"
        
        script = string2jsString(script)
        if sourceURL: sourceURL = string2jsString(sourceURL)

        exception = _JSValueRef(None)
        print "JSCheckScriptSyntax(%s, %s, %s, %d, %s)" % (str(self), jsString2string(script), str(sourceURL), startingLineNumber, str(exception))
        result = _JSC.JSCheckScriptSyntax(self.ctx,
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


#-------------------------------------------------------------------
# constants
#-------------------------------------------------------------------

_PARM_IN   = 1
_PARM_OUT  = 2
_PARM_ZERO = 4

#-------------------------------------------------------------------
# enums
#-------------------------------------------------------------------

#-------------------------------------------------------------------
_JSTypeUndefined              = 0
"""JSType"""
_JSTypeNull                   = 1
"""JSType"""
_JSTypeBoolean                = 2
"""JSType"""
_JSTypeNumber                 = 3
"""JSType"""
_JSTypeString                 = 4
"""JSType"""
_JSTypeObject                 = 5
"""JSType"""

#-------------------------------------------------------------------
_JSClassAttributeNone                 = 0
"""JSClassAttribute"""
_JSClassAttributeNoAutomaticPrototype = 1 << 1 
"""JSClassAttribute"""

#-------------------------------------------------------------------
_JSPropertyAttributeNone       = 0
"""JSPropertyAttribute"""
_JSPropertyAttributeReadOnly   = 1 << 1
"""JSPropertyAttribute"""
_JSPropertyAttributeDontEnum   = 1 << 2 
"""JSPropertyAttribute"""
_JSPropertyAttributeDontDelete = 1 << 3 
"""JSPropertyAttribute"""

#-------------------------------------------------------------------
# simple typedefs
#-------------------------------------------------------------------

_JSClassRef                    = c_void_p
_JSContextRef                  = c_void_p
_JSGlobalContextRef            = c_void_p
_JSObjectRef                   = c_void_p
_JSPropertyNameAccumulatorRef  = c_void_p
_JSPropertyNameArrayRef        = c_void_p
_JSStringRef                   = c_void_p
_JSValueRef                    = c_void_p
_JSChar                        = c_wchar
_JSType                        = c_int
_JSClassAttribute              = c_int
_JSPropertyAttribute           = c_int
_JSClassAttributes             = c_uint
_JSPropertyAttributes          = c_uint

#-------------------------------------------------------------------
# callback functions
#-------------------------------------------------------------------

#-------------------------------------------------------------------
_JSObjectCallAsConstructorCallback = CFUNCTYPE(
    _JSObjectRef,         # result
    _JSContextRef,        # ctx
    _JSObjectRef,         # constructor
    c_size_t,             # argumentCount,
    POINTER(_JSValueRef), # arguments
    POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
_JSObjectCallAsFunctionCallback = CFUNCTYPE(
    _JSValueRef,          # result
    _JSContextRef,        # ctx,
    _JSObjectRef,         # function,
    _JSObjectRef,         # thisObject,
    c_size_t,             # argumentCount,
    POINTER(_JSValueRef), # arguments
    POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
_JSObjectConvertToTypeCallback = CFUNCTYPE(
    _JSValueRef,          # result
    _JSContextRef,        # ctx
    _JSObjectRef,         # object
    _JSType,              # type
    POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
_JSObjectDeletePropertyCallback = CFUNCTYPE(
    c_int,                # result - bool
    _JSContextRef,        # ctx
    _JSObjectRef,         # object
    _JSStringRef,         # propertyName
    POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
_JSObjectFinalizeCallback = CFUNCTYPE(
    None,                 # result
    _JSObjectRef,         # object
)

#-------------------------------------------------------------------
_JSObjectGetPropertyCallback = CFUNCTYPE(
    _JSValueRef,          # result
    _JSContextRef,        # ctx
    _JSObjectRef,         # object
    _JSStringRef,         # propertyName
    POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
_JSObjectGetPropertyNamesCallback = CFUNCTYPE(
    None,                          # result
    _JSContextRef,                 # ctx
    _JSObjectRef,                  # object
    _JSPropertyNameAccumulatorRef, # propertyNames
)

#-------------------------------------------------------------------
_JSObjectHasInstanceCallback = CFUNCTYPE(
    c_int,                # result - bool
    _JSContextRef,        # ctx
    _JSObjectRef,         # constructor
    _JSValueRef,          # possibleInstance
    POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
_JSObjectHasPropertyCallback = CFUNCTYPE(
    c_int,         # result - bool
    _JSContextRef, # ctx
    _JSObjectRef,  # object
    _JSStringRef,  # propertyName
)

#-------------------------------------------------------------------
_JSObjectInitializeCallback = CFUNCTYPE(
    None,          # result
    _JSContextRef, # ctx
    _JSObjectRef,  # object
)

#-------------------------------------------------------------------
_JSObjectSetPropertyCallback = CFUNCTYPE(
    c_int,                # result - bool
    _JSContextRef,        # ctx
    _JSObjectRef,         # object
    _JSStringRef,         # propertyName
    _JSValueRef,          # value
    POINTER(_JSValueRef), # exception
)

#-------------------------------------------------------------------
# structures
#-------------------------------------------------------------------

#-------------------------------------------------------------------
class _JSStaticFunction(Structure): pass
_JSStaticFunction._fields_ = [
    ("name",           c_char_p), 
    ("callAsFunction", _JSObjectCallAsFunctionCallback),
    ("attributes",     _JSPropertyAttributes),
]

#-------------------------------------------------------------------
class _JSStaticValue(Structure): pass
_JSStaticValue._fields_ = [
    ("name",        c_char_p), 
    ("getProperty", _JSObjectGetPropertyCallback),
    ("setProperty", _JSObjectSetPropertyCallback),
    ("attributes",  _JSPropertyAttributes),
]

#-------------------------------------------------------------------
class _JSClassDefinition(Structure): pass
_JSClassDefinition._fields_ = [
    ("version",           c_int),
    ("attributes",        _JSClassAttributes),
    ("className",         c_char_p),
    ("parentClass",       _JSClassRef),
    ("staticValues",      POINTER(_JSStaticValue)),
    ("staticFunctions",   POINTER(_JSStaticFunction)),
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

#-------------------------------------------------------------------
def _defineStaticMethod(name, resType, parms):
    """define a function named 'name'
    
    parms should be a sequence of sequences of:
       (type, flags, name, defaultValue)
    per the ctypes conventions
    """
    
    types      = [ptype                     for ptype, pflags, pname, pdefault in parms]
    paramFlags = [(pflags, pname, pdefault) for ptype, pflags, pname, pdefault in parms]
    
    prototype = CFUNCTYPE(resType, *types)
    function  = prototype((name, _JSC.lib), tuple(paramFlags))
    
    setattr(_JSC, name, staticmethod(function))

#-------------------------------------------------------------------
class _JSC:
    """native function container"""
    
    libName = find_library("JavaScriptCore")
    if not libName: raise Error, "unable to find the JavaScriptCore library"
    
    lib = CDLL(libName)
    if not lib: raise Error, "unable to load the JavaScriptCore library"

#===================================================================
# _JSBase.h
#===================================================================

#-------------------------------------------------------------------
_defineStaticMethod("JSCheckScriptSyntax", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSStringRef,         _PARM_IN,            "script",             None),
    (_JSStringRef,         _PARM_IN,            "sourceURL",          None),
    (c_int32,              _PARM_IN,            "startingLineNumber", 1),
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None),
))

#-------------------------------------------------------------------
_defineStaticMethod("JSEvaluateScript", _JSValueRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSStringRef,         _PARM_IN,            "script",             None),
    (_JSObjectRef,         _PARM_IN,            "thisObject",         None),
    (_JSStringRef,         _PARM_IN,            "sourceURL",          None),
    (c_int,                _PARM_IN,            "startingLineNumber", 1),
    (POINTER(_JSValueRef), _PARM_IN | _PARM_OUT, "exception",          None),
))

#-------------------------------------------------------------------
_defineStaticMethod("JSGarbageCollect", None, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
))

#===================================================================
# _JSContextRef
#===================================================================

#-------------------------------------------------------------------
_defineStaticMethod("JSContextGetGlobalObject", _JSObjectRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSGlobalContextCreate", _JSGlobalContextRef, (
    (_JSClassRef,          _PARM_IN,            "globalObjectClass",  None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSGlobalContextRelease", None, (
    (_JSGlobalContextRef,  _PARM_IN,            "ctx",                None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSGlobalContextRetain", _JSGlobalContextRef, (
    (_JSGlobalContextRef,  _PARM_IN,            "ctx",                None), 
))

#===================================================================
# _JSObjectRef
#===================================================================

#-------------------------------------------------------------------
_defineStaticMethod("JSClassCreate", _JSClassRef, (
    (POINTER(_JSClassDefinition), _PARM_IN,     "definition",         None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSClassRelease", None, (
    (_JSClassRef,          _PARM_IN,            "jsClass",            None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSClassRetain", None, (
    (_JSClassRef,          _PARM_IN,            "jsClass",            None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectCallAsConstructor", _JSObjectRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
    (c_size_t,             _PARM_IN,            "argumentCount",      0), 
    (POINTER(_JSValueRef), _PARM_IN,            "arguments",          None), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectCallAsFunction", _JSValueRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
    (_JSObjectRef,         _PARM_IN,            "thisObject",         None), 
    (c_size_t,             _PARM_IN,            "argumentCount",      0), 
    (POINTER(_JSValueRef), _PARM_IN,            "arguments",          None), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectCopyPropertyNames", _JSPropertyNameArrayRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectDeleteProperty", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",              None), 
    (_JSObjectRef,         _PARM_IN,            "object",           None), 
    (_JSStringRef,         _PARM_IN,            "propertyName",     None), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",        None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectGetPrivate", c_void_p, (
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectGetProperty", _JSValueRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
    (_JSStringRef,         _PARM_IN,            "propertyName",       None), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectGetPropertyAtIndex", _JSValueRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
    (c_uint,               _PARM_IN,            "propertyIndex",      None), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectGetPrototype", _JSValueRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectHasProperty", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
    (_JSStringRef,         _PARM_IN,            "propertyName",       None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectIsConstructor", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectIsFunction", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectMake", _JSObjectRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSClassRef,          _PARM_IN,            "jsClass",            None), 
    (c_void_p,             _PARM_IN,            "data",               None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectMakeConstructor", _JSObjectRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSClassRef,          _PARM_IN,            "jsClass",            None), 
    (_JSObjectCallAsConstructorCallback, _PARM_IN, "callAsConstructor",   None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectMakeFunction", _JSObjectRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSStringRef,         _PARM_IN,            "name",               None), 
    (c_uint,               _PARM_IN,            "parameterCount",     None), 
    (POINTER(_JSStringRef),_PARM_IN,            "parameterNames",     None), 
    (_JSStringRef,         _PARM_IN,            "body",               None), 
    (_JSStringRef,         _PARM_IN,            "sourceURL",          None), 
    (c_int,                _PARM_IN,            "startingLineNumber", 1), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectMakeFunctionWithCallback", _JSObjectRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSStringRef,         _PARM_IN,            "name",               None), 
    (_JSObjectCallAsFunctionCallback, _PARM_IN, "callAsFunction",     None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectSetPrivate", c_int, (
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
    (c_void_p,             _PARM_IN,            "data",               None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectSetProperty", None, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
    (_JSStringRef,         _PARM_IN,            "propertyName",       None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
    (_JSPropertyAttributes,_PARM_IN,            "attributes",         0), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectSetPropertyAtIndex", None, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
    (c_uint,               _PARM_IN,            "propertyIndex",      0), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSObjectSetPrototype", None, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSObjectRef,         _PARM_IN,            "object",             None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSPropertyNameAccumulatorAddName", None, (
    (_JSPropertyNameAccumulatorRef, _PARM_IN,   "accumulator",        None), 
    (_JSStringRef,         _PARM_IN,            "propertyName",       None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSPropertyNameArrayGetCount", c_size_t, (
    (_JSPropertyNameArrayRef, _PARM_IN,         "array",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSPropertyNameArrayGetNameAtIndex", _JSStringRef, (
    (_JSPropertyNameArrayRef, _PARM_IN,         "array",              None), 
    (c_size_t,            _PARM_IN,            "index",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSPropertyNameArrayRelease", None, (
    (_JSPropertyNameArrayRef, _PARM_IN,         "array",                None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSPropertyNameArrayRetain", _JSPropertyNameArrayRef, (
    (_JSPropertyNameArrayRef, _PARM_IN,         "array",                None), 
))

#===================================================================
# _JSStringRef
#===================================================================

#-------------------------------------------------------------------
_defineStaticMethod("JSStringCreateWithCharacters", _JSStringRef, (
    (POINTER(_JSChar),     _PARM_IN,            "chars",               None), 
    (c_size_t,             _PARM_IN,            "numChars",            0), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSStringCreateWithUTF8CString", _JSStringRef, (
    (c_char_p,             _PARM_IN,            "string",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSStringGetCharactersPtr", POINTER(_JSChar), (
    (_JSStringRef,         _PARM_IN,            "string",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSStringGetLength", c_int32, (
    (_JSStringRef,         _PARM_IN,            "string",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSStringGetMaximumUTF8CStringSize", c_size_t, (
    (_JSStringRef,         _PARM_IN,            "string",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSStringGetUTF8CString", c_size_t, (
    (_JSStringRef,         _PARM_IN,            "string",              None), 
    (c_char_p,             _PARM_IN,            "buffer",              None), 
    (c_size_t,             _PARM_IN,            "bufferSize",          0), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSStringIsEqual", c_int, (
    (_JSStringRef,         _PARM_IN,            "a",                   None), 
    (_JSStringRef,         _PARM_IN,            "b",                   None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSStringIsEqualToUTF8CString", c_int, (
    (_JSStringRef,         _PARM_IN,            "a",                   None), 
    (c_char_p,             _PARM_IN,            "b",                   None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSStringRelease", None, (
    (_JSStringRef,         _PARM_IN,            "string",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSStringRetain", _JSStringRef, (
    (_JSStringRef,         _PARM_IN,            "string",              None), 
))

#===================================================================
# _JSValueRef
#===================================================================

#-------------------------------------------------------------------
_defineStaticMethod("JSValueGetType", _JSType, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueIsBoolean", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueIsEqual", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "a",                  None), 
    (_JSValueRef,          _PARM_IN,            "b",                  None), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueIsInstanceOfConstructor", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
    (_JSObjectRef,         _PARM_IN,            "constructor",        None), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueIsNull", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueIsNumber", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueIsObject", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueIsObjectOfClass", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
    (_JSClassRef,          _PARM_IN,            "jsClass",            None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueIsStrictEqual", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "a",                  None), 
    (_JSValueRef,          _PARM_IN,            "b",                  None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueIsString", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueIsUndefined", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueMakeBoolean", _JSValueRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (c_int,                _PARM_IN,            "boolean",            0), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueMakeNull", _JSValueRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueMakeNumber", _JSValueRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (c_double,             _PARM_IN,            "number",             None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueMakeString", _JSValueRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSStringRef,         _PARM_IN,            "string",             None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueMakeUndefined", None, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueProtect", None, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueToBoolean", c_int, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueToNumber", c_double, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueToObject", _JSObjectRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueToStringCopy", _JSStringRef, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
    (POINTER(_JSValueRef), _PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
_defineStaticMethod("JSValueUnprotect", None, (
    (_JSContextRef,        _PARM_IN,            "ctx",                None), 
    (_JSValueRef,          _PARM_IN,            "value",              None), 
))
