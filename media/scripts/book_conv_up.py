#!python
# -*- coding: utf-8 -*-
#
# Extract .epub to text file.
#

import sys, os, re, datetime
import zlib, zipfile as zip

__help__ = u"""
Usage: book_conv_up.py <dir with .epub>
"""

def E_OS(text):
  return text

path = u'.'
if (len(sys.argv) > 1):
  path = os.path.abspath(E_OS(sys.argv[1]))

title = writer = pwriter = ''
index = part = pindex = 0

for root, dirs, files in os.walk(path, topdown=False):
  for name in files:
    curname = os.path.normpath(os.path.join(root, name))
    absname = os.path.join(os.getcwd(), curname)
    fname, ext = os.path.splitext(name)
    if (ext == '.epub'):
      print fname
      if not zip.is_zipfile(absname):
        print name, ' not a valid ZIP'
        continue

      za = zip.ZipFile(absname)
      for f in za.namelist():

        ft = za.read(f)
        if (f == 'content.opf'):
          title = re.findall('>(.*)</dc:title>', ft)[0]
          writer = re.findall('dc:creator opf:file-as="([^"]*)', ft)[0].replace(' &amp', '')
          subj = re.findall('>(.*)</dc:subject>', ft)[0]
          index = abs(zlib.crc32(name))
          if (pindex != index):
            pindex = index
            part = 0

        if (f == 'cover_image.jpg' or f == 'cover.jpeg'):
          za.extract(f, './')
          os.rename(f, name.encode('utf-8') + '.jpg')

        if (f[:5] == 'index' and os.path.splitext(f)[1] == '.xhtml'):
          content = re.findall('<body class="calibre">(.*)</body>', ft, re.M | re.S)[0]
          fn = name + '@' + writer.decode('utf-8') + '@' + title.decode('utf-8').replace('?','') + '@' + subj.decode('utf-8') + '@' + str(part) + '.txt'
          fbook = file(fn, 'w')
          fbook.write(E_OS(content))
          fbook.close()
          part += 1
