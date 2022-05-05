# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 10:42:04 2022

@author: User
"""

#f = open("portuguese_xml/"+meta['genre']+f[15:17]+".musicxml", "w")
#f.write(aux[2])

from music21 import *
environment.set('musescoreDirectPNGPath', 'C:\\Program Files\\MuseScore 3\\bin\\MuseScore3.exe')
#import json_generator
from os import walk
import string
from json_generator import *
import mei_parsing as mei
import json

mei_path = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Datasets/I-Folk'
f_path = []
genres = {}
allPhrases = {}
nMetric = {
    'Binary' : 0,
    'Ternary' : 0
    }
nTimeSignature = {}

i = 0
#   Iteration through all the MEI files

for (dirpath, dirnames, filenames) in walk(mei_path):
    for f in filenames:
        #print(dirpath + '/' + f)
        f_path.append(dirpath + '/' + f)
        meta = mei.parseSongMetadata(f_path[i])
        
        if meta['country'] == 'Portugal':
            if meta['genre'] == 'Children song':
                if meta['meter'] in nMetric:
                    nMetric[meta['meter']] += 1
                    if(meta['meter'] == 'Binary' and nMetric[meta['meter']] < 14):
                        print('Title: ' + meta['title'])
                        print('Country: ' + meta['country'])
                        print('Meter: ' + meta['meter'])
                        print('Time Signature: ' + meta['time_signature'])
                        print('Genre: ' + meta['genre'])
                        print()
                        allPhrases[meta['title']] = meta['phrases']    
                        musicXML = mei.musicXMLFromMEI(f_path[i], meta)
                        #musicXML[3].show()
                        choice = input('Get midi and png file? (y/n) ')
                        if choice == 'y':
                            musicXML[3].write('musicxml.png', fp= 'pdf_files/' + meta['meter'] + '/' +  str(nMetric[meta['meter']]) + '.pdf')
                            musicXML[3].write('midi', fp= 'pdf_files/'+ meta['meter'] + '/' + str(nMetric[meta['meter']]) + '.midi')
                            #print(meta['title'])
                        print()
                    #if meta['time_signature'] in nTimeSignature:
                    #    nTimeSignature[meta['time_signature']] += 1
                    #else:
                    #   nTimeSignature[meta['time_signature']] = 1
                    #for n in musicXML[3].flat.notes:
                     #   for phrase in meta['phrases']:
                      #      if(n.id == meta['phrases'][phrase]['start'][1:]):
                       #         if(n.lyric != None):
                                    #print("Start of the phrase: " + n.nameWithOctave + n.lyric)
                        #        else:
                                    #print("Start of the phrase: " + n.nameWithOctave)
                         #   if(n.id == meta['phrases'][phrase]['end'][1:]):
                          #      if(n.lyric != None):
                                    #print("End of the phrase: " + n.nameWithOctave + n.lyric)
                           #     else:
                                    #print("End of the phrase: " + n.nameWithOctave)
                    #print()
                    #if(genres[meta['genre']] == 30):
                     #   musicXML[3].show()
                    
        i += 1