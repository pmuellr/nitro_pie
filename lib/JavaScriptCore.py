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

from JavaScriptCoreRaw import JSC

#--------------------------------------------------------------------
# convert a string to a JSString
#--------------------------------------------------------------------
def string2jsString(string):
	if isinstance(string, str):
		return JSC.JSStringCreateWithUTF8CString(string)
	
	elif isinstance(string, unicode):
		return JSC.JSStringCreateWithUTF8CString(string.encode("utf-8"))
		
	else:
		raise TypeError, "expecting a string"

#--------------------------------------------------------------------
# convert a JSString to a string - always utf8
#--------------------------------------------------------------------
def jsString2string(jsString):
	len = JSC.JSStringGetMaximumUTF8CStringSize(jsString)
	
	result = c_char_p(" " * len)

	JSC.JSStringGetUTF8CString(jsString, result, len)
	
	return result.value


