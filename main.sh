#!/bin/bash

script='./scrape_song_2.py'

array="
8613 #
970  
134  
322  # FLOW
356  
7063 
1023 
536  
3892 
1475 # スピッツ
684  # Mr. Children
126  # BUMP OF CHICKEN
2983 # seikimatsu
9699 # SEKAI NO OWARI
4424 # abingdon boys school
991  # THE ALFEE
68   # ASIAN KUNG-FU GENERATION
85   # Bank Band
6701 # DOES
281  # ELLEGARDEN
8060 # flumpool
9369 # Galileo Galilei
9869 # GALNERYUS
4547 # GazettE
356  # GLAY
7655 # GRANRODEO
8795 # HIATUS
444  # JAM Project
1462 # スガシカオ
4082 # RADWIMPS
8377 # UNISON SQUARE GARDEN
"
	

for no in `echo "$array" | awk '{print $1}'`; do
    echo $no
    $script https://www.uta-net.com/artist/$no/
done
