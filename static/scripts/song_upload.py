#!python
#
# Upload song text from .txt
#
# song_upload.py <path_to_files>

import urllib2, sys, os, time

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
      param += [("content", ( E_OS(file(name).read()) ))]

      register_openers()
      datagen, headers = multipart_encode(param)

      uri = "https://egaxegax.appspot.com/songs/add"
      if os.getenv('EGAX_DEBUG') == '1':
          uri = "http://127.0.0.1:8800/songs/add"

      print mcount, uri
      request = urllib2.Request(uri, datagen, headers)
      resp = urllib2.urlopen(request).read()
      time.sleep(1)
