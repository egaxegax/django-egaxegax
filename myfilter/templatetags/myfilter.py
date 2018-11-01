from datetime import datetime
from django.utils.timesince import timesince
from django import template
register = template.Library()

import urllib, urllib2, urlparse, re

@register.filter
def time_since(strval):
    """Time interval."""
    try:
        return timesince(strval)
    except:
        return strval

@register.filter
def strans(strval):
    """Reverse text."""
    ss = strval.split(';')
    for i, strval in enumerate(ss):
        s = strval.split(',')
        s.reverse()
        ss[i] = ' '.join(s)
    return ';'.join(ss)

@register.filter
def strip_text(s):
    """Remove special chars."""
    s = s.lstrip(' Annotation ')
    s = s.replace('"','')
    s = s.replace("'",'')
    s = s.replace(">",'')
    s = s.replace("<",'')
    s = s.replace("!",'')
    return s

@register.filter
def get_im_url(url):
    """Get photo url."""
    if url:
        u = urlparse.urlparse(url)
        if u.netloc == 'yadi.sk': # Yandex disk
            try:
                uri = re.findall(r'<img class="[^\"]*" src="([^\"]*)"', urllib2.urlopen(url).read())
                if uri:
                    scheme, netloc, path, params, query, fragment = urlparse.urlparse(uri[0]) 
                    q = urlparse.parse_qs((query))
                    query = urllib.urlencode(q, True)
                    url = urlparse.urlunparse((scheme, netloc, path, params, query, fragment))
            except:
                pass
        else:
            pass   # Google store
    return url
 
@register.filter
def get_im_thumb(url, sz=''):
    """Get photo thumb with size."""
    if not sz: 
        sz = '2048'
    if url:
        url = get_im_url(url)  # check if Yandex img url
        if re.search('size=\d+x\d+', url): # Ya disk
            url = re.sub('size=\d+x\d+', 'size='+sz+'x'+sz, url)
        elif re.search('=s\d+$', url):  # Google store
            url = re.sub('=s\d+$', '=s'+sz, url)
        else:    # Google store
            url += '=s' + sz
    return url
