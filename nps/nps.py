#!/usr/bin/env python

import os
import sys

#-------------------------------------------------------------------------------
def callback_print(context, function, thisObject, args):
    line = ""
    
    for arg in args:
        if JSObject.isJSObject(arg):
            printable = arg.toString()
        else:
            printable = str(arg)
    
        line = line + printable
        
    print line
    
#-------------------------------------------------------------------------------

lib_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "../lib"))
if lib_path not in sys.path: sys.path.insert(0, lib_path)

from nitro_pie import *

if len(sys.argv) < 2:
    print "Excepting the name of a script to run"
    sys.exit(1)
    
script_file_name = sys.argv[1]
script_file = open(script_file_name)
script      = script_file.read()
script_file.close()
    
context = JSContext()

globalObject = context.getGlobalObject()

function = context.makeFunctionWithCallback("print", callback_print)
globalObject.setProperty("print", function)

try:
    globalObject = context.getGlobalObject()
    globalObject = None
    result       = context.eval(script, globalObject, script_file_name, 1)
    
except JSException, e:
    e = e.value
    
    name      = e.getProperty("name")      if e.hasProperty("name")      else ""
    message   = e.getProperty("message")   if e.hasProperty("message")   else "???"
    sourceURL = e.getProperty("sourceURL") if e.hasProperty("sourceURL") else "???"
    line      = e.getProperty("line")      if e.hasProperty("line")      else -1

    print "Exception thrown: %s: %s: at %s[%d]" % (name, message, sourceURL, line)

    props = e.getPropertyNames()
    known_props = "name message sourceURL line".split()
    for prop in props:
        if prop in known_props: continue
        print "   %s: %s" % (prop, e.getProperty(prop))
    print
        
context.release()
