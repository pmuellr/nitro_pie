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
__date__    = "2009-04-29"
__version__ = "0.6"

__all__ = """
NitroLogging

JSException
JSGlobalContextRef
JSLibrary
JSObjectRef
JSStringRef
JSValueRef
""".split()

import os
import ctypes
import ctypes.util
import inspect

#-------------------------------------------------------------------
# logger
#-------------------------------------------------------------------
_LOGGING = False

def NitroLogging(bool):
    global _LOGGING
    _LOGGING = bool

def _log(message="", args=None):
    if not _LOGGING: return
    
    caller = inspect.stack()[1]
    (frame, filename, lineNumber, function, context, contextIndex) = caller
    filename = os.path.basename(filename)
    
    if args:
        args    = [str(arg) for arg in args]
        message = message % tuple(args)
        
    message = message.replace("$f", function)
    message = message.replace("\n", "\\n")
    
    print "%s[%4d]: %s" % (filename, lineNumber, message)

if False:
    #-------------------------------------------------------------------
    kJSTypeUndefined = 0
    kJSTypeNull      = 1
    kJSTypeBoolean   = 2
    kJSTypeNumber    = 3
    kJSTypeString    = 4
    kJSTypeObject    = 5 
    
    #-------------------------------------------------------------------
    kJSPropertyAttributeNone       = 0
    kJSPropertyAttributeReadOnly   = 1 << 1
    kJSPropertyAttributeDontEnum   = 1 << 2 
    kJSPropertyAttributeDontDelete = 1 << 3 

#--------------------------------------------------------------------
class JSContextRef(ctypes.c_void_p):
    """Models the JSContextRef type.
    
    <p>These methods call functions defined in 
    &[JSContextRef.h][http://developer.apple.com/documentation/Carbon/Reference/WebKit_JavaScriptCore_Ref/JSContextRef/index.html].
    """
    functions = []
    
    #----------------------------------------------------------------
    def getGlobalObject(self):
        """Returns the global object associated with a context.
        
        @returns #[JSValueRef]
        """
        _log("JSContextRef.$f(%s)", (self,))
        result = _JSContextGetGlobalObject(self)
        return result
    
    #----------------------------------------------------------------
    def garbageCollect(self):
        """Runs the garbage collector.
        
        The garbage collector does *[need] to be run explicitly,
        but can.
        """
        _log("JSContextRef.$f(%s)", (self,))
        return _JSGarbageCollect(self)
    
    #----------------------------------------------------------------
    def eval(self, script, thisObject=None, sourceURL=None, startingLineNumber=1):
        """Evaluate a string of JavaScript code.
        
        @returns (#[JSValueRef]) The value of executing the script.
        
        @param script             (str | unicode | #[JSStringRef])
        @param thisObject         (#[JSObjectRef])
        @param sourceURL          (str | unicode | #[JSStringRef])
        @param startingLineNumber (int)
        
        @throws (#[JSException])  When a JavaScript exception occurs
            during the processing of the script
        """
        _log("JSContextRef.$f(%s, '%s', %s, '%s', %s)", (self, script, thisObject, sourceURL, startingLineNumber))
        if thisObject:         assert isinstance(context,            JSObjectRef),   "Expecting a JSValueRef for the thisObject parameter"
        if startingLineNumber: assert isinstance(startingLineNumber, int),          "Expecting an int for the startingLineNumber parameter"

        scriptRef    = JSStringRef.asRef(script)
        sourceURLRef = JSStringRef.asRef(sourceURL)
        exception    = JSValueRef()
        exception.protect(self)
        
        if not scriptRef: 
            raise TypeError, "Expecting a string for the script parameter"
            
        _log("JSContextRef.$f() ->")
        result = _JSEvaluateScript(
            self,
            scriptRef,
            thisObject,
            sourceURLRef,
            startingLineNumber,
            ctypes.byref(exception)
            )
        _log("JSContextRef.$f() -> %s", (result,))

        if script    != scriptRef:    scriptRef.release()
        if sourceURL != sourceURLRef: sourceURLRef.release()
        
        if exception.value: 
            _log("JSContextRef.$f() raising exception")
            raise JSException, exception

        exception.unprotect(self)
        
        return result
    
    #----------------------------------------------------------------
    def checkScriptSyntax(self, script, sourceURL=None, startingLineNumber=1):
        _log("JSContextRef.$f(%s, '%s', '%s', %s)", (self, script, sourceURL, startingLineNumber))
        if startingLineNumber: assert isinstance(startingLineNumber, int),          "Expecting an int for the startingLineNumber parameter"
    
        scriptRef    = JSStringRef.asRef(script)
        sourceURLRef = JSStringRef.asRef(sourceURL)
        exception    = JSValueRef(None)
        
        if not scriptRef: 
            raise TypeError, "Expecting a string for the script parameter"
            
        result = _JSCheckScriptSyntax(
            self,
            scriptRef,
            sourceURLRef,
            startingLineNumber,
            ctypes.byref(exception)
            )
        
        if script    != scriptRef:    scriptRef.release()
        if sourceURL != sourceURLRef: sourceURLRef.release()

        if exception.value: 
            raise JSException, exception
            
        return result
    
    #----------------------------------------------------------------
    def makeFunction(self, name, function):
        _log("JSContextRef.$f(%s, '%s', %s)", (self, name, function))
        assert callable(function), "Expecting a function for the function parameter"
        
        def callbackFunction(cbContext, cbFunction, thisObject, argCount, argRefs, exception):
            args = []
            
            for i in xrange(0, argCount):
                args.append(argRefs[i])
            
            result = function(cbContext, cbFunction, thisObject, args)
            
            if not result: return None
            
            if not isinstance(result,JSValueRef):
                raise TypeError, "callback function: '%s' - callbacks must return a JSValueRef" % name
            
            return result.value
            
        callback = JSObjectCallAsFunctionCallback(callbackFunction)
        
        # problem - need to keep the callbacks from being GC'd
        JSContextRef.functions.append(callback)
        
        nameRef = JSStringRef.asRef(name)
        
        result = _JSObjectMakeFunctionWithCallback(self, nameRef, callback)
        
        if name != nameRef: nameRef.release()
        
        return result
    
#--------------------------------------------------------------------
class JSGlobalContextRef(JSContextRef):
    """Models the JSGlobalContextRef type.
    
    <p>These methods call functions defined in 
    &[JSContextRef.h][http://developer.apple.com/documentation/Carbon/Reference/WebKit_JavaScriptCore_Ref/JSContextRef/index.html].
    """

    #----------------------------------------------------------------
    @staticmethod
    def create():
        _log("JSGlobalContextRef.$f()")
        return _JSGlobalContextCreate(None)
        
    #----------------------------------------------------------------
    def release(self):
        _log("JSGlobalContextRef.$f(%s)", (str(self),))
        return _JSGlobalContextRelease(self)
    
    #----------------------------------------------------------------
    def retain(self):
        _log("JSGlobalContextRef.$f(%s)", (str(self),))
        return _JSGlobalContextRetain(self)
    

#--------------------------------------------------------------------
class JSStringRef(ctypes.c_void_p):
    """Models the JSStringRef type.
    
    <p>These methods call functions defined in 
    &[JSStringRef.h][http://developer.apple.com/documentation/Carbon/Reference/WebKit_JavaScriptCore_Ref/JSStringRef/index.html].
    """

    #----------------------------------------------------------------
    @staticmethod
    def asRef(string):
        if not string: return string
        if isinstance(string, JSStringRef): return string
        
        return JSStringRef.create(string)

    #----------------------------------------------------------------
    @staticmethod
    def create(string):
        _log("JSStringRef.$f('%s')", (string,))
    
        if isinstance(string, str):
            # make sure it's utf-8
            uniString = unicode(string,  "utf-8" )
            string    = uniString.encode("utf-8")
        
        elif isinstance(string, unicode):
            string = string.encode("utf-8")
            
        else:
            raise TypeError, "expecting a string"
            
        buffer = ctypes.create_string_buffer(string)
        
        result = _JSStringCreateWithUTF8CString(buffer)
        
        _log("JSStringRef.$f() -> %s", (result,))
        
        return result

    #----------------------------------------------------------------
    def toString(self):
        _log("JSStringRef.$f(%s)", (self,))
        
        len    = _JSStringGetMaximumUTF8CStringSize(self) + 1
        result = ctypes.create_string_buffer(len)
    
        _JSStringGetUTF8CString(self, result, len)
        
        _log("JSStringRef.$f() -> '%s'", (result.value,))
        
        return result.value

    #----------------------------------------------------------------
    def retain(self):
        _log("JSStringRef.$f(%s)", (self,))
    
        _JSStringRetain(self)
        
    #----------------------------------------------------------------
    def release(self):
        _log("JSStringRef.$f(%s)", (self,))
        
        _JSStringRelease(self)

#--------------------------------------------------------------------
class JSValueRef(ctypes.c_void_p):
    """Models the JSValueRef type.
    
    <p>These methods call functions defined in 
    &[JSValueRef.h][http://developer.apple.com/documentation/Carbon/Reference/WebKit_JavaScriptCore_Ref/JSValueRef/index.html].
    """

    kJSTypeUndefined = 0
    kJSTypeNull      = 1
    kJSTypeBoolean   = 2
    kJSTypeNumber    = 3
    kJSTypeString    = 4
    kJSTypeObject    = 5 

    #----------------------------------------------------------------
    @staticmethod
    def makeBoolean(context, value):
        _log("JSValueRef.$f(%s, %s)", (context, value))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueMakeBoolean(context, value)

    #----------------------------------------------------------------
    @staticmethod
    def makeNull(context):
        _log("JSValueRef.$f(%s)", (context,))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueMakeNull(context)

    #----------------------------------------------------------------
    @staticmethod
    def makeNumber(context, number):
        _log("JSValueRef.$f(%s, %s)", (context, number))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueMakeNumber(context, number)

    #----------------------------------------------------------------
    @staticmethod
    def makeString(context, string):
        _log("JSValueRef.$f(%s, %s)", (context, string))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"
        assert isinstance(string,  JSStringRef),  "Expecting a JSStringRef for the string parameter"

        return _JSValueMakeString(context, string)

    #----------------------------------------------------------------
    @staticmethod
    def makeUndefined(context):
        _log("JSValueRef.$f(%s)", (context,))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueMakeUndefined(context)

    #----------------------------------------------------------------
    def asJSObjectRef(self, context):
        _log("JSValueRef.$f(%s)", (self,))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"
        
        if isinstance(self, JSObjectRef): return self
        
        type = self.getType(context)
        
        if type != JSValueRef.kJSTypeObject:
            raise TypeError, "Unable to convert a non-object into a JSObjectRef (type was: %s)" % str(type)

        return ctypes.cast(self, JSObjectRef)
    
    #----------------------------------------------------------------
    def getType(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueGetType(context, self)
    
    #----------------------------------------------------------------
    def isBoolean(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueIsBoolean(context, self).value
    
    #----------------------------------------------------------------
    def isEqual(self, context, other):
        _log("JSValueRef.$f(%s, %s, %s)", (self, context, other))
        assert isinstance(context, JSContextRef),  "Expecting a JSContextRef for the context parameter"
        assert isinstance(other, JSValueRef),      "Expecting a JSValueRef for the other parameter"

        return _JSValueIsEqual(context, self, other, None)
    
    #----------------------------------------------------------------
    def isInstanceOf(self, context, constructor):
        _log("JSValueRef.$f(%s, %s, %s)", (self, context, constructor))
        assert isinstance(context,     JSContextRef), "Expecting a JSContextRef for the context parameter"
        assert isinstance(constructor, JSValueRef),   "Expecting a JSValueRef for the constructor parameter"
        
        return _JSValueIsInstanceOfConstructor(context, self, constructor, None)
    
    #----------------------------------------------------------------
    def isNull(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueIsNull(context, self)
    
    #----------------------------------------------------------------
    def isNumber(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueIsNumber(context, self)
    
    #----------------------------------------------------------------
    def isObject(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueIsObject(context, self)
    
    #----------------------------------------------------------------
    def isStrictEqual(self, context, other):
        _log("JSValueRef.$f(%s, %s, %s)", (self, context, other))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"
        assert isinstance(other,   JSValueRef),   "Expecting a JSValueRef for the other parameter"

        return _JSValueIsStrictEqual(context, self, other)
    
    #----------------------------------------------------------------
    def isString(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueIsString(context, self)
    
    #----------------------------------------------------------------
    def isUndefined(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueIsUndefined(context, self)
    
    #----------------------------------------------------------------
    def protect(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"
        
        _JSValueProtect(context, self)
    
    #----------------------------------------------------------------
    def toBoolean(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueToBoolean(context, self)
    
    #----------------------------------------------------------------
    def toNumber(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueToNumber(context, self, None)
    
    #----------------------------------------------------------------
    def toObject(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        result =_JSValueToObject(context, self, None)
        result.context = context
    
    #----------------------------------------------------------------
    def toStringRef(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueToStringCopy(context, self, None)
    
    #----------------------------------------------------------------
    def toString(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        ref = self.toStringRef(context)
        result = ref.toString()
        ref.release()
        
        return result
    
    #----------------------------------------------------------------
    def unprotect(self, context):
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        _JSValueUnprotect(context, self)

#--------------------------------------------------------------------
class JSObjectRef(JSValueRef):
    """Models the JSObjectRef type.
    
    <p>These methods call functions defined in 
    &[JSObjectRef.h][http://developer.apple.com/documentation/Carbon/Reference/WebKit_JavaScriptCore_Ref/JSObjectRef/index.html].
    
    <p>This class is a subclass of #[JSValueRef], and so all of it's
    methods are available to instances of this class.
    """

    kJSPropertyAttributeNone       = 0
    kJSPropertyAttributeReadOnly   = 1 << 1
    kJSPropertyAttributeDontEnum   = 1 << 2 
    kJSPropertyAttributeDontDelete = 1 << 3 

    #----------------------------------------------------------------
    def deleteProperty(self, context, propertyName):
        _log("JSObjectRef.$f(%s, %s, %s)", (self, context, propertyName))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"
        
        propertyNameRef = JSStringRef.asRef(propertyName)
        if not propertyNameRef: raise TypeError, "Expecting a string for the propertyName parameter"
        
        result = _JSObjectDeleteProperty(context, self, propertyNameRef, None)
        if propertyName != propertyNameRef: propertyNameRef.release()
        
        return result
        
    #----------------------------------------------------------------
    def getProperty(self, context, propertyName):
        _log("JSObjectRef.$f(%s, %s, %s)", (self, context, propertyName))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        propertyNameRef = JSStringRef.asRef(propertyName)
        if not propertyNameRef: raise TypeError, "Expecting a string for the propertyName parameter"
        
        result = _JSObjectGetProperty(context, self, propertyNameRef, None)
        if propertyName != propertyNameRef: propertyNameRef.release()
        
        result.context = context
        return result

    #----------------------------------------------------------------
    def getPropertyAtIndex(self, context, propertyIndex):
        _log("JSObjectRef.$f(%s, %s, %s)", (self, propertyIndex, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"
        assert isinstance(propertyIndex, int),    "Expecting an integer for the propertyIndex parameter"
        
        result = _JSObjectGetPropertyAtIndex(context, self, propertyIndex, None)
        result.context = context
        return result

    #----------------------------------------------------------------
    def getPropertyNames(self, context):
        _log("JSObjectRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"
        
        propertyNameArrayRef = _JSObjectCopyPropertyNames(context, self)
        _JSPropertyNameArrayRetain(propertyNameArrayRef)
        
        names = []
        
        count = _JSPropertyNameArrayGetCount(propertyNameArrayRef)
        for i in xrange(0, count):
            prop = _JSPropertyNameArrayGetNameAtIndex(propertyNameArrayRef, i)
            names.append(prop.toString())
        
        _JSPropertyNameArrayRelease(propertyNameArrayRef)
        
        return names

    #----------------------------------------------------------------
    def getPrototype(self, context):
        _log("JSObjectRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        result = _JSObjectGetPrototype(context, self)
        result.context = context
        return result

    #----------------------------------------------------------------
    def hasProperty(self, context, propertyName):
        _log("JSObjectRef.$f(%s, %s, %s)", (self, context, propertyName))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        propertyNameRef = JSStringRef.asRef(propertyName)
        if not propertyNameRef: raise TypeError, "Expecting a string for the propertyName parameter"
        
        result = _JSObjectHasProperty(context, self, propertyNameRef)
        if propertyName != propertyNameRef: propertyNameRef.release()
        
        return result

    #----------------------------------------------------------------
    def isConstructor(self, context):
        _log("JSObjectRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSObjectIsConstructor(context, self)

    #----------------------------------------------------------------
    def isFunction(self, context):
        _log("JSObjectRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSObjectIsFunction(context, self)

    #----------------------------------------------------------------
    def setProperty(self, context, propertyName, value, attributes=kJSPropertyAttributeNone):
        _log("JSObjectRef.$f(%s, %s, %s, %s, %s)", (self, context, propertyName, value, attributes))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        assert isinstance(context, JSContextRef),       "Expecting a JSContextRef for the context parameter"
        if value: assert isinstance(value, JSValueRef), "Expecting a JSValueRef for the value parameter"
        assert isinstance(attributes, int),             "Expecting an integer for the attributes parameter"
        
        propertyNameRef = JSStringRef.asRef(propertyName)
        if not propertyNameRef: raise TypeError, "Expecting a string for the propertyName parameter"
 
        _JSObjectSetProperty(context, self, propertyNameRef, value, attributes, None)

        if propertyName != propertyNameRef: propertyNameRef.release()

    #----------------------------------------------------------------
    def setPropertyAtIndex(self, context, propertyIndex, value):
        _log("JSObjectRef.$f(%s, %s, %s, %s)", (self, context, propertyIndex, value))
        assert isinstance(context, JSContextRef),       "Expecting a JSContextRef for the context parameter"
        assert isinstance(propertyIndex, int),          "Expecting an integer for the propertyIndex parameter"
        if value: assert isinstance(value, JSValueRef), "Expecting a JSValueRef for the value parameter"
        
        _JSObjectSetPropertyAtIndex(context, self, propertyIndex, value, None)

    #----------------------------------------------------------------
    def setPrototype(self, context, prototype):
        _log("JSObjectRef.$f(%s, %s, %s)", (self, context, prototype))
        assert isinstance(context, JSContextRef),               "Expecting a JSContextRef for the context parameter"
        if prototype: assert isinstance(prototype, JSValueRef), "Expecting a JSValueRef for the prototype parameter"

        _JSObjectSetPrototype(context, self, prototype)

#--------------------------------------------------------------------
class JSException(Exception):

    #----------------------------------------------------------------
    def __init__(self, value):
        self.value = value
        
    #----------------------------------------------------------------
    def __str__(self):
        return repr(self.value)
    
#-------------------------------------------------------------------
# simple typedefs
#-------------------------------------------------------------------

JSType               = ctypes.c_int
JSClassAttribute     = ctypes.c_int
JSPropertyAttribute  = ctypes.c_int
JSClassAttributes    = ctypes.c_uint
JSPropertyAttributes = ctypes.c_uint
JSChar               = ctypes.c_wchar

class JSPropertyNameAccumulatorRef(ctypes.c_void_p): pass
class JSClassRef(ctypes.c_void_p): pass
class JSPropertyNameArrayRef(ctypes.c_void_p): pass

#-------------------------------------------------------------------
# callback functions
#-------------------------------------------------------------------

#-------------------------------------------------------------------
JSObjectCallAsConstructorCallback = ctypes.CFUNCTYPE(
    JSObjectRef,                 # result
    JSContextRef,                # ctx
    JSObjectRef,                 # constructor
    ctypes.c_size_t,             # argumentCount,
    ctypes.POINTER(JSValueRef),  # arguments
    ctypes.POINTER(JSValueRef),  # exception
)

#-------------------------------------------------------------------
JSObjectCallAsFunctionCallback = ctypes.CFUNCTYPE(
    JSValueRef,                  # result
    JSContextRef,                # ctx,
    JSObjectRef,                 # function,
    JSObjectRef,                 # thisObject,
    ctypes.c_size_t,             # argumentCount,
    ctypes.POINTER(JSValueRef),  # arguments
    ctypes.POINTER(JSValueRef),  # exception
)

#-------------------------------------------------------------------
JSObjectConvertToTypeCallback = ctypes.CFUNCTYPE(
    JSValueRef,                 # result
    JSContextRef,               # ctx
    JSObjectRef,                # object
    JSType,                     # type
    ctypes.POINTER(JSValueRef), # exception
)

#-------------------------------------------------------------------
JSObjectDeletePropertyCallback = ctypes.CFUNCTYPE(
    ctypes.c_int,                # result - bool
    JSContextRef,               # ctx
    JSObjectRef,                # object
    JSStringRef,                # propertyName
    ctypes.POINTER(JSValueRef), # exception
)

#-------------------------------------------------------------------
JSObjectFinalizeCallback = ctypes.CFUNCTYPE(
    None,                 # result
    JSObjectRef,          # object
)

#-------------------------------------------------------------------
JSObjectGetPropertyCallback = ctypes.CFUNCTYPE(
    JSValueRef,                 # result
    JSContextRef,               # ctx
    JSObjectRef,                # object
    JSStringRef,                # propertyName
    ctypes.POINTER(JSValueRef), # exception
)

#-------------------------------------------------------------------
JSObjectGetPropertyNamesCallback = ctypes.CFUNCTYPE(
    None,                          # result
    JSContextRef,                 # ctx
    JSObjectRef,                  # object
    JSPropertyNameAccumulatorRef, # propertyNames
)

#-------------------------------------------------------------------
JSObjectHasInstanceCallback = ctypes.CFUNCTYPE(
    ctypes.c_int,                # result - bool
    JSContextRef,               # ctx
    JSObjectRef,                # constructor
    JSValueRef,                 # possibleInstance
    ctypes.POINTER(JSValueRef), # exception
)

#-------------------------------------------------------------------
JSObjectHasPropertyCallback = ctypes.CFUNCTYPE(
    ctypes.c_int,         # result - bool
    JSContextRef,        # ctx
    JSObjectRef,         # object
    JSStringRef,         # propertyName
)

#-------------------------------------------------------------------
JSObjectInitializeCallback = ctypes.CFUNCTYPE(
    None,          # result
    JSContextRef, # ctx
    JSObjectRef,  # object
)

#-------------------------------------------------------------------
JSObjectSetPropertyCallback = ctypes.CFUNCTYPE(
    ctypes.c_int,                # result - bool
    JSContextRef,               # ctx
    JSObjectRef,                # object
    JSStringRef,                # propertyName
    JSValueRef,                 # value
    ctypes.POINTER(JSValueRef), # exception
)

#-------------------------------------------------------------------
# structures
#-------------------------------------------------------------------

#-------------------------------------------------------------------
class JSStaticFunction(ctypes.Structure): pass
JSStaticFunction._fields_ = [
    ("name",           ctypes.c_char_p), 
    ("callAsFunction", JSObjectCallAsFunctionCallback),
    ("attributes",     JSPropertyAttributes),
]

#-------------------------------------------------------------------
class JSStaticValue(ctypes.Structure): pass
JSStaticValue._fields_ = [
    ("name",        ctypes.c_char_p), 
    ("getProperty", JSObjectGetPropertyCallback),
    ("setProperty", JSObjectSetPropertyCallback),
    ("attributes",  JSPropertyAttributes),
]

#-------------------------------------------------------------------
class JSClassDefinition(ctypes.Structure): pass
JSClassDefinition._fields_ = [
    ("version",           ctypes.c_int),
    ("attributes",        JSClassAttributes),
    ("className",         ctypes.c_char_p),
    ("parentClass",       JSClassRef),
    ("staticValues",      ctypes.POINTER(JSStaticValue)),
    ("staticFunctions",   ctypes.POINTER(JSStaticFunction)),
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

#--------------------------------------------------------------------
class JSLibrary:
    """Manages the native JavaScriptCore library
    
    You can set the $[libraryPath] and $[libraryName] class variables
    AFTER importing the module and BEFORE invoking any other
    code in the module.  If the $[libraryPath] variable is set,
    it overrides the $[libraryName] variable.

    <p>$[libraryName] holds the short name of the native JavaScriptCore library.
    
    <p>If this variable is set, but the $[libraryPath] variable is not
    set, the library will be searched for in the system via a
    system defined method.
    
    <p>The default value for $[libraryName] is $["JavaScriptCore"].

    <p>$[libraryPath] Holds the fully qualified name of the JavaScriptCore library.
    
    <p>If this variable is set, it overrides the $[libraryName] variable
    setting and is used as the complete name of the library.
    """

    libraryName = "JavaScriptCore"
    libraryPath = None
    _library    = None
    
    #----------------------------------------------------------------
    @staticmethod
    def getLibrary():
        """Return the JavaScriptCore library as a CDLL or equivalent.
        
        @return ctypes.CDLL
        The JavaScriptCore library in use.
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
# JSBase.h
#===================================================================

#-------------------------------------------------------------------
_defineFunction("JSCheckScriptSyntax", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSStringRef,                     "script"), 
    (JSStringRef,                     "sourceURL"), 
    (ctypes.c_int32,                  "startingLineNumber"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSEvaluateScript", JSValueRef, (
    (JSContextRef,                    "ctx"), 
    (JSStringRef,                     "script"), 
    (JSObjectRef,                     "thisObject"),
    (JSStringRef,                     "sourceURL"),
    (ctypes.c_int,                    "startingLineNumber"),
    (ctypes.POINTER(JSValueRef),      "exception"),
))

#-------------------------------------------------------------------
_defineFunction("JSGarbageCollect", None, (
    (JSContextRef,                    "ctx"), 
))

#===================================================================
# JSContextRef
#===================================================================

#-------------------------------------------------------------------
_defineFunction("JSContextGetGlobalObject", JSObjectRef, (
    (JSContextRef,                    "ctx"), 
))

#-------------------------------------------------------------------
_defineFunction("JSGlobalContextCreate", JSGlobalContextRef, (
    (JSClassRef,                      "globalObjectClass"), 
))

#-------------------------------------------------------------------
_defineFunction("JSGlobalContextRelease", None, (
    (JSGlobalContextRef,              "ctx"), 
))

#-------------------------------------------------------------------
_defineFunction("JSGlobalContextRetain", JSGlobalContextRef, (
    (JSGlobalContextRef,              "ctx"), 
))

#===================================================================
# JSObjectRef
#===================================================================

#-------------------------------------------------------------------
_defineFunction("JSClassCreate", JSClassRef, (
    (ctypes.POINTER(JSClassDefinition), "definition"), 
))

#-------------------------------------------------------------------
_defineFunction("JSClassRelease", None, (
    (JSClassRef,                      "jsClass"), 
))

#-------------------------------------------------------------------
_defineFunction("JSClassRetain", None, (
    (JSClassRef,                      "jsClass"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectCallAsConstructor", JSObjectRef, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
    (ctypes.c_size_t,                 "argumentCount"), 
    (ctypes.POINTER(JSValueRef),      "arguments"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectCallAsFunction", JSValueRef, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
    (JSObjectRef,                     "thisObject"), 
    (ctypes.c_size_t,                 "argumentCount"), 
    (ctypes.POINTER(JSValueRef),      "arguments"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectCopyPropertyNames", JSPropertyNameArrayRef, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectDeleteProperty", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
    (JSStringRef,                     "propertyName"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectGetPrivate", ctypes.c_void_p, (
    (JSObjectRef,                     "object"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectGetProperty", JSValueRef, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
    (JSStringRef,                     "propertyName"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectGetPropertyAtIndex", JSValueRef, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
    (ctypes.c_uint,                   "propertyIndex"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectGetPrototype", JSValueRef, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectHasProperty", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
    (JSStringRef,                     "propertyName"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectIsConstructor", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectIsFunction", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectMake", JSObjectRef, (
    (JSContextRef,                    "ctx"), 
    (JSClassRef,                      "jsClass"), 
    (ctypes.c_void_p,                 "data"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectMakeConstructor", JSObjectRef, (
    (JSContextRef,                      "ctx"), 
    (JSClassRef,                        "jsClass"), 
    (JSObjectCallAsConstructorCallback, "callAsConstructor"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectMakeFunction", JSObjectRef, (
    (JSContextRef,                    "ctx"), 
    (JSStringRef,                     "name"), 
    (ctypes.c_uint,                   "parameterCount"), 
    (ctypes.POINTER(JSStringRef),     "parameterNames"), 
    (JSStringRef,                     "body"), 
    (JSStringRef,                     "sourceURL"), 
    (ctypes.c_int,                    "startingLineNumber"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectMakeFunctionWithCallback", JSObjectRef, (
    (JSContextRef,                    "ctx"), 
    (JSStringRef,                     "name"), 
    (JSObjectCallAsFunctionCallback,  "callAsFunction"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectSetPrivate", ctypes.c_int, (
    (JSObjectRef,                     "object"), 
    (ctypes.c_void_p,                 "data"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectSetProperty", None, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
    (JSStringRef,                     "propertyName"), 
    (JSValueRef,                      "value"), 
    (JSPropertyAttributes,            "attributes"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectSetPropertyAtIndex", None, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
    (ctypes.c_uint,                   "propertyIndex"), 
    (JSValueRef,                      "value"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSObjectSetPrototype", None, (
    (JSContextRef,                    "ctx"), 
    (JSObjectRef,                     "object"), 
    (JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSPropertyNameAccumulatorAddName", None, (
    (JSPropertyNameAccumulatorRef,    "accumulator"), 
    (JSStringRef,                     "propertyName"), 
))

#-------------------------------------------------------------------
_defineFunction("JSPropertyNameArrayGetCount", ctypes.c_size_t, (
    (JSPropertyNameArrayRef,          "array"), 
))

#-------------------------------------------------------------------
_defineFunction("JSPropertyNameArrayGetNameAtIndex", JSStringRef, (
    (JSPropertyNameArrayRef,          "array"), 
    (ctypes.c_size_t,                 "index"), 
))

#-------------------------------------------------------------------
_defineFunction("JSPropertyNameArrayRelease", None, (
    (JSPropertyNameArrayRef,          "array"), 
))

#-------------------------------------------------------------------
_defineFunction("JSPropertyNameArrayRetain", JSPropertyNameArrayRef, (
    (JSPropertyNameArrayRef,          "array"), 
))

#===================================================================
# JSStringRef
#===================================================================

#-------------------------------------------------------------------
_defineFunction("JSStringCreateWithCharacters", JSStringRef, (
    (ctypes.POINTER(JSChar),          "chars"), 
    (ctypes.c_size_t,                 "numChars"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringCreateWithUTF8CString", JSStringRef, (
    (ctypes.c_char_p,                  "string"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringGetCharactersPtr", ctypes.POINTER(JSChar), (
    (JSStringRef,                     "string"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringGetLength", ctypes.c_int32, (
    (JSStringRef,                     "string"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringGetMaximumUTF8CStringSize", ctypes.c_size_t, (
    (JSStringRef,                     "string"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringGetUTF8CString", ctypes.c_size_t, (
    (JSStringRef,                     "string"), 
    (ctypes.c_char_p,                 "buffer"), 
    (ctypes.c_size_t,                 "bufferSize"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringIsEqual", ctypes.c_int, (
    (JSStringRef,                     "a"), 
    (JSStringRef,                     "b"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringIsEqualToUTF8CString", ctypes.c_int, (
    (JSStringRef,                     "a"), 
    (ctypes.c_char_p,                 "b"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringRelease", None, (
    (JSStringRef,                     "string"), 
))

#-------------------------------------------------------------------
_defineFunction("JSStringRetain", JSStringRef, (
    (JSStringRef,                     "string"), 
))

#===================================================================
# JSValueRef
#===================================================================

#-------------------------------------------------------------------
_defineFunction("JSValueGetType", JSType, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsBoolean", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsEqual", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "a"), 
    (JSValueRef,                      "b"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsInstanceOfConstructor", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
    (JSObjectRef,                     "constructor"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsNull", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsNumber", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsObject", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsObjectOfClass", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
    (JSClassRef,                      "jsClass"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsStrictEqual", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "a"), 
    (JSValueRef,                      "b"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsString", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueIsUndefined", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueMakeBoolean", JSValueRef, (
    (JSContextRef,                    "ctx"), 
    (ctypes.c_int,                    "boolean"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueMakeNull", JSValueRef, (
    (JSContextRef,                    "ctx"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueMakeNumber", JSValueRef, (
    (JSContextRef,                    "ctx"), 
    (ctypes.c_double,                 "number"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueMakeString", JSValueRef, (
    (JSContextRef,                    "ctx"), 
    (JSStringRef,                     "string"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueMakeUndefined", JSValueRef, (
    (JSContextRef,                    "ctx"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueProtect", None, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueToBoolean", ctypes.c_int, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueToNumber", ctypes.c_double, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueToObject", JSObjectRef, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueToStringCopy", JSStringRef, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
    (ctypes.POINTER(JSValueRef),      "exception"), 
))

#-------------------------------------------------------------------
_defineFunction("JSValueUnprotect", None, (
    (JSContextRef,                    "ctx"), 
    (JSValueRef,                      "value"), 
))

#-------------------------------------------------------------------
# code for main entry point below
#-------------------------------------------------------------------

#-------------------------------------------------------------------
def _printHelp():
    program = os.path.basename(sys.argv[0])
    help = """
%(program)s %(version)s

%(program)s is a program which executes JavaScript code using JavaScriptCore.

Usage: %(program)s [OPTIONS] [SCRIPT [ARGUMENT ...]

SCRIPT is the name of a script file to run, and arguments are
arguments passed to the script(s) run.

OPTIONS
   -e script-source     JavaScript source to execute
   -f script-file       filename of JavaScript source to execute
   
The -e and -f options may be used multiple times, the scripts will be
executed in order.  If no script is specified, a REPL will be run.
You may use - as the file name, in which case input will be read from stdin.
""" % { "program": program, "version": __version__ }

    print help.strip()
    sys.exit(1)

#-------------------------------------------------------------------
class _ScriptString:
    
    def __init__(self, string):
        self.string   = string
        self.filename = "<literal>"
        
#-------------------------------------------------------------------
class _ScriptFile:
    
    def __init__(self, filename):
        self.filename = filename
        if (filename == "-"): 
            self.filename = "<stdin>"
            return
        
        ifile = open(filename)
        self.string = ifile.read()
        ifile.close()

#-------------------------------------------------------------------
def _parseArgs():
    scripts   = []
    arguments = []
    useRepl  = False

    args = sys.argv[1:]
    
    in_options = True
    
    while (len(args) > 0):
        arg = args.pop(0)
        
        if not in_options:
            arguments.append(arg)
            
        else:
            if arg in ("-?", "--?", "-h", "--h", "-help", "--help"):
                _printHelp()
                
            elif arg == "-e":
                source = args.pop(0)
                scripts.append(_ScriptString(source))
            
            elif arg == "-f":
                source = args.pop(0)
                
                if source == "-":
                    useRepl = True
                else:
                    scripts.append(_ScriptFile(source))
            
            else:
                in_options = False
                scripts.append(_ScriptFile(arg))
            
    return (scripts, arguments, useRepl)

#-------------------------------------------------------------------------------
def _callbackPrint(context, function, thisObject, args):
#    if True: return
    _log("$f(%s, %s, %s, %s)", (context, function, thisObject, args))

    line = ""
    
    for valueRef in args:
        string = valueRef.toString(context)
        _log("$f() valueRef.toString(%s): '%s'", (context, string))
        line   = line + string
        
    print line
    _log("$f() <-")
    
    return JSValueRef.makeUndefined(context)

#-------------------------------------------------------------------------------
def _handleJSException(e, context):

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
    
#-------------------------------------------------------------------------------
def _main():

    #---------------------------------------------------------------
    # parse arguments
    #---------------------------------------------------------------
    (scripts, arguments, useRepl) = _parseArgs()
    
    if len(scripts) == 0: 
        useRepl = True
    
    #---------------------------------------------------------------
    # start processing        
    #---------------------------------------------------------------
    context = JSGlobalContextRef.create()
    
    globalObject = context.getGlobalObject()
    globalObject.protect(context)
    
    #---------------------------------------------------------------
    # add builtins
    #---------------------------------------------------------------
    function = context.makeFunction(None, _callbackPrint)
    globalObject.setProperty(context, "print", function)
    
    #---------------------------------------------------------------
    # add arguments
    #---------------------------------------------------------------
    jsArgs = context.eval("[]").asJSObjectRef(context)
    jsArgs.protect(context)
    
    if len(scripts) > 0:
        executable = scripts[-1].filename
    else:
        executable = "<stdin>"
        
    val = JSStringRef.create(executable)
    jsArgs.setPropertyAtIndex(context, 0, JSValueRef.makeString(context,val))
    val.release()
    
    for i, argument in enumerate(arguments):
        val = JSStringRef.create(argument)
        jsArgs.setPropertyAtIndex(context, i+1, JSValueRef.makeString(context,val))
        val.release()
        
    globalObject.setProperty(context, "arguments", jsArgs)
    jsArgs.unprotect(context)
    
    #---------------------------------------------------------------
    # add environment
    #---------------------------------------------------------------
    jsEnv = context.eval("({})").asJSObjectRef(context)
    jsEnv.protect(context)

    for key, val in os.environ.iteritems():
        val = JSStringRef.create(val)
        jsEnv.setProperty(context, key, JSValueRef.makeString(context,val))
        val.release()
    
    globalObject.setProperty(context, "environment", jsEnv)
    jsEnv.unprotect(context)
    
    #---------------------------------------------------------------
    # run scripts
    #---------------------------------------------------------------
    for script in scripts:
        try:
            result = context.eval(script.string, None, script.filename, 1)
        except JSException, e:
            _handleJSException(e, context)
            break
            
    #---------------------------------------------------------------
    # run repl
    #---------------------------------------------------------------
    if useRepl:
        
        program = os.path.basename(sys.argv[0])
        print "%s %s" % (program, __version__)
        
        while True:
            sys.stdout.write(">>> ")
            line = sys.stdin.readline()
            if line == "": break
            
            line = line.strip()
            if line:
                try:
                    result = context.eval(line, None, "<repl>", 1)
                    
                    if not result.isUndefined(context):
                        resultStr = result.toString(context)
                        print resultStr
                except JSException, e:
                    _handleJSException(e, context)
            
    globalObject.unprotect(context)
    context.release()

#-------------------------------------------------------------------
if __name__ == '__main__':
    import os
    import sys
    
    NitroLogging(not True)
    _main()    
