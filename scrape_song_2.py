#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import re
from urllib.parse import urljoin
import requests
import lxml.html
from pymongo import MongoClient

URL_ARTIST_DEFAULT = 'http://www.uta-net.com/artist/684/'


def main():
    """
    scrape_list_page(): artist の楽曲一覧から song ページの URL を取得
    scrape_song()     : 1つの song のページから曲名、アーティスト名、歌詞を取得
    extract_key()     : URL からキーを取り出す
    """
    # 楽曲一覧ページの指定
    if len(sys.argv) > 1:
        root_url = sys.argv[1]
    else:
        root_url = URL_ARTIST_DEFAULT

    client = MongoClient('localhost', 27017) # 第2引数はポート番号
    collection = client.scraping.songs # scraping データベースの songs コレクションを得る（ない場合は新規作成）
    collection.create_index('key', unique=True)

    session = requests.Session()  # Session によって複数ページを効率よくクローリング
    response = requests.get(root_url)
    urls = scrape_list_page(response)
    
    for url in urls:
        key = extract_key(url) # URL からキーを取得
        #print(key)
        song = collection.find_one({'key': key}) # MongoDB から key に該当するデータを検索
        if not song:
            time.sleep(1)
            response = session.get(url)
            song = scrape_song(response)
            collection.insert_one(song)

        #print(song)
        #print(song['lyric'].replace('\n', ' '))
        print(song['lyric'])

        
    
def scrape_list_page(response):
    """
    パーマリンク一覧の中で、楽曲に関するものを抽出するジェネレータ関数
    ex. <td class="side td1"><a href="/song/69260/">...
    """
    root = lxml.html.fromstring(response.content)
    #root.make_links_absolute(response.url) # 相対パスをすべて絶対パスに変換
    
    for a in root.cssselect('td.side.td1 a[href^="/song/"]'):  
        url = urljoin(response.url, a.get('href'))
        #print(url, a.text)
        yield url

    

def scrape_song(response):
    """
    引数 response から曲名、アーティスト、作詞者、作曲者、歌詞を取得
    return: dict 型
    TODO: 編曲者がいる場合の対応
    """
    root = lxml.html.fromstring(response.content)
    song = {'url'      : response.url,
            'key'      : extract_key(response.url),
            'title'    : root.cssselect('div.title h2')[0].text,
            'artist'   : root.cssselect('div.kashi_artist span[itemprop="byArtist name"]')[0].text,
            'lyricist' : root.cssselect('div.artist_etc.clearfix h4')[0].text,
            'comporser': root.cssselect('div.artist_etc.clearfix h4')[1].text,
    }

    # 歌詞に <br /> を残すための処理
    # 一旦 str 型の html に戻してから <br>, <br /> を "\n" に置換
    # Note: "<br />" は "<br>" にすでに変換されている
    item = lxml.html.tostring(root.cssselect('#kashi_area')[0]).decode('utf-8').replace(u"<br>", "\n")
    lyric = lxml.html.fromstring(item).text_content()
    song['lyric'] = lyric.replace('\u3000', ' ') # 全角スペースを半角スペースに

    return song



def extract_key(url):
    # URL から末尾のISBNを取り出しキーとする
    return re.search(r'/song/([0-9]+)/$', url).group(1)



if __name__ == '__main__':
    main()
