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
	
#	print "defineFunction(%s, %s, %s)" % (name, str(resType), str(parms))
#	print "   types:      %s" % types
#	print "   paramFlags: %s" % paramFlags
	
	prototype = CFUNCTYPE(resType, *types)
#	print "   prototype:  %s" % prototype

	function  = prototype((name, JSC), tuple(paramFlags))
#	print "   function:   %s" % function
	
	return function

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
JSChar                        = c_ushort
JSType                        = c_int
JSClassAttribute              = c_int
JSPropertyAttribute           = c_int
JSPropertyAttributes          = c_uint

#-------------------------------------------------------------------
# enums
#-------------------------------------------------------------------

# JSType
kJSTypeUndefined              = 0
kJSTypeNull                   = 1
kJSTypeBoolean                = 2
kJSTypeNumber                 = 3
kJSTypeString                 = 4
kJSTypeObject                 = 5

# JSClassAttribute
kJSClassAttributeNone                 = 0
kJSClassAttributeNoAutomaticPrototype = 1 << 1 

# JSPropertyAttribute
kJSPropertyAttributeNone       = 0
kJSPropertyAttributeReadOnly   = 1 << 1
kJSPropertyAttributeDontEnum   = 1 << 2 
kJSPropertyAttributeDontDelete = 1 << 3 

#-------------------------------------------------------------------
# structures
#-------------------------------------------------------------------

#-------------------------------------------------------------------
class JSClassDefinition(ctypes.Structure):
    pass

"""
This structure contains properties and callbacks that define a type of object. All fields other than the version field are optional. Any pointer may be NULL.

typedef struct { 
    int version; // current (and only) version is 0 
    JSClassAttributes attributes;  
    const char *className; 
    JSClassRef parentClass;  
    const JSStaticValue *staticValues; 
    const JSStaticFunction *staticFunctions;  
    JSObjectInitializeCallback initialize; 
    JSObjectFinalizeCallback finalize; 
    JSObjectHasPropertyCallback hasProperty; 
    JSObjectGetPropertyCallback getProperty; 
    JSObjectSetPropertyCallback setProperty; 
    JSObjectDeletePropertyCallback deleteProperty; 
    JSObjectGetPropertyNamesCallback getPropertyNames; 
    JSObjectCallAsFunctionCallback callAsFunction; 
    JSObjectCallAsConstructorCallback callAsConstructor; 
    JSObjectHasInstanceCallback hasInstance; 
    JSObjectConvertToTypeCallback convertToType; 
} JSClassDefinition;  
Fields
version
The version number of this structure. The current version is 0.
attributes
A logically ORed set of JSClassAttributes to give to the class.
className
A null-terminated UTF8 string containing the class's name.
parentClass
A JSClass to set as the class's parent class. Pass NULL use the default object class.
staticValues
A JSStaticValue array containing the class's statically declared value properties. Pass NULL to specify no statically declared value properties. The array must be terminated by a JSStaticValue whose name field is NULL.
staticFunctions
A JSStaticFunction array containing the class's statically declared function properties. Pass NULL to specify no statically declared function properties. The array must be terminated by a JSStaticFunction whose name field is NULL.
initialize
The callback invoked when an object is first created. Use this callback to initialize the object.
finalize
The callback invoked when an object is finalized (prepared for garbage collection). Use this callback to release resources allocated for the object, and perform other cleanup.
hasProperty
The callback invoked when determining whether an object has a property. If this field is NULL, getProperty is called instead. The hasProperty callback enables optimization in cases where only a property's existence needs to be known, not its value, and computing its value is expensive.
getProperty
The callback invoked when getting a property's value.
setProperty
The callback invoked when setting a property's value.
deleteProperty
The callback invoked when deleting a property.
getPropertyNames
The callback invoked when collecting the names of an object's properties.
callAsFunction
The callback invoked when an object is called as a function.
hasInstance
The callback invoked when an object is used as the target of an 'instanceof' expression.
callAsConstructor
The callback invoked when an object is used as a constructor in a 'new' expression.
convertToType
The callback invoked when converting an object to a particular JavaScript type.
Discussion
The staticValues and staticFunctions arrays are the simplest and most efficient means for vending custom properties. Statically declared properties autmatically service requests like getProperty, setProperty, and getPropertyNames. Property access callbacks are required only to implement unusual properties, like array indexes, whose names are not known at compile-time. 

If you named your getter function "GetX" and your setter function "SetX", you would declare a JSStaticValue array containing "X" like this: 

JSStaticValue StaticValueArray[] = { { "X", GetX, SetX, kJSPropertyAttributeNone }, { 0, 0, 0, 0 } }; 

Standard JavaScript practice calls for storing function objects in prototypes, so they can be shared. The default JSClass created by JSClassCreate follows this idiom, instantiating objects with a shared, automatically generating prototype containing the class's function objects. The kJSClassAttributeNoAutomaticPrototype attribute specifies that a JSClass should not automatically generate such a prototype. The resulting JSClass instantiates objects with the default object prototype, and gives each instance object its own copy of the class's function objects. 

A NULL callback specifies that the default object callback should substitute, except in the case of hasProperty, where it specifies that getProperty should substitute.
"""

#-------------------------------------------------------------------
class JSObjectCallAsConstructorCallback(ctypes.Structure):
    pass

"""
The callback invoked when an object is used as a constructor in a 'new' expression.

typedef JSObjectRef ( *JSObjectCallAsConstructorCallback) (
    JSContextRef ctx,
    JSObjectRef constructor,
    size_t argumentCount,
    const JSValueRef arguments[],
    JSValueRef *exception);  
Parameters
ctx
The execution context to use.
constructor
A JSObject that is the constructor being called.
argumentCount
An integer count of the number of arguments in arguments.
arguments
A JSValue array of the arguments passed to the function.
exception
A pointer to a JSValueRef in which to return an exception, if any.
Return Value
A JSObject that is the constructor's return value.
Discussion
If you named your function CallAsConstructor, you would declare it like this: 

JSObjectRef CallAsConstructor(JSContextRef ctx, JSObjectRef constructor, size_t argumentCount, const JSValueRef arguments[], JSValueRef* exception); 

If your callback were invoked by the JavaScript expression 'new myConstructor()', constructor would be set to myConstructor. 

If this callback is NULL, using your object as a constructor in a 'new' expression will throw an exception.
"""

#-------------------------------------------------------------------
class JSObjectCallAsFunctionCallback(ctypes.Structure):
    pass

"""
The callback invoked when an object is called as a function.

typedef JSValueRef ( *JSObjectCallAsFunctionCallback) (
    JSContextRef ctx,
    JSObjectRef function,
    JSObjectRef thisObject,
    size_t argumentCount,
    const JSValueRef arguments[],
    JSValueRef *exception);  
Parameters
ctx
The execution context to use.
function
A JSObject that is the function being called.
thisObject
A JSObject that is the 'this' variable in the function's scope.
argumentCount
An integer count of the number of arguments in arguments.
arguments
A JSValue array of the arguments passed to the function.
exception
A pointer to a JSValueRef in which to return an exception, if any.
Return Value
A JSValue that is the function's return value.
Discussion
If you named your function CallAsFunction, you would declare it like this: 

JSValueRef CallAsFunction(JSContextRef ctx, JSObjectRef function, JSObjectRef thisObject, size_t argumentCount, const JSValueRef arguments[], JSValueRef* exception); 

If your callback were invoked by the JavaScript expression 'myObject.myFunction()', function would be set to myFunction, and thisObject would be set to myObject. 

If this callback is NULL, calling your object as a function will throw an exception.
"""

#-------------------------------------------------------------------
class JSObjectConvertToTypeCallback(ctypes.Structure):
    pass

"""
The callback invoked when converting an object to a particular JavaScript type.

typedef JSValueRef ( *JSObjectConvertToTypeCallback) (
    JSContextRef ctx,
    JSObjectRef object,
    JSType type,
    JSValueRef *exception);  
Parameters
ctx
The execution context to use.
object
The JSObject to convert.
type
A JSType specifying the JavaScript type to convert to.
exception
A pointer to a JSValueRef in which to return an exception, if any.
Return Value
The objects's converted value, or NULL if the object was not converted.
Discussion
If you named your function ConvertToType, you would declare it like this: 

JSValueRef ConvertToType(JSContextRef ctx, JSObjectRef object, JSType type, JSValueRef* exception); 

If this function returns false, the conversion request forwards to object's parent class chain (which includes the default object class). 

This function is only invoked when converting an object to number or string. An object converted to boolean is 'true.' An object converted to object is itself.
"""

#-------------------------------------------------------------------
class JSObjectDeletePropertyCallback(ctypes.Structure):
    pass

"""
The callback invoked when deleting a property.

typedef bool ( *JSObjectDeletePropertyCallback) (
    JSContextRef ctx,
    JSObjectRef object,
    JSStringRef propertyName,
    JSValueRef *exception);  
Parameters
ctx
The execution context to use.
object
The JSObject in which to delete the property.
propertyName
A JSString containing the name of the property to delete.
exception
A pointer to a JSValueRef in which to return an exception, if any.
Return Value
true if propertyName was successfully deleted, otherwise false.
Discussion
If you named your function DeleteProperty, you would declare it like this: 

bool DeleteProperty(JSContextRef ctx, JSObjectRef object, JSStringRef propertyName, JSValueRef* exception); 

If this function returns false, the delete request forwards to object's statically declared properties, then its parent class chain (which includes the default object class).
"""

#-------------------------------------------------------------------
class JSObjectFinalizeCallback(ctypes.Structure):
    pass

"""
The callback invoked when an object is finalized (prepared for garbage collection). An object may be finalized on any thread.

typedef void ( *JSObjectFinalizeCallback) (
    JSObjectRef object);  
Parameters
object
The JSObject being finalized.
Discussion
If you named your function Finalize, you would declare it like this: 

void Finalize(JSObjectRef object); 

The finalize callback is called on the most derived class first, and the least derived class (the parent class) last. 

You must not call any function that may cause a garbage collection or an allocation of a garbage collected object from within a JSObjectFinalizeCallback. This includes all functions that have a JSContextRef parameter.
"""

#-------------------------------------------------------------------
class JSObjectGetPropertyCallback(ctypes.Structure):
    pass

"""
The callback invoked when getting a property's value.

typedef JSValueRef ( *JSObjectGetPropertyCallback) (
    JSContextRef ctx,
    JSObjectRef object,
    JSStringRef propertyName,
    JSValueRef *exception);  
Parameters
ctx
The execution context to use.
object
The JSObject to search for the property.
propertyName
A JSString containing the name of the property to get.
exception
A pointer to a JSValueRef in which to return an exception, if any.
Return Value
The property's value if object has the property, otherwise NULL.
Discussion
If you named your function GetProperty, you would declare it like this: 

JSValueRef GetProperty(JSContextRef ctx, JSObjectRef object, JSStringRef propertyName, JSValueRef* exception); 

If this function returns NULL, the get request forwards to object's statically declared properties, then its parent class chain (which includes the default object class), then its prototype chain.
"""

#-------------------------------------------------------------------
class JSObjectGetPropertyNamesCallback(ctypes.Structure):
    pass

"""
The callback invoked when collecting the names of an object's properties.

typedef void ( *JSObjectGetPropertyNamesCallback) (
    JSContextRef ctx,
    JSObjectRef object,
    JSPropertyNameAccumulatorRef propertyNames);  
Parameters
ctx
The execution context to use.
object
The JSObject whose property names are being collected.
propertyNames
A JavaScript property name accumulator in which to accumulate the names of object's properties.
Discussion
If you named your function GetPropertyNames, you would declare it like this: 

void GetPropertyNames(JSContextRef ctx, JSObjectRef object, JSPropertyNameAccumulatorRef accumulator); 

Property name accumulators are used by JSObjectCopyPropertyNames and JavaScript for...in loops. 

Use JSPropertyNameAccumulatorAddName to add property names to accumulator. A class's getPropertyNames callback only needs to provide the names of properties that the class vends through a custom getProperty or setProperty callback. Other properties, including statically declared properties, properties vended by other classes, and properties belonging to object's prototype, are added independently.
"""

#-------------------------------------------------------------------
class JSObjectHasInstanceCallback(ctypes.Structure):
    pass

"""
hasInstance The callback invoked when an object is used as the target of an 'instanceof' expression.

typedef bool ( *JSObjectHasInstanceCallback) (
    JSContextRef ctx,
    JSObjectRef constructor,
    JSValueRef possibleInstance,
    JSValueRef *exception);  
Parameters
ctx
The execution context to use.
constructor
The JSObject that is the target of the 'instanceof' expression.
possibleInstance
The JSValue being tested to determine if it is an instance of constructor.
exception
A pointer to a JSValueRef in which to return an exception, if any.
Return Value
true if possibleInstance is an instance of constructor, otherwise false.
Discussion
If you named your function HasInstance, you would declare it like this: 

bool HasInstance(JSContextRef ctx, JSObjectRef constructor, JSValueRef possibleInstance, JSValueRef* exception); 

If your callback were invoked by the JavaScript expression 'someValue instanceof myObject', constructor would be set to myObject and possibleInstance would be set to someValue. 

If this callback is NULL, 'instanceof' expressions that target your object will return false. 

Standard JavaScript practice calls for objects that implement the callAsConstructor callback to implement the hasInstance callback as well.
"""

#-------------------------------------------------------------------
class JSObjectHasPropertyCallback(ctypes.Structure):
    pass

"""
The callback invoked when determining whether an object has a property.

typedef bool ( *JSObjectHasPropertyCallback) (
    JSContextRef ctx,
    JSObjectRef object,
    JSStringRef propertyName);  
Parameters
ctx
The execution context to use.
object
The JSObject to search for the property.
propertyName
A JSString containing the name of the property look up.
Return Value
true if object has the property, otherwise false.
Discussion
If you named your function HasProperty, you would declare it like this: 

bool HasProperty(JSContextRef ctx, JSObjectRef object, JSStringRef propertyName); 

If this function returns false, the hasProperty request forwards to object's statically declared properties, then its parent class chain (which includes the default object class), then its prototype chain. 

This callback enables optimization in cases where only a property's existence needs to be known, not its value, and computing its value would be expensive. 

If this callback is NULL, the getProperty callback will be used to service hasProperty requests.
"""

#-------------------------------------------------------------------
class JSObjectInitializeCallback(ctypes.Structure):
    pass

"""
The callback invoked when an object is first created.

typedef void ( *JSObjectInitializeCallback) (
    JSContextRef ctx,
    JSObjectRef object);  
Parameters
ctx
The execution context to use.
object
The JSObject being created.
Discussion
If you named your function Initialize, you would declare it like this: 

void Initialize(JSContextRef ctx, JSObjectRef object); 

Unlike the other object callbacks, the initialize callback is called on the least derived class (the parent class) first, and the most derived class last.
"""

#-------------------------------------------------------------------
class JSObjectSetPropertyCallback(ctypes.Structure):
    pass

"""
The callback invoked when setting a property's value.

typedef bool ( *JSObjectSetPropertyCallback) (
    JSContextRef ctx,
    JSObjectRef object,
    JSStringRef propertyName,
    JSValueRef value,
    JSValueRef *exception);  
Parameters
ctx
The execution context to use.
object
The JSObject on which to set the property's value.
propertyName
A JSString containing the name of the property to set.
value
A JSValue to use as the property's value.
exception
A pointer to a JSValueRef in which to return an exception, if any.
Return Value
true if the property was set, otherwise false.
Discussion
If you named your function SetProperty, you would declare it like this: 

bool SetProperty(JSContextRef ctx, JSObjectRef object, JSStringRef propertyName, JSValueRef value, JSValueRef* exception); 

If this function returns false, the set request forwards to object's statically declared properties, then its parent class chain (which includes the default object class).
"""

#-------------------------------------------------------------------
class JSStaticFunction(ctypes.Structure):
    pass

"""
This structure describes a statically declared function property.

typedef struct { 
    const char *const name; 
    JSObjectCallAsFunctionCallback callAsFunction; 
    JSPropertyAttributes attributes; 
} JSStaticFunction;  
Fields
name
A null-terminated UTF8 string containing the property's name.
callAsFunction
A JSObjectCallAsFunctionCallback to invoke when the property is called as a function.
attributes
A logically ORed set of JSPropertyAttributes to give to the property.
"""

#-------------------------------------------------------------------
class JSStaticValue(ctypes.Structure):
    pass

"""
This structure describes a statically declared value property.

typedef struct { 
    const char *const name; 
    JSObjectGetPropertyCallback getProperty; 
    JSObjectSetPropertyCallback setProperty; 
    JSPropertyAttributes attributes; 
} JSStaticValue;  
Fields
name
A null-terminated UTF8 string containing the property's name.
getProperty
A JSObjectGetPropertyCallback to invoke when getting the property's value.
setProperty
A JSObjectSetPropertyCallback to invoke when setting the property's value. May be NULL if the ReadOnly attribute is set.
attributes
A logically ORed set of JSPropertyAttributes to g
"""

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
