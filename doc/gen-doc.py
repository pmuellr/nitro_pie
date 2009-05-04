#!/usr/bin/env python

import os
import sys
import inspect

lib_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "../lib"))
if lib_path not in sys.path: sys.path.insert(0, lib_path)

import nitro_pie

#--------------------------------------------------------------------
def docFirstLine(function):
    if None == function.__doc__: return "no documentation available"
    
    return function.__doc__.split("\n")[0]

#--------------------------------------------------------------------
def docFull(function):
    if None == function.__doc__: return "no documentation available"
    
    return function.__doc__

#--------------------------------------------------------------------
def getStaticMethods(cls):
    result = []
    
    for propName in dir(cls):
        prop = getattr(cls, propName)
        
        if inspect.isfunction(prop): 
            result.append(prop)
    
    return result

#--------------------------------------------------------------------
def getMethods(cls):
    result = []
    
    for propName in dir(cls):
        prop = getattr(cls, propName)
        
        if inspect.ismethod(prop): 
            result.append(prop)
    
    return result

#--------------------------------------------------------------------
def argString(name, function):
    args = inspect.getargspec(function)[0]
    
    if inspect.ismethod(function):
        args = args[1:]
        
    result = "%s(" % name
    for i, arg in enumerate(args):
        if i == len(args) - 1:
            formatString = "%s%s"
        else:
            formatString = "%s%s, "
        result = formatString % (result, arg)
        
    result = "%s)" % result
    
    return result

#--------------------------------------------------------------------
def processPointerType(typeName):

    id = "api.%s" % typeName
    
    skipNames = ["from_param", "value", "functions"]

    type = getattr(nitro_pie, typeName)
    propNames = dir(type)
    propNames = [propName for propName in propNames if propName[0] != "_"]
    propNames = [propName for propName in propNames if propName not in skipNames]

    print "<!-- =========================================== -->"
    print "<h2><a name='%s'>%s</a></h2>" % (id, typeName)
    print "<div style='margin-left:2em'>"
    
#    print "<table cellpadding=3 cellspacing=0 frame=border border=1>"
    print "<table cellpadding=3 cellspacing=0"
    
    smethods = getStaticMethods(type)
    methods  = getMethods(type)
    
    if len(smethods) > 0:
        print "<tr><td colspan=2><em><strong style='font-size:120%'>Static Methods</strong></em></td></tr>"
        
        for method in smethods:
            name     = method.__name__
            id       = "api.%s.%s" % (typeName, name)
            doc      = docFirstLine(method)
            
            print "<tr><td><code style='margin-left:2em'><strong><a href='#%s'>%s</a></strong></code></td><td width=100%%>%s</td></tr>" % (id, name, doc)
            
    if len(methods) > 0:
        print "<tr><td colspan=2><em><strong style='font-size:120%'>Methods</strong></em></td></tr>"
        
        for method in methods:
            name     = method.__name__
            id       = "api.%s.%s" % (typeName, name)
            doc      = docFirstLine(method)
            
            print "<tr><td><code style='margin-left:2em'><strong><a href='#%s'>%s</a></strong></code></td><td width=100%%>%s</td></tr>" % (id, name, doc)
        
    print "</table>"
        
    for propName in propNames:
        prop = getattr(type, propName)
        if not callable(prop): continue

        doc      = docFull(prop)
        id       = "api.%s.%s" % (typeName, propName)
        propArgs = argString(propName, prop)
        print "<h3><code><a name='%s'>%s</a></code></h3>" % (id, propArgs)
        
        print "<div style='margin-left:2em'>"
        print doc
        print "</div>"
    
    print "</div>"
     
        
#--------------------------------------------------------------------
pointerTypes = """
JSGlobalContextRef
JSStringRef
JSValueRef
JSObjectRef
""".split()

print "<p>Classes"
print "<ul>"
for pointerType in pointerTypes:
    id = "api.%s" % pointerType
    print "<li><a href='#%s'>%s" % (id, pointerType)
print "</ul>"

for pointerType in pointerTypes:
    processPointerType(pointerType)


