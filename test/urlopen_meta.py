import re
import sys
from urllib.request import urlopen, Request

url = 'https://gihyo.jp/dp/'
headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"}
req = Request(url, headers=headers) 

f = urlopen(req)
bytes_content = f.read()

scanned_text = bytes_content[:1024].decode('ascii', errors = 'replace')

match = re.search(r'charset=["\']?([\w-]+)', scanned_text)
if match:
    encording = match.group(1)
else:
    encording = 'utf-8'

print('encording:', encording, file=sys.stderr)

text = bytes_content.decode(encording)
print(text)
