# -*- coding: utf-8 -*-
"""
Created on Wed May 25 18:08:11 2022

@author: Daniel Diogo
"""
import sys
sys.path.append('C:/Users/User/Documents/Faculdade/5_Ano/2_Semestre/Python_Workstation/iFolkSimilarity/parsing')

import json
from music21 import *
import json_generator2 as kranen
from fractions import Fraction

reducPath = 'reductedSongsPTAnnotTool.json'
json_path = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ptParsingAnnotToolRight.json'

def loadReductedSongs(filePath):
    songReductions = {}
    f = open(filePath, "r")
    fileLines = f.readlines()

    for line in fileLines:
        songReductions = json.loads(line)
    
    return songReductions

def loadSongs(filePath):
    songFeatures = []
    f = open(filePath, "r")
    fileLines = f.readlines()

    for line in fileLines:
        songFeatures.append(json.loads(line))
    
    return songFeatures

def reductByIndex(thisSong, indexes):
    
    #Debugging
    #print(thisSong['name'][67:])
    
    s = stream.Part()
    
    if 'time_change' in thisSong:
        for ts in thisSong['time_change']:
            newTS = meter.TimeSignature(ts[1])
            s.append(newTS)
            s.elements[-1].offset = ts[0]
    else:
        if thisSong['freemeter'] == False:
            s.timeSignature = meter.TimeSignature(thisSong['time_signature'])
    
    indexes = [tup[0] for tup in indexes]
    feat = thisSong['features']

    if (float(feat['offsets'][0]) != 0.0):
        firstRest = note.Rest(quarterLength = Fraction(feat['offsets'][0]))
        s.append(firstRest)

    for i in range(len(feat['duration'])):
        
        if i in indexes:
            newElement = note.Note(feat['pitch'][i], quarterLength = feat['duration'][i])
        else:
            newElement = note.Rest(quarterLength = feat['duration'][i])
            
        s.append(newElement)
        s.elements[-1].offset = Fraction(feat['offsets'][i])

    #Debugging
    #s.show()    
    
    return s.flat


""" MAIN STARTS HERE """

reductedSongs = loadReductedSongs(reducPath)
iFolkSongs = loadSongs(json_path)
m21reduc = {}

for i in range(len(iFolkSongs)):
    print(i+1)
    
    thisSong = iFolkSongs[i]
    songID = iFolkSongs[i]['name'][67:]
    
    if thisSong['alt_title'] == 'Voz 2':
        songID = songID + '-vox2'
    
    m21reduc[songID] = {}
    
    meta = {}
    
    for label in thisSong:
        if label == 'features':
            break
        else:
            meta[label] = thisSong[label]
    
    showThis = False
    
    enter = True
    """
    if ("Barca" in thisSong['title']) or ("Rolinha" in thisSong['title']):
        if "PT" == songID[:2]:
            enter = True
        else:
            enter = False
    else:
        enter = False
    """
    if enter == True:
       # if "Barca" in thisSong['title']:
       #     showThis = False
        
        print(thisSong['title'])
        
        for cat in reductedSongs[songID]:
            m21reduc[songID][cat] = {}
            
            if (cat == 'All') or (cat == 'TIV'):
                for distType in reductedSongs[songID][cat]:
                    m21reduc[songID][cat][distType] = {}
                    
                    if cat == 'All':
                            
                        for portion in reductedSongs[songID][cat][distType]:
                            print(songID)
                            print(cat)
                            print(distType)
                            print(portion)
                            print()
                            auxStream = reductByIndex(thisSong, reductedSongs[songID][cat][distType][portion])
                            m21reduc[songID][cat][distType][portion] = kranen.m21StreamToDS(auxStream, meta, thisSong)
                            
                            if showThis == True:
                                m21reduc[songID][cat][distType][portion].show()
    
                    if cat == 'TIV':
                        for portion in reductedSongs[songID][cat][distType]:
                            print(songID)
                            print(cat)
                            print(distType)
                            print(portion)
                            print()
                            auxStream = reductByIndex(thisSong, reductedSongs[songID][cat][distType][portion])
                            m21reduc[songID][cat][distType][portion] = kranen.m21StreamToDS(auxStream, meta, thisSong)
                            
                            if showThis == True:
                                m21reduc[songID][cat][distType][portion].show()
    
            else:
               for portion in reductedSongs[songID][cat]:
                   print(songID)
                   print(cat)
                   print(portion)
                   print()
                   auxStream = reductByIndex(thisSong, reductedSongs[songID][cat][portion])
                   m21reduc[songID][cat][portion] = kranen.m21StreamToDS(auxStream, meta, thisSong)
                   
                   if showThis == True:
                       m21reduc[songID][cat][distType][portion].show()

    json_string = json.dumps(m21reduc[songID])

    with open('reductedSongs-AT-PT-m21.json', 'a', encoding='utf8') as outfile:
        outfile.write(json_string)
        outfile.write('\n')
