#!/usr/bin/env python
#
# Copyright 2011 Eric A. Borisch. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice, this list of
#      conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright notice, this list
#      of conditions and the following disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY ERIC A. BORISCH ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ERIC A. BORISCH OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those of the
# authors and should not be interpreted as representing official policies, either expressed
# or implied, of Eric A. Borisch.


import sys
import os
import re

def usage():
  print("Usage: depTree.py port_name [max_depth (0 = infinite)]")
  sys.exit(0)

scannedDeps=set()
sentLines=set()

if len(sys.argv) < 2:
  usage()

if "-?" in sys.argv:
  usage()

def extract(line):
  return [x.strip() for x in line[line.find(":")+1:].split(',')]

def scanDeps(a, depth):
  # Don't scan twice
  if (a,depth) in scannedDeps:
    return
  else:
    scannedDeps.add((a,depth))

  if maxDepth and depth + 1 > maxDepth :
    return
  (inp,result)=os.popen2("port info " + a)
  result = result.readlines();

  for line in result:
    if re.search("Build Dependencies",line):
      style = "[style=dotted]"
    elif re.search("Library Dependencies",line):
      style = ""
    elif re.search("Runtime Dependencies",line):
      style = "[style=dashed]"
    else:
      continue

    deps = extract(line)
    for dep in deps:
      newOut = '"%s" -> "%s" %s;' % (a,dep,style)
      if not newOut in sentLines:
        sentLines.add(newOut)
        dotProc.stdin.write(newOut)
      scanDeps(dep,depth+1)

maxDepth = 0

for arg in sys.argv[1:]:
  try:
    if int(arg):
      maxDepth = int(arg)
      sys.argv.remove(arg)
  except:
    pass

from subprocess import *

dotProc = Popen(["dot","-Tpng"], stdin=PIPE, stdout=PIPE)

dotProc.stdin.write("Digraph G {")
for port in sys.argv[1:]:
  scanDeps(port, 0)
dotProc.stdin.write('graph [label="Dependencies of %s"]' % ','.join(sys.argv[1:]))
dotProc.stdin.write("}")

if dotProc.returncode:
  print ("Error in dot subprocess!?)")
  sys.exit(dotProc.returncode)

results = dotProc.communicate()
oFile=open(sys.argv[1] + ".png",'w')
oFile.write(results[0])
oFile.close()

v=Popen(("open" , sys.argv[1]+".png"))
v.communicate()
sys.exit(0)

