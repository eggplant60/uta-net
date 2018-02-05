#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import argparse
from pymongo import MongoClient
import re
import numpy as np
from sklearn.cross_validation import train_test_split

from pyknp import Jumanpp
import unicodedata
import sys
import codecs

#sys.stdin = codecs.getreader('utf-8')(sys.stdin)
#sys.stdout = codecs.getwriter('utf-8')(sys.stdout)


def read_db(collection, query=None):

    titles = []
    artists = []
    lyrics = []
    
    for entry in collection.find(query):
        titles.append(entry['title'])
        artists.append(entry['artist'])
        lyrics.append(entry['lyric'])

    return titles, artists, lyrics


def split_batches(titles, artists, lyrics):
    new_titles = []
    new_artists = []
    new_lyrics = []

    for t, a, l in zip(titles, artists, lyrics):
        split_lyrics = re.split('\n\n+', l) # パラグラフごとに分ける
        for split_lyric in split_lyrics:
            # パラグラフの切れ目以外の改行は / で置き換えておく
            split_lyric = split_lyric.replace('\n', '/')
            if not is_english_all(split_lyric):
                new_titles.append(t)    # 同じタイトル、アーティストで埋める
                new_artists.append(a)
                new_lyrics.append(split_lyric)

    return new_titles, new_artists, new_lyrics


def is_english_all(string): # \n が含まれているとエラー
    for ch in string:
        name = unicodedata.name(ch)
        if "CJK UNIFIED" in name \
           or "HIRAGANA" in name \
           or "KATAKANA" in name \
           or "FULLWIDTH" in name:
            return False
    return True
        


def split_words(string): # アルファベット+半角スペース+アルファベットだとエラー
    jumanpp = Jumanpp()
    semi_split = string.split(' ')
    str_list = []
    for s in semi_split:
        if is_english_all(s):
            str_list.append(s)
        else:
            result = jumanpp.analysis(s)
            str_list.extend([mrph.midasi for mrph in result.mrph_list()])
    return ' '.join(str_list)



def get_lyrics_dataset():
    client = MongoClient('localhost', 27017) # 第2引数はポート番号
    collection = client.scraping.songs       # ない場合は新規作成
    print('number of the entries: {}'.format(collection.find().count()))

    titles, artists, lyrics = read_db(collection)
    titles, artists, lyrics = split_batches(titles, artists, lyrics)

    len_lyrics = len(lyrics)
    new_lyrics = []
    for i, l in enumerate(lyrics):
        print('{}/{}'.format(i+1, len_lyrics))
        new_lyrics.append(l)

    #print(titles, artists, lyrics)
    #print(split_words("Today aaa 運命なら"))
    #print(split_words("ケーキを食べる"))

    return titles, artists, new_lyrics


if __name__ == '__main__':
    _, _, lyrics = get_lyrics_dataset()
    print(lyrics[10:15])
    

