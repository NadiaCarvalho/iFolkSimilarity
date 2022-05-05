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
mei_path = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Datasets/I-Folk'
f_path = []
i=0
n_files = 5
songs = []

#   Iteration through all the MEI files

outfileName = input("What will the output file name be? ")

for (dirpath, dirnames, filenames) in walk(mei_path):
    for f in filenames:
        print("File %d out of %d" %(i+1, len(filenames)))
        f_path.append(dirpath + '/' + f)
        if i < len(filenames): 
        #if i < n_files:
            songs.append(mei_to_mtc(f_path[i], f))
            songs[i].pop('mei')
            json_string = json.dumps(songs[i])
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
    