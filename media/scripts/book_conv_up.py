#!python
# -*- coding: utf-8 -*-
#
# Extract .epub to text files for form upload.
#

import sys, os, re, datetime
import zlib, zipfile

pth = os.path.abspath(sys.argv[0] + '../../../../')

sys.path.insert(0, pth)
sys.path.insert(0, pth + '/django/utils')

from transliterate import *

__help__ = u"""
Usage: book_conv_up.py <dir with .epub>
"""

def E_OS(text):
  return text

path = u'.'
if (len(sys.argv) > 1):
  path = os.path.abspath(E_OS(sys.argv[1]))

title = writer = pwriter = ''
index = part = pindex = k = 0

for root, dirs, files in os.walk(path, topdown=False):
  for name in files:
    oldname = os.path.normpath(os.path.join(root, name))
    name = translit(name.decode('cp1251'), 'ru', reversed=True).encode('utf-8').replace("'","").replace(" ","_").replace('«','').replace('»','')
    curname = os.path.normpath(os.path.join(root, name))
    fname, ext = os.path.splitext(name)
    if (ext == '.epub'):
      k += 1
      os.rename(oldname, curname)
      print k, name
      if not zipfile.is_zipfile(curname):
        print name, ' not a valid ZIP'
        continue

      za = zipfile.ZipFile(curname)
      for f in za.namelist():

        ft = za.read(f)
        if (f == 'content.opf'):
          title = re.findall('>(.*)</dc:title>', ft)[0].replace('?','')
          writer = re.findall('dc:creator .*opf:file-as="([^"\&\;]*)', ft)[0].replace(' &amp', '')
          subj = re.findall('>(.*)</dc:subject>', ft)
          if subj:
              subj = subj[0]
          else:
              print "!! Subj is not defined !!"
              subj = 'prose_classic'
          index = abs(zlib.crc32(name))
          if (pindex != index):
            pindex = index
            part = 0

        if (f.startswith('cover')):
          za.extract(f, './')
          newname = name + '.jpg'
          if os.path.isfile(newname):
            os.remove(newname)
          os.rename(f, newname)

        if (f.startswith('index') and f.endswith('.xhtml') and part == 0):
          content = re.findall('<body class="calibre">(.*)</body>', ft, re.M | re.S)[0]
          fn = name + '@' + writer.decode('utf-8') + '@' + title.decode('utf-8') + '@' + subj.decode('utf-8') + '@' + str(part) + '.txt'
          fbook = file(fn, 'w')
          fbook.write(E_OS(content))
          fbook.close()
          part += 1
