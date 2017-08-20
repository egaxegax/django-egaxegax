#!python
# -*- coding: utf-8 -*-
#
# Upload song text from .txt
#
# song_upload.py <path_to_files>

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2, re, sys, os, time, zlib, base64

def E_OS(text):
  if os.name == 'nt':
    return text.decode('cp1251')
  return text

path = u'.'
mcount = 0 # files uploaded counter
nstart = 0 # start counter
ncount = 0 # count 
nname = '' # search name

if len(sys.argv) > 1:
  path = os.path.abspath(sys.argv[1])

if len(sys.argv) > 2:
  if sys.argv[2].isdigit():
    nstart = int(sys.argv[2])
  else:
    nname = sys.argv[2]

if len(sys.argv) > 3:
  ncount = int(sys.argv[3])

uplog = file(os.path.join(path, 'up.log'), 'w')

for root, dirs, files in os.walk(path, topdown=False):
  for name in files:

    fname, ext = os.path.splitext(name)

    if ext == '.txt':

      mcount += 1

      if mcount < nstart:
          continue

      if ncount and (mcount - nstart) >= ncount:
          break

      # search name
      if nname and nname not in fname:
          continue

      artist = os.path.basename(root)
      title = fname

      os.chdir(root)

      print artist, title

      param = []
      param += [("artist", E_OS(artist))]
      param += [("title", E_OS(title))]
      param += [("content", E_OS( file(name).read() ))]

      register_openers()
      datagen, headers = multipart_encode(param)

      uri = "http://egaxegax.appspot.com/songs/add"
#       uri = "http://127.0.0.1:8800/songs/add"
#       request = urllib2.Request(uri)
      print mcount, uri
      request = urllib2.Request(uri, datagen, headers)
      print >> uplog, urllib2.urlopen(request).read()
      time.sleep(1)
