#!python
# -*- coding: utf-8 -*-
#
# Upload books from text files with cover image and .epub file
#
# book_upload.py <path_to_files>

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2, re, sys, os, time, zlib

def E_OS(text):
  if os.name == 'nt':
    return text.decode('cp1251')
  return text

path = u'.'
mcount = 0 # files uploaded counter
nstart = 0 # start counter

if len(sys.argv) > 1:
  path = os.path.abspath(sys.argv[1])

if len(sys.argv) > 2:
  nstart = int(sys.argv[2])

uplog = file(os.path.join(path, 'up.log'), 'w')

for root, dirs, files in os.walk(path, topdown=False):
  for name in files:

    fname, ext = os.path.splitext(name)

    if ext == '.txt':

      mcount += 1

      if mcount < nstart:
          continue

      ss = fname.split('@')
      mname, writer, title, subject, part = ss
      
      print mname, writer, title, subject, part

      os.chdir(root)
      param = []
 
      if int(part) == 0:
          try:
            param += [('img', open(mname + '.jpg', "rb"))]
          except:
            pass
     
          try:
            prev = os.getcwd()
            os.chdir('..')
            param += [('file', open(mname, "rb"))]
            os.chdir(prev)
          except:
            pass
 
      param += [("title", E_OS(title))]
      param += [("writer", E_OS(writer))]
      param += [("subject", E_OS(subject))]
      param += [("content", file(name).read())]
      param += [("part", part)]

      register_openers()
      datagen, headers = multipart_encode(param)
 
      request = urllib2.Request("http://egaxegax.appspot.com/books/add")
      uri = re.findall(r'form action="([^\"]*)"', urllib2.urlopen(request).read())
      if uri:
          print mcount, uri
          request = urllib2.Request(uri[0], datagen, headers)
          print >> uplog, urllib2.urlopen(request).read()
          time.sleep(3)

