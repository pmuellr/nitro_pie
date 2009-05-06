#!/usr/bin/env python

import os
import re
import sys
import inspect
import StringIO
import textwrap

lib_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "../lib"))
if lib_path not in sys.path: sys.path.insert(0, lib_path)

import nitro_pie

textile = False

#--------------------------------------------------------------------
_macro_patterns_html = (
    (re.compile(r"\&\[(.*?)\]\[(.*?)\]"), r"<a href='\2'>\1</a>"),
    (re.compile(r"\*\[(.*?)\]"),          r"<strong>\1</strong>"),
    (re.compile(r"\$\[(.*?)\]"),          r"<code>\1</code>"),
    (re.compile(r"\#\[(.*?)\]"),          r"<code><a href='#api.\1'>\1</a></code>"),
)

_macro_patterns_textile = (
    (re.compile(r"\&\[(.*?)\]\[(.*?)\]"), r"<a href='\2'>\1</a>"),
    (re.compile(r"\*\[(.*?)\]"),          r"<strong>\1</strong>"),
    (re.compile(r"\$\[(.*?)\]"),          r"<code>\1</code>"),
    (re.compile(r"\#\[(.*?)\]"),          r"\1"),
)

def expandMacros(string):

    macro_patterns = _macro_patterns_textile if textile else _macro_patterns_html

    for (pattern, repl) in macro_patterns:
        string = re.sub(pattern, repl, string)

    return string

#--------------------------------------------------------------------
class DocClass:

    def __init__(self, cls):
        self.cls = cls
        
        doc = cls.__doc__
        if doc:
            doc = expandMacros(doc)
            self.docOneLine = doc.split("\n")[0]
            self.docFull    = doc
        else:
            self.docOneLine = "<strong><span style='color:#F00'>No documentation available</span></strong>"
            self.docFull    = ""
            
        smethods = []
        cmethods = []
        imethods = []
            
        propNames = cls.__dict__.keys()
        propNames.sort()
        
        for propName in propNames:
            prop = getattr(cls, propName)
            
            if inspect.isfunction(prop):
                if prop.__name__[0] != "_":
                    smethods.append(prop)
                    
            if inspect.ismethod(prop):
                if prop.__name__[0] != "_":
                    imethods.append(prop)
                elif prop.__name__ == "__init__":
                    cmethods.append(prop)
                    
        self.smethods = [DocMethodStatic(cls,method)      for method in smethods]
        self.cmethods = [DocMethodConstructor(cls,method) for method in cmethods]
        self.imethods = [DocMethodInstance(cls,method)    for method in imethods]

    def getName(self):
        return self.cls.__name__
        
    def getDocOneLine(self):
        return self.docOneLine
        
    def getDocFull(self):
        return self.docFull
        
    def getLinkName(self):
        return "api.%s" % self.getName()

    def getStaticMethods(self):
        return self.smethods
        
    def getConstructors(self):
        return self.cmethods
        
    def getMethods(self):
        return self.imethods
        

#--------------------------------------------------------------------
class DocFunction(object):

    def __init__(self, cls, func):
        self.cls  = cls
        self.func = func
        
        self.name = func.__name__
        
        doc = func.__doc__
        if not doc:
            self.docOneLine = "<strong><span style='color:#F00'>No documentation available</span></strong>"
            self.docFull    = ""
            return
            
        doc = expandMacros(doc)
        self.docOneLine = doc.split("\n")[0]
        self.docFull    = doc
        
        doc = Doc(doc)
        self.docOneLine = doc.firstLine
        self.docFull    = doc.body

    def getName(self):
        return self.name
        
    def getPrintName(self):
        return self.getName()
        
    def getLinkName(self):
        return "api.%s.%s" % (self.cls.__name__, self.getName())

    def getDocOneLine(self):
        return self.docOneLine
        
    def getDocFull(self):
        return self.docFull
        
    def getArgNames(self):
        return inspect.getargspec(self.func)[0]

    def getSignature(self):
        args = self.getArgNames()
        dfts = inspect.getargspec(self.func)[3]
        
        if not dfts: dfts = []
            
        dfts = [str(dft) for dft in dfts]
        
        while len(dfts) < len(args):
            dfts.insert(0,"")
            
        result = "%s(" % self.getPrintName() 
        
        for i, arg in enumerate(args):
            dft = dfts[i]
            
            if dft:
                arg = "%s = %s" % (arg, dft)
            
            if i == len(args) - 1:
                formatString = "%s%s"
            else:
                formatString = "%s%s, "
            result = formatString % (result, arg)
            
        result = "%s)" % result
        
        return result

#--------------------------------------------------------------------
class DocMethodStatic(DocFunction):

    def __init(self, cls, func):
        DocFunction.__init__(self,cls,func)
        
#--------------------------------------------------------------------
class DocMethodInstance(DocFunction):

    def __init(self, cls, func):
        DocFunction.__init__(self,cls,func)

    def getArgNames(self):
        return super(DocMethodInstance, self).getArgNames()[1:]
        
#--------------------------------------------------------------------
class DocMethodConstructor(DocMethodInstance):

    def __init(self, cls, func):
        DocMethodInstance.__init__(self, cls, func)
        
        self.name = cls.__name__

    def getLinkName(self):
        return "api.%s.__init__" % (self.cls.__name__)

    def getPrintName(self):
        return self.cls.__name__

#--------------------------------------------------------------------
class Doc:

    def __init__(self, doc):
    
        self.doc       = textwrap.dedent(doc)
        self.firstLine = None
        self.body      = None
        
        self.parse()

    def parse(self):
        if not self.doc:
            self.firstLine = "<strong><span style='color:#F00'>No documentation available</span></strong>"
            self.body      = ""
            return
    
        body_pattern = re.compile(r"(.*?)\n(.*)", re.DOTALL)
        match = body_pattern.match(self.doc)
        
        if not match:
            self.firstLine = self.doc
            return
            
        self.firstLine = match.group(1)
        
        rest = match.group(2)
        
        section_pattern = re.compile(r"\n\s*?@")
        
        sections = section_pattern.split(rest)
        
        if not sections:
            self.body = "<p>%s" % self.firstLine
            
        self.body = sections[0]
        
        self.sections = sections[1:]
        
        returns = None
        parms   = []
        throws  = []

        pattern_return = re.compile(r"\w+\s*\((.*?)\)(.*)", re.DOTALL)
        pattern_parm   = re.compile(r"\w+\s*(\w+)\s*\((.*?)\)(.*)", re.DOTALL)
        pattern_throw  = re.compile(r"\w+\s*\((.*?)\)(.*)", re.DOTALL)
        
        for section in self.sections:
            sectionType = section.split()[0]
            
            if sectionType in ["return", "returns"]:
                match = pattern_return.match(section)
                if not match: continue
                
                type = match.group(1)
                desc = match.group(2)
                returns = "<strong><code>%s</code></strong> - %s" % (type, desc)
            
            elif sectionType in ["parm", "param", "arg"]:
                match = pattern_parm.match(section)
                if not match: continue
                
                name = match.group(1)
                type = match.group(2)
                desc = match.group(3)
                parm = "<strong><code>%s</code></strong> <tt>(%s)</tt><br>%s" % (name, type, desc)
                parms.append(parm)
            
            elif sectionType in ["throw", "throws"]:
                match = pattern_throw.match(section)
                if not match: continue
                
                type = match.group(1)
                desc = match.group(2)
                throw = "<strong><code>%s</code></strong> - %s" % (type, desc)
                throws.append(throw)
            
        if returns:
            self.body += "\n<p><strong>Returns:</strong>"
            self.body += "\n<ul>"
            self.body += "\n<li><p>" + returns
            self.body += "\n</ul>"
            
        if parms:
            self.body += "\n<p><strong>Parameters:</strong>"
            self.body += "\n<ul>"
            for parm in parms:
                self.body += "\n<li><p>" + parm
            self.body += "\n</ul>"
        
        if throws:
            self.body += "\n<p><strong>Raises:</strong>"
            self.body += "\n<ul>"
            for throw in throws:
                self.body += "\n<li><p>" + throw
            self.body += "\n</ul>"
        

#--------------------------------------------------------------------
def processMethods(apiFile, label, methods):

    if not len(methods): return

    print >>apiFile, "<hr>"
    print >>apiFile, "<h4>%s</h4>" % label
    print >>apiFile, "<div style='margin-left:4em'>"
    
    if False:
        print >>apiFile, "<table cellpadding=3 cellspacing=0>"
        
        for method in methods:
            name     = method.getPrintName()
            id       = method.getLinkName()
            doc      = method.getDocOneLine()
            
            print >>apiFile, "<tr><td><code style='margin-left:2em'><strong><a href='#%s'>%s</a></strong></code></td><td width=100%%>%s</td></tr>" % (id, name, doc)
    
        print >>apiFile, "</table>"
    
    for method in methods:
        name     = method.getSignature()
        id       = method.getLinkName()
        doc      = "%s<p>%s" % (method.getDocOneLine(), method.getDocFull())

        if textile:        
            print >>apiFile, "<p>*@%s@*" % (name)
        else:
            print >>apiFile, "<p><code><strong><a name='%s'>%s</a></strong></code>" % (id, name)
        print >>apiFile, "<div style='margin-left:4em'>"
        print >>apiFile, doc
        print >>apiFile, "</div>"

    print >>apiFile, "</div>"

#--------------------------------------------------------------------
def processDocClass(apiFile, docClass):

    name = docClass.getName()
    link = docClass.getLinkName()
    doc  = docClass.getDocFull()
    
    print >>apiFile, "<hr>"
    print >>apiFile, "<h3><a name='%s'>Class %s</a></h3>" % (link, name)
    print >>apiFile, "<div style='margin-left:2em'>"
    print >>apiFile, "<p>%s" % doc
    print >>apiFile, "<p>"

    processMethods(apiFile, "Static Methods", docClass.getStaticMethods())
    processMethods(apiFile, "Constructor",    docClass.getConstructors())
    processMethods(apiFile, "Methods",        docClass.getMethods())
    
    print >>apiFile, "</div>"
    print >>apiFile, ""

#--------------------------------------------------------------------
if len(sys.argv) > 1:
    if sys.argv[1] == "textile":
        textile = True

iFilename = "nitro_pie.tmpl.html"
oFilename = "nitro_pie.html"

classNames = """
JSLibrary
JSContextRef
JSGlobalContextRef
JSStringRef
JSValueRef
JSObjectRef
JSException
""".split()

apiFile = StringIO.StringIO()

if False:
    print >>apiFile, "<p>"
    print >>apiFile, "<table cellpadding=3 cellspacing=0>"
    
    for className in classNames:
        cls  = getattr(nitro_pie, className)
        id   = "api.%s" % className
        name = cls.__name__
        doc  = docFirstLine(cls)
        
        print >>apiFile, "<tr><td><code style='margin-left:2em'><strong><a href='#%s'>%s</a></strong></code></td><td width=100%%>%s</td></tr>" % (id, name, doc)
    
    print >>apiFile, "</table>"
    
    for className in classNames:
        processPointerType(apiFile, className)

docClasses = [DocClass(getattr(nitro_pie, className)) for className in classNames]

if not textile:
    print >>apiFile, "<h3>Classes</h3>"
    print >>apiFile, "<p>"
    print >>apiFile, "<table cellpadding=3 cellspacing=0>"
    
    for docClass in docClasses:
        name = docClass.getName()
        doc  = docClass.getDocOneLine()
        link = docClass.getLinkName()
        
        print >>apiFile, "<tr><td><code style='margin-left:2em'><strong><a href='#%s'>%s</a></strong></code></td><td width=100%%>%s</td></tr>" % (link, name, doc)
    
    print >>apiFile, "</table>"

for docClass in docClasses:
    processDocClass(apiFile, docClass)    

apiOut = apiFile.getvalue()
apiFile.close()

if textile:
    print apiOut
    sys.exit()
    
iFile = open(iFilename)
contents = iFile.read()
iFile.close()

warning = "<!-- warning: this file was automatically generated, do not edit it. -->\n\n"

warning = warning * 10

oFile = open(oFilename, "w")
oFile.write(warning)
oFile.write(contents.replace("%api_doc%", apiOut))
oFile.close()