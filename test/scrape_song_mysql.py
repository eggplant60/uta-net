#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import re
from urllib.request import urlopen, Request
from html import unescape
#import sqlite3
import MySQLdb as mysql

URL_ARTIST_DEFAULT = 'http://www.uta-net.com/artist/684/'
#SONGS_DB = 'songs.db'


def main():
    """
    fetch()        : 与えられた url（artist/song のページ）から html を取得
    scrape_artist(): artist のページから song のページの URL を取得
    scrape_song()  : 1つの song のページから曲名、アーティスト名、歌詞を取得
    save_song()    : DB に1つの曲情報を追加
    """
    #with open('mr_children_songs/index.html.3') as f:
    #    html = f.read()
    #dict = scrape_song(html)
    #print(dict)

    if len(sys.argv) > 1:
        html_artist = fetch(sys.argv[1])
    else:
        html_artist = fetch(URL_ARTIST_DEFAULT)
        
    for song in scrape_artist(html_artist):
        html_song = fetch(song['url'])
        song_data = scrape_song(html_song)
        #print(song_data)
        save_song(os.environ['MYSQL_DB'], os.environ['MYSQL_USER'], os.environ['MYSQL_PASS'], song_data)
        time.sleep(1)
        
    
def fetch(url):
    """
    引数 url の Web ページを取得する。
    Web ページのエンコーディングは Contet-Type ヘッダから取得
    return: str 型の HTML
    """
    # サイトによっては header を指定しないと 403 forbbiten になるため
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"}
    req = Request(url, headers=headers) 
    f = urlopen(req)
    encording = f.info().get_content_charset(failobj="utf-8") # 明示されていないときは utf-8
    html = f.read().decode(encording)
    return html


def scrape_artist(html_artist):
    """
    アーティストのページには曲一覧があるので、そこから個々の曲ページへの URL を取得
    return: 曲(dict)のリスト
    """
    songs = []
    for partial_html in re.findall(r'<tr><td class="side td1">.*?</td></tr>',
                                   html_artist, re.DOTALL):
        url, title = re.search(r'<a href="(.*?)">(.*?)</a>',
                               partial_html, re.DOTALL).group(1,2)
        url = 'http://www.uta-net.com' + url
        title = re.sub(r'<.*?>', '', title) # タグの削除
        title = unescape(title)

        songs.append({'url': url, 'title': title}) 
          
    return songs
    

def scrape_song(html_song):
    """
    引数 html_song から曲名、アーティスト、作詞者、作曲者、歌詞を取得
    return: dict 型
    """
    title = re.search(r'<h2.*?>(.*?)</h2>.*</div>.*<div class="artist_etc clearfix">',
                      html_song, re.DOTALL).group(1)
    title = unescape(title)

    artist = re.search(r'<a href="/artist/[0-9]+/" .*<span itemprop="title">(.*?)</span></a></h3><br>',
                       html_song).group(1)
    artist = unescape(artist)

    lyricist, comporser = re.search(r'作詞：<h4>(.*?)</h4><br>.*作曲：<h4>(.*?)</h4><br>',
                                    html_song, re.DOTALL).group(1,2)
    lyricist = unescape(lyricist)
    comporser = unescape(comporser)
    
    lyric = re.search(r'<div id="kashi_area">(.*?)</div>', html_song).group(1)
    #lyric = lyric.replace('<br />', '<\ >')
    lyric = lyric.replace('\u3000', ' ') # 全角スペースを半角スペースに
    lyric = unescape(lyric)
          
    return {'title': title,
            'artist': artist,
            'lyricist': lyricist,
            'comporser': comporser,
            'lyric': lyric}


def save_song(db, user, passwd, song_data):
    """
    引数 song_data で与えられた dict を MySQL データベースに保存
    return:  なし
    """
    conn = mysql.connect(db=db, user=user, passwd=passwd, charset='utf8mb4')
    
    c = conn.cursor()
    #c.execute('DROP TABLE IF EXISTS songs') # すでにテーブルが存在する場合は削除
    try:
        c.execute('''
        CREATE TABLE songs(
        title text, 
        artist text,
        lyricist text, 
        comporser text, 
        lyric text
        )
        ''')

    except:
        pass
    c.execute('INSERT INTO songs VALUES (%(title)s, %(artist)s, %(lyricist)s, %(comporser)s, %(lyric)s)', song_data)
    conn.commit()

    #c.execute('SELECT * FROM songs')
    #for row in c.fetchall():
    #    print(row)
    
    conn.close()
    

if __name__ == '__main__':
    main()
