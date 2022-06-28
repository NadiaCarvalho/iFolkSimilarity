# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 10:24:33 2022

@author: Daniel Diogo
"""

#   Library imports

from music21 import *
#import json_generator
from os import walk
import string
from json_generator import *
import mei_parsing as mei
import json


def m21TOLyrics(s):
    dict_lyrics = s.flat.lyrics()
    lyrics = []
    for l in dict_lyrics[1]:
            parsed_text = l.text.replace(u'\xa0', u' ')
            lyrics.append(parsed_text)
    return lyrics

#   Path to the MEI files and variable setup
auxPitch = pitch.Pitch('C')
mei_path = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Datasets/PTOnly'
f_path = []
i=0
n_files = 5
songs = []

ATSongs = ['A Barca Virou', 'Lá Vai Uma Lá Vão Duas', 'Senhora D. Anica', 'Pantaleão',
           'Passa, Passa, Gabriel', 'Ó Terrá, Tá, Tá', 'Que Linda Falua',
           'Fui Ao Jardim Da Celeste', 'Marcha Soldado', 'Rosa Branca Ao Peito',
           'A Rolinha, Andou, Andou', 'Disse O Galo Prá Galinha', 'Teresinha de Jesus',
           'Os Passarinhos', 'Lá Vai O Comboio, Lá Vai', "Sant'Antóino Se Levantou",
           'Senhores Donos da Casa']

#   Iteration through all the MEI files

outfileName = input("What will the output file name be? ")

for (dirpath, dirnames, filenames) in walk(mei_path):
    for f in filenames:
        print("File %d out of %d" %(i+1, len(filenames)))
        f_path.append(dirpath + '/' + f)
        if i < len(filenames): 
        #if i < n_files:
            to_parse = mei_to_mtc(f_path[i], f)
            isit = input("To Parse "+to_parse['title']+"?")
            
            if isit == 'y':    
                songs.append(to_parse)
                if 'mei' in s:
                    s.pop('mei')
                json_string = json.dumps(songs[-1])
                with open(outfileName + '.json', 'a', encoding='utf8') as outfile:
                    outfile.write(json_string)
                    #json.dump(str(songs[i]), outfile, indent=4, sort_keys=True, ensure_ascii=False)
                    outfile.write('\n')
        else:
            break
        i += 1
    break

"""
f = open("example.xml", "w")
f.write(x[0]['xml'])
f.close()
"""

    #music21_object = converter.parse(f_path[i])
    #aux_key = music21_object.analyze('key')
    #print(aux_key)
    #array.append(getattr(aux_key, 'name'))