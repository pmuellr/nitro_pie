#!/bin/sh

echo ---------------------------------------------------
echo Python
echo ---------------------------------------------------
time python sum.py

echo

echo ---------------------------------------------------
echo JavaScriptCore
echo ---------------------------------------------------
time python ../lib/nitro-pie.py sum.js