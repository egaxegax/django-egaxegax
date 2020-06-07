#!python
#
# Upload images to GAE
#
# photo_upload.py <path_to_files> [<memberonly>] [<user>]

import urllib2, re, sys, os, time

sys.path.insert(0, os.path.abspath(sys.argv[0] + '/../../vendor'))

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

def E_OS(text):
  if os.name == 'nt':
    return text.decode('cp1251')
  return text

path = '.'
if (len(sys.argv) > 1):
  path = os.path.abspath(sys.argv[1])

memberonly = False
if (len(sys.argv) > 2):
  memberonly = len(sys.argv[2]) > 0
  
user = 'guru'
if (len(sys.argv) > 3):
  user = sys.argv[3]

uplog = file(os.path.join(path, 'up.log'), 'w')

for root, dirs, files in os.walk(path, topdown=False):

  cwd = os.getcwd()
  os.chdir(root)

  for name in files:

    fname, ext = os.path.splitext(name)

    if ext.lower() in ('.gif','.jpg','.png',):

      param = []

      try:
        param += [('img', open(name, "rb"))]
      except:
        print 'Error: ', sys.exc_info()[0], sys.exc_info()[1]

      param += [("album", E_OS(os.path.basename(cwd)))]
      param += [("title", E_OS(fname))]
      param += [("memberonly", memberonly)]
      param += [("user", user)]

      print os.path.basename(cwd), name

      register_openers()
      datagen, headers = multipart_encode(param)

      url = "https://egaxegax.appspot.com/photos/add"
      if os.getenv('EGAX_DEBUG') == '1':
          url = "http://127.0.0.1:8800/photos/add"

      request = urllib2.Request(url)
      uri = re.findall(r'form action="([^\"]*)"', urllib2.urlopen(request).read())
      if uri:
          print uri
          request = urllib2.Request(uri[0], datagen, headers)
          print >> uplog, urllib2.urlopen(request).read()
          time.sleep(3)
