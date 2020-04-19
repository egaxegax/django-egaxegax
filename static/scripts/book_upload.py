#!python
#
# Upload books from text files and .epub file located ..
#
# book_upload.py <path_to_files_txt>

import urllib2, re, sys, os, time

sys.path.insert(0, os.path.abspath(sys.argv[0] + '/../../../vendor'))

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

def E_OS(text):
  if os.name == 'nt':
    return text.decode('cp1251')
  return text

path = '.'
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
      mname, writer, title, subject = ss
      
      print mname, writer, title, subject

      os.chdir(root)
      param = []
 
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

      register_openers()
      datagen, headers = multipart_encode(param)

      uri = "https://egaxegax.appspot.com/books/add"
      if os.getenv('EGAX_DEBUG') == '1':
          uri = "http://127.0.0.1:8800/books/add"
 
      request = urllib2.Request(uri)
      uri = re.findall(r'form action="([^\"]*)"', urllib2.urlopen(request).read())
      if uri:
          print mcount, uri
          request = urllib2.Request(uri[0], datagen, headers)
          print >> uplog, urllib2.urlopen(request).read()
          time.sleep(3)
