# base64 encode image

import sys, os.path
import base64

img = file(sys.argv[1], "rb")
ext = os.path.splitext(sys.argv[1])[1][1:]
print ( "data:image/" + ext + ";base64," + base64.b64encode(img.read()) )