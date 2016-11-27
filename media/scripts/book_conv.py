#!python
# -*- coding: utf-8 -*-
#
# Extract .epub to GAE DataStore text file.
#

import sys, os, re, datetime
import zlib, zipfile as zip

__help__ = u"""
Usage: book_conv.py <dir with .epub> (extract to current dir)
"""

def E_OS(text):
  return text

path = u'.'
if (len(sys.argv) > 1):
  path = os.path.abspath(E_OS(sys.argv[1]))

fbook = False
title = writer = pwriter = ''
index = part = pindex = 0
author_id = 5521805645185024 # guru
dt = datetime.datetime.today().replace(microsecond=0).isoformat()
wrt = {}

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
          writer = re.findall('dc:creator .*="([^"]*)', ft)[0].replace(' &amp', '')
          writer_id = abs(zlib.crc32(writer))
          index = abs(zlib.crc32(writer + ' ' + title))
          if (pindex != index):
            pindex = index
            part = 0
            fname = 'books_book_' + writer.decode('utf-8') + '_' + title.decode('utf-8').replace('?','') + '.txt'
            if (fbook): fbook.close()
            fbook = file(fname, 'w')
            if os.stat(fname).st_size == 0:
              print >> fbook, 'index,title,writer_id,content,part,key,date,author_id'

#         if (f == 'cover_image.jpg'):
#           za.extract(f, './')
#           os.rename(f, name.encode('utf-8') + '.jpg')

        if (f[:5] == 'index' and os.path.splitext(f)[1] == '.xhtml'):
          book_id = abs(zlib.crc32(title + ' ' + str(part)))
          content = re.findall('<body class="calibre">(.*)</body>', ft, re.M | re.S)[0]
          if part > 0: # skip uploaded part 0
              print >> fbook, str(index) + ',"' + E_OS(title) + '",' + str(writer_id) + ',"' + E_OS(content.replace('"','""')) + '",' + str(part) + ',' + str(book_id) + ',"' + dt + '",' + str(author_id)
          part += 1
          if not writer in wrt:
            wrt[writer] = [writer_id]
          if not index in wrt[writer]:
            wrt[writer].append( index ) 

fwriter = file('books_writer.txt', 'w')
print >> fwriter, 'count,writer,key'
for writer in wrt:
  writer_id = wrt[writer][0]
  print >> fwriter, str(len(wrt[writer])-1) + ',"' + E_OS(writer) + '",' + str(writer_id)
