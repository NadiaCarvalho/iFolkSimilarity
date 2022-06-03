# -*- coding: utf-8 -*-
"""
Created on Wed May 25 18:08:11 2022

@author: Daniel Diogo
"""
import sys
sys.path.append('C:/Users/User/Documents/Faculdade/5_Ano/2_Semestre/Python_Workstation/iFolkSimilarity/parsing')

import json
from music21 import *
import m21StreamToDS as kranen

reducPath = 'reductedSongs.json'
json_path = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ifolk2405.json'

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
    
    s = stream.Stream()
    p = stream.Part()
    m = stream.Measure(number=0)
    mNumber = 0
    
    indexes = [tup[0] for tup in indexes]
    feat = thisSong['features']

    for i in range(len(feat['duration'])):
        
        if feat['beatstrength'][i] == 1:
            
            if m.elements:
                p.append(m)
            
            mNumber += 1
            m = stream.Measure(number=mNumber)
            m.timeSignature = meter.TimeSignature(feat['timesignature'][i]) 
        
        if i in indexes:
            newElement = note.Note(feat['pitch'][i])
            newElement.duration.quarterLength = feat['duration'][i]
        else:
            newElement = note.Rest(feat['duration'][i])
        
        m.append(newElement)
        
    s.append(p)
        
    return s


""" MAIN STARTS HERE """

reductedSongs = loadReductedSongs(reducPath)
iFolkSongs = loadSongs(json_path)
m21reduc = {}

for i in range(len(iFolkSongs)):
    
    thisSong = iFolkSongs[i]
    songID = iFolkSongs[i]['name'][67:]
    m21reduc[songID] = {}
    
    meta = {}
    
    for label in thisSong:
        if label == 'features':
            break
        else:
            meta[label] = thisSong[label]
    
    showThis = False
    
    if 'PT' == songID[0:2]:
       # if "Barca" in thisSong['title']:
       #     showThis = False
        
        for cat in reductedSongs[songID]:
            m21reduc[songID][cat] = {}
            
            if (cat == 'Both') or (cat == 'TIV'):
                for distType in reductedSongs[songID][cat]:
                    m21reduc[songID][cat][distType] = {}
                    
                    if cat == 'All':
                            
                        for portion in reductedSongs[songID][cat][distType]:
                            auxStream = reductByIndex(thisSong, reductedSongs[songID][cat][distType][portion])
                            m21reduc[songID][cat][distType][portion] = kranen.m21StreamToDS(auxStream, meta)
                            
                            if showThis == True:
                                m21reduc[songID][cat][distType][portion].show()
    
                    if cat == 'TIV':
                        for portion in reductedSongs[songID][cat][distType]:
                            auxStream = reductByIndex(thisSong, reductedSongs[songID][cat][distType][portion])
                            m21reduc[songID][cat][distType][portion] = kranen.m21StreamToDS(auxStream, meta)
                            
                            if showThis == True:
                                m21reduc[songID][cat][distType][portion].show()
    
            else:
               for portion in reductedSongs[songID][cat]:
                   auxStream = reductByIndex(thisSong, reductedSongs[songID][cat][portion])
                   m21reduc[songID][cat][portion] = kranen.m21StreamToDS(auxStream, meta)
                   
                   if showThis == True:
                       m21reduc[songID][cat][distType][portion].show()

json_string = json.dumps(m21reduc)

with open('reductedSongsDataStructure.json', 'w', encoding='utf8') as outfile:
    outfile.write(json_string)
