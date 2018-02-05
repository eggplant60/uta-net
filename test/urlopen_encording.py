import sys
from urllib.request import urlopen, Request

url = 'https://gihyo.jp/dp/'
headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"}
req = Request(url, headers=headers) 

f = urlopen(req)

encording = f.info().get_content_charset(failobj="utf-8")
print('encording:', encording, file=sys.stderr)

text = f.read().decode(encording)
print(text)
