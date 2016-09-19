#!python
# -*- coding: utf-8 -*-
#
# Upload file to GAE BlobStore.
#

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2, re, sys

# Register the streaming http handlers with urllib2
register_openers()

# Start the multipart/form-data encoding of the file "DSC0001.jpg"
# "image1" is the name of the parameter, which is normally set
# via the "name" parameter of the HTML <input> tag.

# headers contains the necessary Content-Type and Content-Length
# datagen is a generator object that yields the encoded parameters
datagen, headers = multipart_encode({
  "img": open(sys.argv[1], "rb"),
  "title":sys.argv[2],
  "title1":sys.argv[2],
  "album":sys.argv[3],
  "album1":sys.argv[3] })

request = urllib2.Request("http://egaxegax.appspot.com/photos/add")
uri = re.findall(r'form action="([^\"]*)"',urllib2.urlopen(request).read())
if uri:
    print uri
    # Create the Request object
    request = urllib2.Request(uri[0], datagen, headers)
    # Actually do the request, and get the response
    print urllib2.urlopen(request).read()
