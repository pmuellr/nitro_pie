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
__date__    = "2009-05-06"
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

#--------------------------------------------------------------------
class RememberedObjects(object):

    index      = 1
    remembered = {}
    
    #----------------------------------------------------------------
    @staticmethod
    def remember(obj, finalizer=None):
        remembered[index] = (obj, finalizer)
        
        result  = index
        index  += 1
        return result
        
    #----------------------------------------------------------------
    @staticmethod
    def get(index):
        return remembered[index][0]
        
    #----------------------------------------------------------------
    @staticmethod
    def forget(index):
        (obj, finalizer) = remembered[index]

        del remembered[index]
        
        if finalizer:
            finalizer(obj)
    

#--------------------------------------------------------------------
class JSContextRef(ctypes.c_void_p):
    """Models the JSContextRef type.
    
    <p>These methods call functions defined in 
    &[JSContextRef.h][http://developer.apple.com/documentation/Carbon/Reference/WebKit_JavaScriptCore_Ref/JSContextRef/index.html].
    
    <p>Instances of this class are not created directly; instead
    use the <strong>create()</strong> method of #[JSGlobalContextRef]
    class.
    
    """
    functions = []
    
    #----------------------------------------------------------------
    def getGlobalObject(self):
        """Returns the global object associated with a context.
        
        @returns (#[JSValueRef]) the global object associated with the context
        """
        JSLibrary._ensureLibrary()
        _log("JSContextRef.$f(%s)", (self,))
        result = _JSContextGetGlobalObject(self)
        return result
    
    #----------------------------------------------------------------
    def garbageCollect(self):
        """Runs the garbage collector.
        
        The garbage collector does *[need] to be run explicitly,
        but can be by invoking this method.
        """
        JSLibrary._ensureLibrary()
        _log("JSContextRef.$f(%s)", (self,))
        return _JSGarbageCollect(self)
    
    #----------------------------------------------------------------
    def eval(self, script, thisObject=None, sourceURL=None, startingLineNumber=1):
        """Evaluate a string of JavaScript code.
        
        @returns (#[JSValueRef]) 
                 the value of executing the script.
        
        @param script             (str | unicode | #[JSStringRef])
               the script to execute
        @param thisObject         (#[JSObjectRef])
               the object to act as $[this] when the script executes
        @param sourceURL          (str | unicode | #[JSStringRef])
               the name of the script
        @param startingLineNumber (int)
               the line of the source the script starts on
        
        @throws (#[JSException])  
                raised when a JavaScript exception occurs
                during the processing of the script
        """
        JSLibrary._ensureLibrary()
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
        """Check the syntax of a string of JavaScript code.
        
        @returns (boolean) 
                 whether the script is syntactically correct
        
        @param script             (str | unicode | #[JSStringRef])
               the script to check
        @param sourceURL          (str | unicode | #[JSStringRef])
               the name of the script
        @param startingLineNumber (int)
               the line of the source the script starts on
        
        @throws (#[JSException])  
                raised when a JavaScript exception occurs
                during the processing of the script
        """
        JSLibrary._ensureLibrary()
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
        """Creates a JavaScript function implemented in Python.

        <p>The third argument to the <code>makeFunction()</code> method
        is a Python callable, which should have the following signature:
        
<pre>
def callback_print(context, function, thisObject, args)
</pre>
        
        <p>The <code>context</code> parameter 
        (<code>JSContextRef</code>)
        is the context that the function was invoked within.
        The <code>function</code> parameter 
        (<code>JSObjectRef</code>)
        is the JavaScript function that is currently executing.
        The <code>thisObject</code> parameter 
        (<code>JSObjectRef</code>)
        is the <code>'this'</code> value for the invocation.
        The <code>args</code> parameter 
        (list of <code>JSValueRef</code>)
        is the array of parameters passed to the function.  
        
        <p>The function should return whatever value it needs to return
        as a <code>JSValueRef</code>.  Here's
        an example of a function which prints it's arguments:
        
<pre>
def callbackPrint(context, function, thisObject, args):
    line = ""
    
    for valueRef in args:
        string = valueRef.toString(context)
        line   = line + string
        
    print line
    
    return context.makeUndefined()
</pre>
        
        @return (#[JSObjectRef])
                the JavaScript function just created
        
        @param name (str | unicode | #[JSStringRef])
               the name of the function
        
        @param function (callable)
               the Python function that implements the JavaScript function
        """
        JSLibrary._ensureLibrary()
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
    
    #----------------------------------------------------------------
    def makeBoolean(self, value):
        """Creates a new JavaScript boolean value.
        
        @return (#[JSValueRef]) the value created
        @param value (boolean) the boolean value to create
        """
        JSLibrary._ensureLibrary()
        _log("JSContextRef.$f(%s, %s)", (self, value))

        return _JSValueMakeBoolean(self, value)

    #----------------------------------------------------------------
    def makeNull(self):
        """Creates a new JavaScript null value.
        
        @return (#[JSValueRef]) the value created
        """
        JSLibrary._ensureLibrary()
        _log("JSContextRef.$f(%s)", (self,))

        return _JSValueMakeNull(self)

    #----------------------------------------------------------------
    def makeNumber(self, number):
        """Creates a new JavaScript number value.
        
        @return (#[JSValueRef]) the value created
        @param number (int |float) the number value to create
        """
        JSLibrary._ensureLibrary()
        _log("JSContextRef.$f(%s, %s)", (self, number))

        return _JSValueMakeNumber(self, number)

    #----------------------------------------------------------------
    def makeString(self, string):
        """Creates a new JavaScript string value.
        
        @return (#[JSValueRef]) the value created
        @param string (#[JSStringRef]) the string value to create
        """
        JSLibrary._ensureLibrary()
        _log("JSContextRef.$f(%s, %s)", (self, string))
        assert isinstance(string,  JSStringRef),  "Expecting a JSStringRef for the string parameter"

        return _JSValueMakeString(self, string)

    #----------------------------------------------------------------
    def makeUndefined(self):
        """Creates a new JavaScript undefined value.
        
        @return (#[JSValueRef]) the value created
        """
        JSLibrary._ensureLibrary()
        _log("JSContextRef.$f(%s)", (self,))

        return _JSValueMakeUndefined(self)

    #----------------------------------------------------------------
    def makePythonObjectRef(self, pythonValue):
        """Creates a new JSObjectRef which holds a Python value.
        
        @return (#[JSValueRef]) the value created
        """
        JSLibrary._ensureLibrary()
        _log("JSContextRef.$f(%s)", (self,))

        return _JSValueMakeUndefined(self)

        #----------------------------------------------------------------
    def addBuiltins(self):
        """Adds the nitro_pie shell builtin functions to this context.
        """
        
        _register_builtins(self)
        
        return _JSValueMakeUndefined(self)
    
#--------------------------------------------------------------------
class JSGlobalContextRef(JSContextRef):
    """Models the JSGlobalContextRef type.

    <p>This class is a subclass of #[JSContextRef].
    
    <p>These methods call functions defined in 
    &[JSContextRef.h][http://developer.apple.com/documentation/Carbon/Reference/WebKit_JavaScriptCore_Ref/JSContextRef/index.html].
    """

    #----------------------------------------------------------------
    @staticmethod
    def create():
        """Create a new instance of this class.
        
        @return (#[JSGlobalContextRef]) the new instance
        """
        JSLibrary._ensureLibrary()
        _log("JSGlobalContextRef.$f()")
        return _JSGlobalContextCreate(None)
        
    #----------------------------------------------------------------
    def release(self):
        """Release this context
        """
        JSLibrary._ensureLibrary()
        _log("JSGlobalContextRef.$f(%s)", (str(self),))
        return _JSGlobalContextRelease(self)
    
    #----------------------------------------------------------------
    def retain(self):
        """Retain this context
        """
        JSLibrary._ensureLibrary()
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
        """Creates an instance of this class from a string.
        
        Slightly different from create, this function may 
        also be passed an instance of this class and it
        will then simply return that instance.  In this
        case, you will have to test yourself whether or
        not the reference was created, so you can 
        <code>release()</code> it later.
        
        @returns (#[JSStringRef])
                 the #[JSStringRef] created (or passed in)
                 
        @param string (str | unicode | #[JSStringRef])
               the object to convert to a #[JSStringRef]
        """
        JSLibrary._ensureLibrary()
        _log("JSStringRef.$f()")

        if not string: return string
        if isinstance(string, JSStringRef): return string
        
        return JSStringRef.create(string)

    #----------------------------------------------------------------
    @staticmethod
    def create(string):
        """Creates an instance of this class from a string.
        
        The caller is responsible for freeing this string
        with the #[release()] method when no longer needed.
        
        @returns (#[JSStringRef])
                 the #[JSStringRef] created
                 
        @param string (str | unicode)
               the object to convert to a #[JSStringRef]
        """
        JSLibrary._ensureLibrary()
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
        """Convert this object to a Python string.
        
        @returns (str)
                 always returns a UTF-8 encoding of the string
        """
        JSLibrary._ensureLibrary()
        _log("JSStringRef.$f(%s)", (self,))
        
        len    = _JSStringGetMaximumUTF8CStringSize(self) + 1
        result = ctypes.create_string_buffer(len)
    
        _JSStringGetUTF8CString(self, result, len)
        
        _log("JSStringRef.$f() -> '%s'", (result.value,))
        
        return result.value

    #----------------------------------------------------------------
    def retain(self):
        """Retain this instance.
        """
        JSLibrary._ensureLibrary()
        _log("JSStringRef.$f(%s)", (self,))
    
        _JSStringRetain(self)
        
    #----------------------------------------------------------------
    def release(self):
        """Retain this instance.
        """
        JSLibrary._ensureLibrary()
        _log("JSStringRef.$f(%s)", (self,))
        
        _JSStringRelease(self)

#--------------------------------------------------------------------
class JSValueRef(ctypes.c_void_p):
    """Models the JSValueRef type.
    
    <p>These methods call functions defined in 
    &[JSValueRef.h][http://developer.apple.com/documentation/Carbon/Reference/WebKit_JavaScriptCore_Ref/JSValueRef/index.html].
    
    This class also defines the following constants, returned
    from the $[getType()] method.
    <ul>
    <li><code>kJSTypeUndefined</code>
    <li><code>kJSTypeNull</code>
    <li><code>kJSTypeBoolean</code>
    <li><code>kJSTypeNumber</code>
    <li><code>kJSTypeString</code>
    <li><code>kJSTypeObject</code>
    </ul>
    """

    kJSTypeUndefined = 0
    kJSTypeNull      = 1
    kJSTypeBoolean   = 2
    kJSTypeNumber    = 3
    kJSTypeString    = 4
    kJSTypeObject    = 5 

    #----------------------------------------------------------------
    def asJSObjectRef(self, context):
        """Attempts to cast this object as a #[JSObjectRef].
        
        Many values returned from APIs in this module are typed
        as #[JSValueRef] (by <code>ctypes</code>), but are 
        actually #[JSObjectRef]
        instances.  This method will cast them to #[JSObjectRef] so
        you can use those methods on the object.
        
        Primitive values and strings cannot be recast.
        
        @param context (#[JSContextRef]) 
        @throws (TypeError)
                raised if the object cannot be recast.
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s)", (self,))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"
        
        if isinstance(self, JSObjectRef): return self
        
        type = self.getType(context)
        
        if type != JSValueRef.kJSTypeObject:
            raise TypeError, "Unable to convert a non-object into a JSObjectRef (type was: %s)" % str(type)

        return ctypes.cast(self, JSObjectRef)
    
    #----------------------------------------------------------------
    def getType(self, context):
        """Returns the type of the value.
        
        @returns (int) 
                 One of the <code>kJSType</code> constants defined in
                 this class.
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueGetType(context, self)
    
    #----------------------------------------------------------------
    def isBoolean(self, context):
        """Returns whether this value is a boolean.
        
        @returns (boolean) indicator
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueIsBoolean(context, self).value
    
    #----------------------------------------------------------------
    def isEqual(self, context, other):
        """Returns whether this value is equal to another value.
        
        @returns (boolean) indicator
        @param context (#[JSContextRef]) 
        @param other (#[JSValueRef]) 
               the value to compare against
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s, %s)", (self, context, other))
        assert isinstance(context, JSContextRef),  "Expecting a JSContextRef for the context parameter"
        assert isinstance(other, JSValueRef),      "Expecting a JSValueRef for the other parameter"

        return _JSValueIsEqual(context, self, other, None)
    
    #----------------------------------------------------------------
    def isInstanceOf(self, context, constructor):
        """Returns whether this value is an instance of a constructor.
        
        @param constructor (#[JSValueRef]) 
               the constructor to test against
        
        @returns (boolean) indicator
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s, %s)", (self, context, constructor))
        assert isinstance(context,     JSContextRef), "Expecting a JSContextRef for the context parameter"
        assert isinstance(constructor, JSValueRef),   "Expecting a JSValueRef for the constructor parameter"
        
        return _JSValueIsInstanceOfConstructor(context, self, constructor, None)
    
    #----------------------------------------------------------------
    def isNull(self, context):
        """Returns whether this value is null.
        
        @returns (boolean) indicator
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueIsNull(context, self)
    
    #----------------------------------------------------------------
    def isNumber(self, context):
        """Returns whether this value is a number.
        
        @returns (boolean) indicator
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueIsNumber(context, self)
    
    #----------------------------------------------------------------
    def isObject(self, context):
        """Returns whether this value is a non-primitive object.
        
        @returns (boolean) indicator
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueIsObject(context, self)
    
    #----------------------------------------------------------------
    def isStrictEqual(self, context, other):
        """Returns whether this value is strictly equal to another value.
        
        @returns (boolean) indicator
        @param context (#[JSContextRef]) 
        @param other (#[JSValueRef]) 
               the value to compare against
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s, %s)", (self, context, other))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"
        assert isinstance(other,   JSValueRef),   "Expecting a JSValueRef for the other parameter"

        return _JSValueIsStrictEqual(context, self, other)
    
    #----------------------------------------------------------------
    def isString(self, context):
        """Returns whether this value is a string.
        
        @returns (boolean) indicator
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueIsString(context, self)
    
    #----------------------------------------------------------------
    def isUndefined(self, context):
        """Returns whether this value is undefined.
        
        @returns (boolean) indicator
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueIsUndefined(context, self)
    
    #----------------------------------------------------------------
    def protect(self, context):
        """Protect this value from garbage collection.
        
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"
        
        _JSValueProtect(context, self)
    
    #----------------------------------------------------------------
    def toBoolean(self, context):
        """Convert this value to a boolean.
        
        @returns (boolean) the converted value
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueToBoolean(context, self)
    
    #----------------------------------------------------------------
    def toNumber(self, context):
        """Convert this value to a number.
        
        @returns (float) the converted value
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueToNumber(context, self, None)
    
    #----------------------------------------------------------------
    def toObject(self, context):
        """Convert this value to an object.
        
        @returns (#[JSObject]) the converted value
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        result =_JSValueToObject(context, self, None)
        result.context = context
    
    #----------------------------------------------------------------
    def toStringRef(self, context):
        """Convert this value to a JSStringRef.
        
        @returns (#[JSStringRef]) the converted value
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSValueToStringCopy(context, self, None)
    
    #----------------------------------------------------------------
    def toString(self, context):
        """Convert this value to a string.
        
        This method will temporarily create a #[JSStringRef]
        instance, convert that to a Python string, and then
        release that #[JSStringRef] instance.
        
        @returns (str) the converted value (utf-8 encoded string)
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSValueRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        ref = self.toStringRef(context)
        result = ref.toString()
        ref.release()
        
        return result
    
    #----------------------------------------------------------------
    def unprotect(self, context):
        """Remove the protect of this value from garbage collection.

        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
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
    
    <p>This class also defines the following constants, which can be
    used in the $[setProperty()] method.
    
    <ul>
    <li><code>kJSPropertyAttributeNone</code>
    <li><code>kJSPropertyAttributeReadOnly</code>
    <li><code>kJSPropertyAttributeDontEnum</code>
    <li><code>kJSPropertyAttributeDontDelete</code>
    </ul>
    """

    kJSPropertyAttributeNone       = 0
    kJSPropertyAttributeReadOnly   = 1 << 1
    kJSPropertyAttributeDontEnum   = 1 << 2 
    kJSPropertyAttributeDontDelete = 1 << 3 

    #----------------------------------------------------------------
    def deleteProperty(self, context, propertyName):
        """Delete the property of an object.
        
        @returns (boolean) indicator of success
        @param context      (#[JSContextRef]) 
        @param propertyName (str | unicode | #[JSStringRef])
        """
        JSLibrary._ensureLibrary()
        _log("JSObjectRef.$f(%s, %s, %s)", (self, context, propertyName))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"
        
        propertyNameRef = JSStringRef.asRef(propertyName)
        if not propertyNameRef: raise TypeError, "Expecting a string for the propertyName parameter"
        
        result = _JSObjectDeleteProperty(context, self, propertyNameRef, None)
        if propertyName != propertyNameRef: propertyNameRef.release()
        
        return result
        
    #----------------------------------------------------------------
    def getProperty(self, context, propertyName):
        """Return the property of an object.
        
        @returns (#[JSValueRef]) value of the property
        @param context      (#[JSContextRef]) 
        @param propertyName (str | unicode | #[JSStringRef])
        """
        JSLibrary._ensureLibrary()
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
        """Return the property of an array.
        
        @returns (#[JSValueRef]) value of the property
        @param context       (#[JSContextRef]) 
        @param propertyIndex (int)
        """
        JSLibrary._ensureLibrary()
        _log("JSObjectRef.$f(%s, %s, %s)", (self, propertyIndex, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"
        assert isinstance(propertyIndex, int),    "Expecting an integer for the propertyIndex parameter"
        
        result = _JSObjectGetPropertyAtIndex(context, self, propertyIndex, None)
        result.context = context
        return result

    #----------------------------------------------------------------
    def getPropertyNames(self, context):
        """Return the names of the properties of the object
        
        @param context (#[JSContextRef]) 
        @returns (list of str) the names of the properties of the object
        """
        JSLibrary._ensureLibrary()
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
        """Return the prototype of the object
        
        @returns (#[JSValueRef]) the prototype of the object
        @param context (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSObjectRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        result = _JSObjectGetPrototype(context, self)
        result.context = context
        return result

    #----------------------------------------------------------------
    def hasProperty(self, context, propertyName):
        """Return whether the object contains the specified property.
        
        @returns (boolean) indicator
        @param context      (#[JSContextRef]) 
        @param propertyName (str | unicode | #[JSStringRef])
        """
        JSLibrary._ensureLibrary()
        _log("JSObjectRef.$f(%s, %s, %s)", (self, context, propertyName))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        propertyNameRef = JSStringRef.asRef(propertyName)
        if not propertyNameRef: raise TypeError, "Expecting a string for the propertyName parameter"
        
        result = _JSObjectHasProperty(context, self, propertyNameRef)
        if propertyName != propertyNameRef: propertyNameRef.release()
        
        return result

    #----------------------------------------------------------------
    def isConstructor(self, context):
        """Return whether the object is a constructor.
        
        @returns (boolean) indicator
        @param context      (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSObjectRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSObjectIsConstructor(context, self)

    #----------------------------------------------------------------
    def isFunction(self, context):
        """Return whether the object is a function.
        
        @returns (boolean) indicator
        @param context      (#[JSContextRef]) 
        """
        JSLibrary._ensureLibrary()
        _log("JSObjectRef.$f(%s, %s)", (self, context))
        assert isinstance(context, JSContextRef), "Expecting a JSContextRef for the context parameter"

        return _JSObjectIsFunction(context, self)

    #----------------------------------------------------------------
    def setProperty(self, context, propertyName, value, attributes=kJSPropertyAttributeNone):
        """Set the property of an object.
        
        @param context      (#[JSContextRef]) 
        @param propertyName (str | unicode | #[JSStringRef])
        @param value        (#[JSValueRef])
        @param attributes   (int) 
                            one of the kJSPropertyAttribute defined by this class
        """
        JSLibrary._ensureLibrary()
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
        """Set the property of an array.
        
        @param context       (#[JSContextRef]) 
        @param propertyIndex (int)
        @param value         (#[JSValueRef])
        """
        JSLibrary._ensureLibrary()
        _log("JSObjectRef.$f(%s, %s, %s, %s)", (self, context, propertyIndex, value))
        assert isinstance(context, JSContextRef),       "Expecting a JSContextRef for the context parameter"
        assert isinstance(propertyIndex, int),          "Expecting an integer for the propertyIndex parameter"
        if value: assert isinstance(value, JSValueRef), "Expecting a JSValueRef for the value parameter"
        
        _JSObjectSetPropertyAtIndex(context, self, propertyIndex, value, None)

    #----------------------------------------------------------------
    def setPrototype(self, context, prototype):
        """Set the prototype of an object.
        
        @param context   (#[JSContextRef]) 
        @param prototype (#[JSValueRef])
        """
        JSLibrary._ensureLibrary()
        _log("JSObjectRef.$f(%s, %s, %s)", (self, context, prototype))
        assert isinstance(context, JSContextRef),               "Expecting a JSContextRef for the context parameter"
        if prototype: assert isinstance(prototype, JSValueRef), "Expecting a JSValueRef for the prototype parameter"

        _JSObjectSetPrototype(context, self, prototype)

#--------------------------------------------------------------------
class JSException(Exception):
    """Contains a JavaScript execution.
    
    This exception will be raised in cases where a JavaScript runtime
    occurs.  The $[value] property will contain the value thrown from
    JavaScript, typed as a #[JSValueRef].
    """

    #----------------------------------------------------------------
    def __init__(self, value):
        """Creates a new instance of this class.  
        
        Not intended to be called directly.
        """
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
    """Manages the native JavaScriptCore library.
    
    <p>You can set the $[libraryPath] and $[libraryName] class variables
    AFTER importing the module and BEFORE invoking any other
    code in the module.  If the $[libraryPath] variable is set,
    it overrides the $[libraryName] variable.

    <p>$[libraryName] holds the short name of the native JavaScriptCore library.
    
    <p>If this variable is set, but the $[libraryPath] variable is not
    set, the library will be searched for in the system via a
    system defined method.
    
    <p>The default value for $[libraryName] is $["JavaScriptCore"].

    <p>$[libraryPath] holds the fully qualified name of the JavaScriptCore library.
    
    <p>If this variable is set, it overrides the $[libraryName] variable
    setting and is used as the complete name of the library.
    """

    libraryName = "JavaScriptCore"
    libraryPath = None
    _library    = None

    #----------------------------------------------------------------
    @staticmethod
    def _ensureLibrary():
        if JSLibrary._library: return
        
        JSLibrary.getLibrary()
        JSLibrary._loadLibrary()
    
    #----------------------------------------------------------------
    @staticmethod
    def getLibrary():
        """Return the JavaScriptCore library as a CDLL or equivalent.
        
        @return (ctypes.CDLL) the JavaScriptCore library in use
        @throws (Exception) when the library cannot be loaded
        """

        if JSLibrary._library: return JSLibrary._library
        
        if not JSLibrary.libraryPath:
            JSLibrary.libraryPath = ctypes.util.find_library(JSLibrary.libraryName)
            
        if not JSLibrary.libraryPath:
            raise Exception, "unable to find the JavaScriptCore library"
            
        JSLibrary._library = ctypes.CDLL(JSLibrary.libraryPath)
        return JSLibrary._library

    #-------------------------------------------------------------------
    @staticmethod
    def _defineFunction(name, resType, parms):
        """define a function named 'name'
        
        parms should be a sequence of sequences of:
        
        (type, flags, name, defaultValue)
        
        per the ctypes conventions
        """
        
        types      = [ptype      for ptype, pname in parms]
        paramFlags = [(1, pname) for ptype, pname in parms]
        
        prototype = ctypes.CFUNCTYPE(resType, *types)
        function  = prototype((name, JSLibrary._library), tuple(paramFlags))
        
        globals()["_" + name] = function

    #----------------------------------------------------------------
    @staticmethod
    def _loadLibrary():

        #===================================================================
        # JSBase.h
        #===================================================================
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSCheckScriptSyntax", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSStringRef,                     "script"), 
            (JSStringRef,                     "sourceURL"), 
            (ctypes.c_int32,                  "startingLineNumber"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSEvaluateScript", JSValueRef, (
            (JSContextRef,                    "ctx"), 
            (JSStringRef,                     "script"), 
            (JSObjectRef,                     "thisObject"),
            (JSStringRef,                     "sourceURL"),
            (ctypes.c_int,                    "startingLineNumber"),
            (ctypes.POINTER(JSValueRef),      "exception"),
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSGarbageCollect", None, (
            (JSContextRef,                    "ctx"), 
        ))
        
        #===================================================================
        # JSContextRef
        #===================================================================
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSContextGetGlobalObject", JSObjectRef, (
            (JSContextRef,                    "ctx"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSGlobalContextCreate", JSGlobalContextRef, (
            (JSClassRef,                      "globalObjectClass"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSGlobalContextRelease", None, (
            (JSGlobalContextRef,              "ctx"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSGlobalContextRetain", JSGlobalContextRef, (
            (JSGlobalContextRef,              "ctx"), 
        ))
        
        #===================================================================
        # JSObjectRef
        #===================================================================
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSClassCreate", JSClassRef, (
            (ctypes.POINTER(JSClassDefinition), "definition"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSClassRelease", None, (
            (JSClassRef,                      "jsClass"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSClassRetain", None, (
            (JSClassRef,                      "jsClass"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectCallAsConstructor", JSObjectRef, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
            (ctypes.c_size_t,                 "argumentCount"), 
            (ctypes.POINTER(JSValueRef),      "arguments"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectCallAsFunction", JSValueRef, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
            (JSObjectRef,                     "thisObject"), 
            (ctypes.c_size_t,                 "argumentCount"), 
            (ctypes.POINTER(JSValueRef),      "arguments"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectCopyPropertyNames", JSPropertyNameArrayRef, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectDeleteProperty", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
            (JSStringRef,                     "propertyName"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectGetPrivate", ctypes.c_void_p, (
            (JSObjectRef,                     "object"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectGetProperty", JSValueRef, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
            (JSStringRef,                     "propertyName"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectGetPropertyAtIndex", JSValueRef, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
            (ctypes.c_uint,                   "propertyIndex"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectGetPrototype", JSValueRef, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectHasProperty", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
            (JSStringRef,                     "propertyName"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectIsConstructor", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectIsFunction", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectMake", JSObjectRef, (
            (JSContextRef,                    "ctx"), 
            (JSClassRef,                      "jsClass"), 
            (ctypes.c_void_p,                 "data"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectMakeConstructor", JSObjectRef, (
            (JSContextRef,                      "ctx"), 
            (JSClassRef,                        "jsClass"), 
            (JSObjectCallAsConstructorCallback, "callAsConstructor"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectMakeFunction", JSObjectRef, (
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
        JSLibrary._defineFunction("JSObjectMakeFunctionWithCallback", JSObjectRef, (
            (JSContextRef,                    "ctx"), 
            (JSStringRef,                     "name"), 
            (JSObjectCallAsFunctionCallback,  "callAsFunction"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectSetPrivate", ctypes.c_int, (
            (JSObjectRef,                     "object"), 
            (ctypes.c_void_p,                 "data"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectSetProperty", None, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
            (JSStringRef,                     "propertyName"), 
            (JSValueRef,                      "value"), 
            (JSPropertyAttributes,            "attributes"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectSetPropertyAtIndex", None, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
            (ctypes.c_uint,                   "propertyIndex"), 
            (JSValueRef,                      "value"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSObjectSetPrototype", None, (
            (JSContextRef,                    "ctx"), 
            (JSObjectRef,                     "object"), 
            (JSValueRef,                      "value"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSPropertyNameAccumulatorAddName", None, (
            (JSPropertyNameAccumulatorRef,    "accumulator"), 
            (JSStringRef,                     "propertyName"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSPropertyNameArrayGetCount", ctypes.c_size_t, (
            (JSPropertyNameArrayRef,          "array"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSPropertyNameArrayGetNameAtIndex", JSStringRef, (
            (JSPropertyNameArrayRef,          "array"), 
            (ctypes.c_size_t,                 "index"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSPropertyNameArrayRelease", None, (
            (JSPropertyNameArrayRef,          "array"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSPropertyNameArrayRetain", JSPropertyNameArrayRef, (
            (JSPropertyNameArrayRef,          "array"), 
        ))
        
        #===================================================================
        # JSStringRef
        #===================================================================
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSStringCreateWithCharacters", JSStringRef, (
            (ctypes.POINTER(JSChar),          "chars"), 
            (ctypes.c_size_t,                 "numChars"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSStringCreateWithUTF8CString", JSStringRef, (
            (ctypes.c_char_p,                  "string"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSStringGetCharactersPtr", ctypes.POINTER(JSChar), (
            (JSStringRef,                     "string"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSStringGetLength", ctypes.c_int32, (
            (JSStringRef,                     "string"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSStringGetMaximumUTF8CStringSize", ctypes.c_size_t, (
            (JSStringRef,                     "string"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSStringGetUTF8CString", ctypes.c_size_t, (
            (JSStringRef,                     "string"), 
            (ctypes.c_char_p,                 "buffer"), 
            (ctypes.c_size_t,                 "bufferSize"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSStringIsEqual", ctypes.c_int, (
            (JSStringRef,                     "a"), 
            (JSStringRef,                     "b"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSStringIsEqualToUTF8CString", ctypes.c_int, (
            (JSStringRef,                     "a"), 
            (ctypes.c_char_p,                 "b"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSStringRelease", None, (
            (JSStringRef,                     "string"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSStringRetain", JSStringRef, (
            (JSStringRef,                     "string"), 
        ))
        
        #===================================================================
        # JSValueRef
        #===================================================================
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueGetType", JSType, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueIsBoolean", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueIsEqual", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "a"), 
            (JSValueRef,                      "b"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueIsInstanceOfConstructor", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
            (JSObjectRef,                     "constructor"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueIsNull", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueIsNumber", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueIsObject", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueIsObjectOfClass", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
            (JSClassRef,                      "jsClass"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueIsStrictEqual", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "a"), 
            (JSValueRef,                      "b"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueIsString", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueIsUndefined", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueMakeBoolean", JSValueRef, (
            (JSContextRef,                    "ctx"), 
            (ctypes.c_int,                    "boolean"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueMakeNull", JSValueRef, (
            (JSContextRef,                    "ctx"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueMakeNumber", JSValueRef, (
            (JSContextRef,                    "ctx"), 
            (ctypes.c_double,                 "number"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueMakeString", JSValueRef, (
            (JSContextRef,                    "ctx"), 
            (JSStringRef,                     "string"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueMakeUndefined", JSValueRef, (
            (JSContextRef,                    "ctx"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueProtect", None, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueToBoolean", ctypes.c_int, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueToNumber", ctypes.c_double, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueToObject", JSObjectRef, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueToStringCopy", JSStringRef, (
            (JSContextRef,                    "ctx"), 
            (JSValueRef,                      "value"), 
            (ctypes.POINTER(JSValueRef),      "exception"), 
        ))
        
        #-------------------------------------------------------------------
        JSLibrary._defineFunction("JSValueUnprotect", None, (
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

One additional function is available in the context which is created.
The print() function takes any number of arguments, concatenates them,
and prints them to stdout.
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
            self.string   = None
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
def _jsfunc_print(context, function, thisObject, args):
    print "".join([arg.toString(context) for arg in args])
    
    return context.makeUndefined()

#-------------------------------------------------------------------------------
def _jsfunc_python_exec(context, function, thisObject, args):

    undefined = context.makeUndefined()
    
    if len(args) == 0: return undefined

    ifile = args[0].toString(context)
    
    execfile(ifile, globals(), { "context" : context })
    
    return undefined


#-------------------------------------------------------------------------------
require_modules = {}

def _jsfunc_require(context, function, thisObject, args):
    undefined = context.makeUndefined()

    if len(args) == 0: return undefined

    modFileName = args[0].toString(context)
    if not os.path.exists(modFileName): 
        print "Unabled to load module '%s': not found" % modFileName
        return undefined

    modFile = open(modFileName)
    modFileContents = modFile.read()
    modFile.close()
    
    if modFileName in require_modules:
        return require_modules[modFileName]
        
    module = context.eval("({})")
    require_modules[modFileName] = module
    
    modContext = JSGlobalContextRef.create()
    modGlobal  = modContext.getGlobalObject()
    modGlobal.protect(modContext)
    
    modGlobal.setProperty(modContext, "exports", module)
    
    _register_builtins(modContext)
    
    modContext.eval(modFileContents, None, modFileName)
    
    return module


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
def _register_builtins(context):
    globalObject = context.getGlobalObject()
    globalObject.protect(context)
    
    function = context.makeFunction(  "print", _jsfunc_print)
    globalObject.setProperty(context, "print", function)
    
    function = context.makeFunction(  "python_exec", _jsfunc_python_exec)
    globalObject.setProperty(context, "python_exec", function)
    
    function = context.makeFunction(  "require", _jsfunc_require)
    globalObject.setProperty(context, "require", function)

    globalObject.unprotect(context)
    
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
    
    #---------------------------------------------------------------
    # add builtins
    #---------------------------------------------------------------
    _register_builtins(context)
    
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
    jsArgs.setPropertyAtIndex(context, 0, context.makeString(val))
    val.release()
    
    for i, argument in enumerate(arguments):
        val = JSStringRef.create(argument)
        jsArgs.setPropertyAtIndex(context, i+1, context.makeString(val))
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
        jsEnv.setProperty(context, key, context.makeString(val))
        val.release()
    
    globalObject.setProperty(context, "environment", jsEnv)
    jsEnv.unprotect(context)
    
    #---------------------------------------------------------------
    # run scripts
    #---------------------------------------------------------------
    for script in scripts:
        if not script.string:
            useRepl = True
        else:
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
