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

import sys
from ctypes import *
import ctypes.util

#-------------------------------------------------------------------
# load the library
#-------------------------------------------------------------------

JSC = ctypes.util.find_library("JavaScriptCore")

if not JSC: raise Error, "unable to find the JavaScriptCore library"

JSC = CDLL(JSC)

if not JSC: raise Error, "unable to load the JavaScriptCore library"

PARM_IN   = 1
PARM_OUT  = 2
PARM_ZERO = 4

#-------------------------------------------------------------------
# define a function named 'name'
# parms should be a sequence of sequences of:
#    ( type, flags, name, defaultValue)
# per the ctypes conventions
#-------------------------------------------------------------------
def defineFunction(name, resType, parms):
    types      = [ptype                     for ptype, pflags, pname, pdefault in parms]
    paramFlags = [(pflags, pname, pdefault) for ptype, pflags, pname, pdefault in parms]
    
    prototype = CFUNCTYPE(resType, *types)
    function  = prototype((name, JSC), tuple(paramFlags))
    
    return function

#-------------------------------------------------------------------
# enums
#-------------------------------------------------------------------

#-------------------------------------------------------------------
# JSType
kJSTypeUndefined              = 0
kJSTypeNull                   = 1
kJSTypeBoolean                = 2
kJSTypeNumber                 = 3
kJSTypeString                 = 4
kJSTypeObject                 = 5

#-------------------------------------------------------------------
# JSClassAttribute
kJSClassAttributeNone                 = 0
kJSClassAttributeNoAutomaticPrototype = 1 << 1 

#-------------------------------------------------------------------
# JSPropertyAttribute
kJSPropertyAttributeNone       = 0
kJSPropertyAttributeReadOnly   = 1 << 1
kJSPropertyAttributeDontEnum   = 1 << 2 
kJSPropertyAttributeDontDelete = 1 << 3 

#-------------------------------------------------------------------
# simple typedefs
#-------------------------------------------------------------------

JSClassRef                    = c_void_p
JSContextRef                  = c_void_p
JSGlobalContextRef            = c_void_p
JSObjectRef                   = c_void_p
JSPropertyNameAccumulatorRef  = c_void_p
JSPropertyNameArrayRef        = c_void_p
JSStringRef                   = c_void_p
JSValueRef                    = c_void_p
JSChar                        = c_wchar
JSType                        = c_int
JSClassAttribute              = c_int
JSPropertyAttribute           = c_int
JSClassAttributes             = c_uint
JSPropertyAttributes          = c_uint

#-------------------------------------------------------------------
# callback functions
#-------------------------------------------------------------------

#-------------------------------------------------------------------
JSObjectCallAsConstructorCallback = CFUNCTYPE(
    JSObjectRef,         # result
    JSContextRef,        # ctx
    JSObjectRef,         # constructor
    c_size_t,            # argumentCount,
    POINTER(JSValueRef), # arguments
    POINTER(JSValueRef), # exception
)

#-------------------------------------------------------------------
JSObjectCallAsFunctionCallback = CFUNCTYPE(
    JSValueRef,          # result
    JSContextRef,        # ctx,
    JSObjectRef,         # function,
    JSObjectRef,         # thisObject,
    c_size_t,            # argumentCount,
    POINTER(JSValueRef), # arguments
    POINTER(JSValueRef), # exception
)

#-------------------------------------------------------------------
JSObjectConvertToTypeCallback = CFUNCTYPE(
    JSValueRef,          # result
    JSContextRef,        # ctx
    JSObjectRef,         # object
    JSType,              # type
    POINTER(JSValueRef), # exception
)

#-------------------------------------------------------------------
JSObjectDeletePropertyCallback = CFUNCTYPE(
    c_int,               # result - bool
    JSContextRef,        # ctx
    JSObjectRef,         # object
    JSStringRef,         # propertyName
    POINTER(JSValueRef), # exception
)

#-------------------------------------------------------------------
JSObjectFinalizeCallback = CFUNCTYPE(
    None,                # result
    JSObjectRef,         # object
)

#-------------------------------------------------------------------
JSObjectGetPropertyCallback = CFUNCTYPE(
    JSValueRef,          # result
    JSContextRef,        # ctx
    JSObjectRef,         # object
    JSStringRef,         # propertyName
    POINTER(JSValueRef), # exception
)

#-------------------------------------------------------------------
JSObjectGetPropertyNamesCallback = CFUNCTYPE(
    None,                         # result
    JSContextRef,                 # ctx
    JSObjectRef,                  # object
    JSPropertyNameAccumulatorRef, # propertyNames
)

#-------------------------------------------------------------------
JSObjectHasInstanceCallback = CFUNCTYPE(
    c_int,               # result - bool
    JSContextRef,        # ctx
    JSObjectRef,         # constructor
    JSValueRef,          # possibleInstance
    POINTER(JSValueRef), # exception
)

#-------------------------------------------------------------------
JSObjectHasPropertyCallback = CFUNCTYPE(
    c_int,        # result - bool
    JSContextRef, # ctx
    JSObjectRef,  # object
    JSStringRef,  # propertyName
)

#-------------------------------------------------------------------
JSObjectInitializeCallback = CFUNCTYPE(
    None,         # result
    JSContextRef, # ctx
    JSObjectRef,  # object
)

#-------------------------------------------------------------------
JSObjectSetPropertyCallback = CFUNCTYPE(
    c_int,               # result - bool
    JSContextRef,        # ctx
    JSObjectRef,         # object
    JSStringRef,         # propertyName
    JSValueRef,          # value
    POINTER(JSValueRef), # exception
)

#-------------------------------------------------------------------
# structures
#-------------------------------------------------------------------

#-------------------------------------------------------------------
class JSStaticFunction(ctypes.Structure): pass
JSStaticFunction._fields_ = [
    ("name",           c_char_p), 
    ("callAsFunction", JSObjectCallAsFunctionCallback),
    ("attributes",     JSPropertyAttributes),
]

#-------------------------------------------------------------------
class JSStaticValue(ctypes.Structure): pass
JSStaticValue._fields_ = [
    ("name",        c_char_p), 
    ("getProperty", JSObjectGetPropertyCallback),
    ("setProperty", JSObjectSetPropertyCallback),
    ("attributes",  JSPropertyAttributes),
]

#-------------------------------------------------------------------
class JSClassDefinition(ctypes.Structure): pass
JSClassDefinition._fields_ = [
    ("version",           c_int),
    ("attributes",        JSClassAttributes),
    ("className",         c_char_p),
    ("parentClass",       JSClassRef),
    ("staticValues",      POINTER(JSStaticValue)),
    ("staticFunctions",   POINTER(JSStaticFunction)),
    ("initialize",        JSObjectInitializeCallback),
    ("finalize",          JSObjectFinalizeCallback),
    ("hasProperty",       JSObjectHasPropertyCallback),
    ("getProperty",       JSObjectGetPropertyCallback),
    ("setProperty",       JSObjectSetPropertyCallback),
    ("deleteProperty",    JSObjectDeletePropertyCallback),
    ("getPropertyNames",  JSObjectGetPropertyNamesCallback),
    ("callAsFunction",    JSObjectCallAsFunctionCallback),
    ("callAsConstructor", JSObjectCallAsConstructorCallback),
    ("hasInstance",       JSObjectHasInstanceCallback),
    ("convertToType",     JSObjectConvertToTypeCallback),
]

#===================================================================
# JSBase.h
#===================================================================

#-------------------------------------------------------------------
JSCheckScriptSyntax = defineFunction("JSCheckScriptSyntax", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSStringRef,         PARM_IN,            "script",             None),
    (JSStringRef,         PARM_IN,            "sourceURL",          None),
    (c_int32,             PARM_IN,            "startingLineNumber", 1),
    (POINTER(JSValueRef), PARM_IN,            "exception",          None),
))

#-------------------------------------------------------------------
JSEvaluateScript = defineFunction("JSEvaluateScript", JSValueRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSStringRef,         PARM_IN,            "script",             None),
    (JSObjectRef,         PARM_IN,            "thisObject",         None),
    (JSStringRef,         PARM_IN,            "sourceURL",          None),
    (c_int,               PARM_IN,            "startingLineNumber", 1),
    (POINTER(JSValueRef), PARM_IN | PARM_OUT, "exception",          None),
))

#-------------------------------------------------------------------
JSGarbageCollect = defineFunction("JSGarbageCollect", None, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
))

#===================================================================
# JSContextRef
#===================================================================

#-------------------------------------------------------------------
JSContextGetGlobalObject = defineFunction("JSContextGetGlobalObject", JSObjectRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
))

#-------------------------------------------------------------------
JSGlobalContextCreate = defineFunction("JSGlobalContextCreate", JSGlobalContextRef, (
    (JSClassRef,          PARM_IN,            "globalObjectClass",  None), 
))

#-------------------------------------------------------------------
JSGlobalContextRelease = defineFunction("JSGlobalContextRelease", None, (
    (JSGlobalContextRef,  PARM_IN,            "ctx",                None), 
))

#-------------------------------------------------------------------
JSGlobalContextRetain = defineFunction("JSGlobalContextRetain", JSGlobalContextRef, (
    (JSGlobalContextRef,  PARM_IN,            "ctx",                None), 
))

#===================================================================
# JSObjectRef
#===================================================================

#-------------------------------------------------------------------
JSClassCreate = defineFunction("JSClassCreate", JSClassRef, (
    (POINTER(JSClassDefinition), PARM_IN,     "definition",         None), 
))

#-------------------------------------------------------------------
JSClassRelease = defineFunction("JSClassRelease", None, (
    (JSClassRef,          PARM_IN,            "jsClass",            None), 
))

#-------------------------------------------------------------------
JSClassRetain = defineFunction("JSClassRetain", None, (
    (JSClassRef,          PARM_IN,            "jsClass",            None), 
))

#-------------------------------------------------------------------
JSObjectCallAsConstructor = defineFunction("JSObjectCallAsConstructor", JSObjectRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSObjectRef,         PARM_IN,            "object",             None), 
    (c_size_t,            PARM_IN,            "argumentCount",      0), 
    (POINTER(JSValueRef), PARM_IN,            "arguments",          None), 
    (POINTER(JSValueRef), PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
JSObjectCallAsFunction = defineFunction("JSObjectCallAsFunction", JSValueRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSObjectRef,         PARM_IN,            "object",             None), 
    (JSObjectRef,         PARM_IN,            "thisObject",         None), 
    (c_size_t,            PARM_IN,            "argumentCount",      0), 
    (POINTER(JSValueRef), PARM_IN,            "arguments",          None), 
    (POINTER(JSValueRef), PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
JSObjectCopyPropertyNames = defineFunction("JSObjectCopyPropertyNames", JSPropertyNameArrayRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSObjectRef,         PARM_IN,            "object",             None), 
))

#-------------------------------------------------------------------
JSObjectDeleteProperty = defineFunction("JSObjectDeleteProperty", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",              None), 
    (JSObjectRef,         PARM_IN,            "object",           None), 
    (JSStringRef,         PARM_IN,            "propertyName",     None), 
    (POINTER(JSValueRef), PARM_IN,            "exception",        None), 
))

#-------------------------------------------------------------------
JSObjectGetPrivate = defineFunction("JSObjectGetPrivate", c_void_p, (
    (JSObjectRef,         PARM_IN,            "object",             None), 
))

#-------------------------------------------------------------------
JSObjectGetProperty = defineFunction("JSObjectGetProperty", JSValueRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSObjectRef,         PARM_IN,            "object",             None), 
    (JSStringRef,         PARM_IN,            "propertyName",       None), 
    (POINTER(JSValueRef), PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
JSObjectGetPropertyAtIndex = defineFunction("JSObjectGetPropertyAtIndex", JSValueRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSObjectRef,         PARM_IN,            "object",             None), 
    (c_uint,              PARM_IN,            "propertyIndex",      None), 
    (POINTER(JSValueRef), PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
JSObjectGetPrototype = defineFunction("JSObjectGetPrototype", JSValueRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSObjectRef,         PARM_IN,            "object",             None), 
))

#-------------------------------------------------------------------
JSObjectHasProperty = defineFunction("JSObjectHasProperty", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSObjectRef,         PARM_IN,            "object",             None), 
    (JSStringRef,         PARM_IN,            "propertyName",       None), 
))

#-------------------------------------------------------------------
JSObjectIsConstructor = defineFunction("JSObjectIsConstructor", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSObjectRef,         PARM_IN,            "object",             None), 
))

#-------------------------------------------------------------------
JSObjectIsFunction = defineFunction("JSObjectIsFunction", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSObjectRef,         PARM_IN,            "object",             None), 
))

#-------------------------------------------------------------------
JSObjectMake = defineFunction("JSObjectMake", JSObjectRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSClassRef,          PARM_IN,            "jsClass",            None), 
    (c_void_p,            PARM_IN,            "data",               None), 
))

#-------------------------------------------------------------------
JSObjectMakeConstructor = defineFunction("JSObjectMakeConstructor", JSObjectRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSClassRef,          PARM_IN,            "jsClass",            None), 
    (JSObjectCallAsConstructorCallback, PARM_IN, "callAsConstructor",   None), 
))

#-------------------------------------------------------------------
JSObjectMakeFunction = defineFunction("JSObjectMakeFunction", JSObjectRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSStringRef,         PARM_IN,            "name",               None), 
    (c_uint,              PARM_IN,            "parameterCount",     None), 
    (POINTER(JSStringRef),PARM_IN,            "parameterNames",     None), 
    (JSStringRef,         PARM_IN,            "body",               None), 
    (JSStringRef,         PARM_IN,            "sourceURL",          None), 
    (c_int,               PARM_IN,            "startingLineNumber", 1), 
    (POINTER(JSValueRef), PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
JSObjectMakeFunctionWithCallback = defineFunction("JSObjectMakeFunctionWithCallback", JSObjectRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSStringRef,         PARM_IN,            "name",               None), 
    (JSObjectCallAsFunctionCallback, PARM_IN, "callAsFunction",     None), 
))

#-------------------------------------------------------------------
JSObjectSetPrivate = defineFunction("JSObjectSetPrivate", c_int, (
    (JSObjectRef,         PARM_IN,            "object",             None), 
    (c_void_p,            PARM_IN,            "data",               None), 
))

#-------------------------------------------------------------------
JSObjectSetProperty = defineFunction("JSObjectSetProperty", None, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSObjectRef,         PARM_IN,            "object",             None), 
    (JSStringRef,         PARM_IN,            "propertyName",       None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
    (JSPropertyAttributes,PARM_IN,            "attributes",         0), 
    (POINTER(JSValueRef), PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
JSObjectSetPropertyAtIndex = defineFunction("JSObjectSetPropertyAtIndex", None, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSObjectRef,         PARM_IN,            "object",             None), 
    (c_uint,              PARM_IN,            "propertyIndex",      0), 
    (JSValueRef,          PARM_IN,            "value",              None), 
    (POINTER(JSValueRef), PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
JSObjectSetPrototype = defineFunction("JSObjectSetPrototype", None, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSObjectRef,         PARM_IN,            "object",             None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
JSPropertyNameAccumulatorAddName = defineFunction("JSPropertyNameAccumulatorAddName", None, (
    (JSPropertyNameAccumulatorRef, PARM_IN,   "accumulator",        None), 
    (JSStringRef,         PARM_IN,            "propertyName",       None), 
))

#-------------------------------------------------------------------
JSPropertyNameArrayGetCount = defineFunction("JSPropertyNameArrayGetCount", c_size_t, (
    (JSPropertyNameArrayRef, PARM_IN,         "array",              None), 
))

#-------------------------------------------------------------------
JSPropertyNameArrayGetNameAtIndex = defineFunction("JSPropertyNameArrayGetNameAtIndex", JSStringRef, (
    (JSPropertyNameArrayRef, PARM_IN,         "array",              None), 
    (c_size_t,            PARM_IN,            "index",              None), 
))

#-------------------------------------------------------------------
JSPropertyNameArrayRelease = defineFunction("JSPropertyNameArrayRelease", None, (
    (JSPropertyNameArrayRef, PARM_IN,         "array",                None), 
))

#-------------------------------------------------------------------
JSPropertyNameArrayRetain = defineFunction("JSPropertyNameArrayRetain", JSPropertyNameArrayRef, (
    (JSPropertyNameArrayRef, PARM_IN,         "array",                None), 
))

#===================================================================
# JSStringRef
#===================================================================

#-------------------------------------------------------------------
JSStringCreateWithCharacters = defineFunction("JSStringCreateWithCharacters", JSStringRef, (
    (POINTER(JSChar),     PARM_IN,            "chars",               None), 
    (c_size_t,            PARM_IN,            "numChars",            0), 
))

#-------------------------------------------------------------------
JSStringCreateWithUTF8CString = defineFunction("JSStringCreateWithUTF8CString", JSStringRef, (
    (c_char_p,            PARM_IN,            "string",              None), 
))

#-------------------------------------------------------------------
JSStringGetCharactersPtr = defineFunction("JSStringGetCharactersPtr", POINTER(JSChar), (
    (JSStringRef,         PARM_IN,            "string",              None), 
))

#-------------------------------------------------------------------
JSStringGetLength = defineFunction("JSStringGetLength", c_int32, (
    (JSStringRef,         PARM_IN,            "string",              None), 
))

#-------------------------------------------------------------------
JSStringGetMaximumUTF8CStringSize = defineFunction("JSStringGetMaximumUTF8CStringSize", c_size_t, (
    (JSStringRef,         PARM_IN,            "string",              None), 
))

#-------------------------------------------------------------------
JSStringGetUTF8CString = defineFunction("JSStringGetUTF8CString", c_size_t, (
    (JSStringRef,         PARM_IN,            "string",              None), 
    (c_char_p,            PARM_IN,            "buffer",              None), 
    (c_size_t,            PARM_IN,            "bufferSize",          0), 
))

#-------------------------------------------------------------------
JSStringIsEqual = defineFunction("JSStringIsEqual", c_int, (
    (JSStringRef,         PARM_IN,            "a",                   None), 
    (JSStringRef,         PARM_IN,            "b",                   None), 
))

#-------------------------------------------------------------------
JSStringIsEqualToUTF8CString = defineFunction("JSStringIsEqualToUTF8CString", c_int, (
    (JSStringRef,         PARM_IN,            "a",                   None), 
    (c_char_p,            PARM_IN,            "b",                   None), 
))

#-------------------------------------------------------------------
JSStringRelease = defineFunction("JSStringRelease", None, (
    (JSStringRef,         PARM_IN,            "string",              None), 
))

#-------------------------------------------------------------------
JSStringRetain = defineFunction("JSStringRetain", JSStringRef, (
    (JSStringRef,         PARM_IN,            "string",              None), 
))

#===================================================================
# JSValueRef
#===================================================================

#-------------------------------------------------------------------
JSValueGetType = defineFunction("JSValueGetType", JSType, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
JSValueIsBoolean = defineFunction("JSValueIsBoolean", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
JSValueIsEqual = defineFunction("JSValueIsEqual", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "a",                  None), 
    (JSValueRef,          PARM_IN,            "b",                  None), 
    (POINTER(JSValueRef), PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
JSValueIsInstanceOfConstructor = defineFunction("JSValueIsInstanceOfConstructor", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
    (JSObjectRef,         PARM_IN,            "constructor",        None), 
    (POINTER(JSValueRef), PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
JSValueIsNull = defineFunction("JSValueIsNull", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
JSValueIsNumber = defineFunction("JSValueIsNumber", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
JSValueIsObject = defineFunction("JSValueIsObject", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
JSValueIsObjectOfClass = defineFunction("JSValueIsObjectOfClass", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
    (JSClassRef,          PARM_IN,            "jsClass",            None), 
))

#-------------------------------------------------------------------
JSValueIsStrictEqual = defineFunction("JSValueIsStrictEqual", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "a",                  None), 
    (JSValueRef,          PARM_IN,            "b",                  None), 
))

#-------------------------------------------------------------------
JSValueIsString = defineFunction("JSValueIsString", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
JSValueIsUndefined = defineFunction("JSValueIsUndefined", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
JSValueMakeBoolean = defineFunction("JSValueMakeBoolean", JSValueRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (c_int,               PARM_IN,            "boolean",            0), 
))

#-------------------------------------------------------------------
JSValueMakeNull = defineFunction("JSValueMakeNull", JSValueRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
))

#-------------------------------------------------------------------
JSValueMakeNumber = defineFunction("JSValueMakeNumber", JSValueRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (c_double,            PARM_IN,            "number",             None), 
))

#-------------------------------------------------------------------
JSValueMakeString = defineFunction("JSValueMakeString", JSValueRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSStringRef,         PARM_IN,            "string",             None), 
))

#-------------------------------------------------------------------
JSValueMakeUndefined = defineFunction("JSValueMakeUndefined", None, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
))

#-------------------------------------------------------------------
JSValueProtect = defineFunction("JSValueProtect", None, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
JSValueToBoolean = defineFunction("JSValueToBoolean", c_int, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
))

#-------------------------------------------------------------------
JSValueToNumber = defineFunction("JSValueToNumber", c_double, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
    (POINTER(JSValueRef), PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
JSValueToObject = defineFunction("JSValueToObject", JSObjectRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
    (POINTER(JSValueRef), PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
JSValueToStringCopy = defineFunction("JSValueToStringCopy", JSStringRef, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
    (POINTER(JSValueRef), PARM_IN,            "exception",          None), 
))

#-------------------------------------------------------------------
JSValueUnprotect = defineFunction("JSValueUnprotect", None, (
    (JSContextRef,        PARM_IN,            "ctx",                None), 
    (JSValueRef,          PARM_IN,            "value",              None), 
))
