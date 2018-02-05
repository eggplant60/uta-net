import sys
import re
from html import unescape
import json

for index in sys.argv[1:]:
    
    with open(index) as f:
        html = f.read()

    #for partial_html in re.findall(r'<div id="kashi_area">.*</div>', html, re.DOTALL):

    #title = re.search(r'<!-- 試聴ボタンここまで -->.*<h2>(.*?)</h2>', html, re.DOTALL).group(1)
    title = re.search(r'<h2>(.*?)</h2>.*</div>.*<div class="artist_etc clearfix">', html, re.DOTALL).group(1)
    title = unescape(title)
    print(title)
    print("")

    artist = re.search(r'<a href="/artist/[0-9]+/" .*<span itemprop="title">(.*?)</span></a></h3><br>',
                       html).group(1)
    artist = unescape(artist)
    print(artist)
    print("")

    kashi = re.search(r'<div id="kashi_area">(.*?)</div>', html).group(1)
    #kashi = kashi.replace('<br />', '\n')
    kashi = unescape(kashi)
    print(kashi)

    print(json.dumps([{'title':title, 'artist':artist, 'kashi':kashi}],
                     ensure_ascii=False, indent=2))
