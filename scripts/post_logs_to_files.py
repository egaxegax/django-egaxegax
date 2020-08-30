#!python
#
# Transform GAE leveldb log format posts dumps to files .txt

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

  if not fnmatch.fnmatch(fn, '*_guestbook_greeting_*'):
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
    if hx[i:i+10*2] == '7375626A6563745F6964':      #subject_id
      ns = i+15*2
    if hx[i:i+5*2] == '7469746C65':                 #title ( skip Untitled )
      ne = i-3*2 
      subject = hx[ns:ne]
      ns = i+11*2
    if ns > ne and hx[i:i+7*2] == '636F6E74656E74': #content
      print hx[ns-2:ns+10]
      continue
      ln = int(hx[ns-2:ns], 16)*2
      if i in [252266, 260308]: ln = 292
      ne = ns+ln
      if i in [252266, 260308]: ns += 4
      if ne < i: title = D_OS(binascii.unhexlify(hx[ns:ne])) #title < content
      else:      title = '___' + str(i)
      for s in ('?', '!', '/'): title = title.replace(s,'')  #replace extra symbols
      for s in ('"',): title = title.replace(s,"'")          #replace extra symbols
    if ne > ns and hx[i:i+7*2] == '6261736536342C':          #base64
      ns1 = i
    if ns1 > ne1 and hx[i:i+9*2] == '6775657374626F6F6B':    #guestbook
      ne1 = i-6*2
      t = binascii.unhexlify(hx[ns1:ne1])
      try:    print(E_OS(subject))
      except: print('...')
      try:    print(E_OS(title)+'\n')
      except: print('...')
      if not exists(join('out', subject)):
        os.mkdir(join('out', subject))
      file(join('out', subject, title+'.txt'), 'w').write(zlib.decompress(base64.b64decode(t[7:]))) ##content
