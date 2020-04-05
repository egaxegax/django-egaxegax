#!python
#
# Transform GAE leveldb log format songs dumps to files .txt

import os, sys, binascii, zlib, base64, fnmatch, time
from os.path import *

def D_OS(text):
  if os.name == 'nt':
    return text.decode('utf-8')
  return text

def E_OS(text):
  if os.name == 'nt':
    return text.encode('cp866')
  return text.encode('utf-8')


if not exists('out'):
  os.mkdir('out') 

for fn in os.listdir('.'):

  if not fnmatch.fnmatch(fn, '*_my_song_*'):
    continue

  print(fn)
  time.sleep(2)

  ns, ns1, ne, ne1, buf = 0, 0, 0, 0, ''

  with open(fn, 'rb') as f:
    while 1:
      bs = f.read(32768)
      if not bs: break
      buf += bs[7:]   #skip 7B of 32KB block
  hx = binascii.hexlify(buf).upper()

  for i in range(0,len(hx),2):
    if hx[i-6*2:i] == '617274697374': #artist
      ns = i+6*2
    if ns > ne and hx[i:i+9*2] == '617574686F725F6964': #author_id
      ln = int(hx[ns-2:ns], 16)*2
      ne = ns+ln
      artist = D_OS(binascii.unhexlify(hx[ns:ne]))
      for s in ('?', '!', '/'): artist = artist.replace(s,'') # replace extra symbols
    if ne >= ns and hx[i-5*2:i] == '7469746C65':    #title ( skip Untitled )
      ns = i+6*2
    if ns > ne and hx[i:i+7*2] == '636F6E74656E74': #content
      ln = int(hx[ns-2:ns], 16)*2
      ne = ns+ln
      title = D_OS(binascii.unhexlify(hx[ns:ne]))
      for s in ('?', '!', '/'): title = title.replace(s,'') # replace extra symbols
    if ne > ns and hx[i:i+7*2] == '6261736536342C':   #base64
      ns1 = i
    if ns1 > ne1 and hx[i:i+7*2] == '6D795F736F6E67': #my_song
      ne1 = i-6*2
      t = binascii.unhexlify(hx[ns1:ne1])
      try:    print(E_OS(artist))
      except: print('...')
      try:    print(E_OS(title)+'\n')
      except: print('...')
      if not exists(join('out', artist)):
        os.mkdir(join('out', artist))
      file(join('out', artist, title+'.txt'), 'w').write(zlib.decompress(base64.b64decode(t[7:]))) ##content
