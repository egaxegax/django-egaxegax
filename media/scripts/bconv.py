#!python
# -*- coding: utf-8 -*-
#
# Extract .epub to GAE DataStore text file.
#

import sys, os, re, datetime
import zlib, zipfile as zip

__help__ = u"""
Usage: bconv.py <dir with .epub>
"""

E_OS = lambda text: text.decode('utf-8').encode('cp1251')

path = u'.'
if (len(sys.argv) > 1):
  path = os.path.abspath(E_OS(sys.argv[1]))

fwriter = fbook = False

for root, dirs, files in os.walk(path, topdown=False):
  for name in files:
    curname = os.path.normpath(os.path.join(root, name))
    absname = os.path.join(os.getcwd(), curname)
    if (os.path.splitext(name)[1] == '.epub'):
      if not zip.is_zipfile(absname):
        print name, ' not a valid ZIP'
        continue

      title = writer = ''
      index = part = wcount = bcount = 0
      author_id = 5521805645185024 # guru
      dt = datetime.datetime.today().replace(microsecond=0).isoformat()

      if (not wcount%100):
        npage = bcount / 100
        sp = str(npage).rjust(4, '0')
        if (fwriter): fwriter.close() 
        fwriter = file('books_writer_' + sp +  '.txt', 'w')
        print >> fwriter, 'count,writer,key'


      za = zip.ZipFile(absname)
      for f in za.namelist():
      
        if (not bcount%100):
          npage = bcount / 100
          sp = str(npage).rjust(4, '0')
          if (fbook): fbook.close()
          fbook = file('books_book_' + sp + '.txt', 'w')
          print >> fbook, 'index,title,writer_id,content,part,key,date,author_id'

        ft = za.read(f)
        if (f == 'content.opf'):
          title = re.findall('>(.*)</dc:title>', ft)[0]
          writer = re.findall('>(.*)</dc:creator>', ft)[0]
          writer_id = abs(zlib.crc32(writer))
          index = abs(zlib.crc32(writer + ' ' + title))
        if (f[:5] == 'index' and os.path.splitext(f)[1] == '.xhtml'):
          book_id = abs(zlib.crc32(title + ' ' + str(part)))
          content = re.findall('<body class="calibre">(.*)</body>', ft, re.M | re.S)[0]
          print >> fbook, str(index) + ',"' + E_OS(title) + '",' + str(writer_id) + ',"' + E_OS(content.replace('"','""')) + '",' + str(part) + ',' + str(book_id) + ',"' + dt + '",' + str(author_id)
          part += 10
          bcount += 1

      print >> fwriter, str(bcount) + ',"' + E_OS(writer) + '",' + str(writer_id)
      wcount += 1
