#!python
# -*- coding: utf-8 -*-
#
# Upload images to Yandex.Disk
#
# photo_upload.py <path_to_files> [<memberonly>] [<user>]

import urllib2, re, sys, os, time

sys.path.insert(0, os.path.abspath(sys.argv[0] + '/../../..'))

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from YaDiskClient.YaDiskClient import YaDisk

def E_OS(text):
  if os.name == 'nt':
    return text.decode('cp1251')
  return text

path = u'.'
if (len(sys.argv) > 1):
  path = os.path.abspath(sys.argv[1])

memberonly = False
if (len(sys.argv) > 2):
  memberonly = len(sys.argv[2]) > 0
  
user = 'guru'
if (len(sys.argv) > 3):
  user = sys.argv[3]

yadisk = YaDisk(os.getenv('YALOGIN'), os.getenv('YAPASSWD'))

for root, dirs, files in os.walk(path, topdown=False):

  cwd = os.getcwd()
  os.chdir(root)

  for name in files:

    fname, ext = os.path.splitext(name)

    if ext.lower() in ('.gif','.jpg','.png',):

      remote_folder = 'FotoSite'
      if os.getenv('EGAX_DEBUG') == '1':
          remote_folder = 'Foto'
      remote_file = name
      remote_path = E_OS('/{folder}/{file}'.format(folder=remote_folder, file=remote_file))

      yadisk.upload(remote_file, remote_path)
      url = yadisk.publish_doc(remote_path)

      param = []

      param += [("album", E_OS(os.path.basename(cwd)))]
      param += [("thumb_url", url)]
      param += [("title", E_OS(fname))]
      param += [("memberonly", memberonly)]
      param += [("user", user)]

      print os.path.basename(cwd), name, url
 
      register_openers()
      datagen, headers = multipart_encode(param)

      url = "http://egaxegax.appspot.com/photos/add"
      if os.getenv('EGAX_DEBUG') == '1':
          url = "http://127.0.0.1:8800/photos/add"
 
      request = urllib2.Request(url)
      uri = re.findall(r'form action="([^\"]*)"', urllib2.urlopen(request).read())
      if uri:
          print uri
          request = urllib2.Request(uri[0], datagen, headers)
          resp = urllib2.urlopen(request).read()
          time.sleep(3)
