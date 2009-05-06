#!/usr/bin/env python

#-------------------------------------------------------------------
# The MIT License
# 
# Copyright (c) 2009 Patrick Mueller
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#-------------------------------------------------------------------

import os
import sys
import subprocess

import unittest

shell = "../lib/nitro_pie.py"

#-------------------------------------------------------------------
class Test(unittest.TestCase):
    
    #---------------------------------------------------------------
    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    #---------------------------------------------------------------
    def test_option_e(self):
    
        args = [
            "python",
            shell,
            "-e",
            "print('Hello')",
            "-e",
            "print('World')",
        ]
        
        process = subprocess.Popen(args,stdout=subprocess.PIPE)
        
        (stdout, stderr) = process.communicate()
        
        self.assertEqual("Hello\nWorld\n", stdout)

    #---------------------------------------------------------------
    def test_option_f(self):
    
        ofilename = "__test__1__.js"
        ofile = open(ofilename,"w")
        ofile.write("print('Hello World')")
        ofile.close()
    
        args = [
            "python",
            shell,
            "-f",
            ofilename,
            "-f",
            ofilename,
        ]
        
        process = subprocess.Popen(args,stdout=subprocess.PIPE)
        
        (stdout, stderr) = process.communicate()
        
        self.assertEqual("Hello World\nHello World\n", stdout)
        
        os.remove(ofilename)        
        
    #---------------------------------------------------------------
    def test_option_ef(self):
    
        ofilename = "__test__1__.js"
        ofile = open(ofilename,"w")
        ofile.write("print('Hello World')")
        ofile.close()
    
        args = [
            "python",
            shell,
            "-f",
            ofilename,
            "-e",
            "print('Hello')",
        ]
        
        process = subprocess.Popen(args,stdout=subprocess.PIPE)
        
        (stdout, stderr) = process.communicate()
        
        self.assertEqual("Hello World\nHello\n", stdout)
        
        os.remove(ofilename)        
        
    #---------------------------------------------------------------
    def test_option_main_script(self):
    
        ofilename = "__test__1__.js"
        ofile = open(ofilename,"w")
        ofile.write("print('Hello World')")
        ofile.close()
    
        args = [
            "python",
            shell,
            ofilename,
        ]
        
        process = subprocess.Popen(args,stdout=subprocess.PIPE)
        
        (stdout, stderr) = process.communicate()
        
        self.assertEqual("Hello World\n", stdout)
        
        os.remove(ofilename)        
        
    #---------------------------------------------------------------
    def test_option_main_ef_script(self):
    
        ofilename = "__test__1__.js"
        ofile = open(ofilename,"w")
        ofile.write("print('Hello World')")
        ofile.close()
    
        args = [
            "python",
            shell,
            "-f",
            ofilename,
            "-e",
            "print('Hello')",
            ofilename,
        ]
        
        process = subprocess.Popen(args,stdout=subprocess.PIPE)
        
        (stdout, stderr) = process.communicate()
        
        self.assertEqual("Hello World\nHello\nHello World\n", stdout)
        
        os.remove(ofilename)        
        
    #---------------------------------------------------------------
    def test_arguments(self):

        script = "for (var i=1; i<arguments.length; i++) print(arguments[i])"   

        ofilename = "__test__1__.js"
        ofile = open(ofilename,"w")
        ofile.write(script)
        ofile.close()
        args = [
            "python",
            shell,
            ofilename,
            "123",
            "abc",
            "789",
        ]
        
        process = subprocess.Popen(args,stdout=subprocess.PIPE)
        
        (stdout, stderr) = process.communicate()
        
        self.assertEqual("123\nabc\n789\n", stdout)

        os.remove(ofilename)        
        
    #---------------------------------------------------------------
    def test_environment(self):

        script = "print(environment['__TESTING__'])"   

        args = [
            "python",
            shell,
            "-e",
            script,
        ]
        
        os.environ["__TESTING__"] = "1,2,3"
        process = subprocess.Popen(args,stdout=subprocess.PIPE,env=os.environ)
        
        (stdout, stderr) = process.communicate()
        
        self.assertEqual("1,2,3\n", stdout)

    #---------------------------------------------------------------
    def test_python_exec(self):

        script = "python_exec('jsfunc_join.py'); print(join('1','2','3'))"   

        args = [
            "python",
            shell,
            "-e",
            script,
        ]
        
        os.environ["__TESTING__"] = "1,2,3"
        process = subprocess.Popen(args,stdout=subprocess.PIPE,env=os.environ)
        
        (stdout, stderr) = process.communicate()
        
        self.assertEqual("123\n", stdout)
        
#-------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()

