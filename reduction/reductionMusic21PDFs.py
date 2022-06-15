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

reducPath = 'reductedSongs1406.json'
json_path = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ifolk1406.json'

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

def reductByIndex(thisSong, indexes, partName):
    
    #Debugging
    #print(thisSong['name'][67:])
    
    s = stream.PartStaff()
    s.partAbbreviation = partName
    s.partName = partName
    
    
    if 'time_change' in thisSong:
        for ts in thisSong['time_change']:
            newTS = meter.TimeSignature(ts[1])
            s.append(newTS)
            s.elements[-1].offset = ts[0]
    else:
        if thisSong['freemeter'] == False:
            s.timeSignature = meter.TimeSignature(thisSong['time_signature'])
    
    if indexes == []:
        indexes = [i for i in range(len(thisSong['features']['pitch']))]
    else:    
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
    
    return s


""" MAIN STARTS HERE """

reductedSongs = loadReductedSongs(reducPath)
iFolkSongs = loadSongs(json_path)
m21reduc = {}

for i in range(len(iFolkSongs)):
    print(i+1)
    
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
    
    enter = True
    
    if "PT" == songID[:2]:
        enter = True
    else:
        enter = False
  
    if enter == True:
       # if "Barca" in thisSong['title']:
       #     showThis = False
        
        print(thisSong['title'])
        
        songStream = stream.Score()
        
        
        for cat in reductedSongs[songID]:
            m21reduc[songID][cat] = {}
            
            if (cat == 'All') or (cat == 'TIV'):
                for distType in reductedSongs[songID][cat]:
                    m21reduc[songID][cat][distType] = {}
                    
                    if cat == 'All':
                        
                        auxPS = stream.PartStaff()
                        
                        for portion in reductedSongs[songID][cat][distType]:
                            print(songID)
                            print(cat)
                            print(distType)
                            print(portion)
                            print()
                            auxStream = reductByIndex(thisSong, reductedSongs[songID][cat][distType][portion], str(cat+' '+distType+' '+portion))
                            songStream.append(auxStream)
           
                        auxStream = reductByIndex(thisSong, [], 'Original')
                        songStream.append(auxStream)
    
                    if cat == 'TIV':
                        
                      
                        
                        for portion in reductedSongs[songID][cat][distType]:
                            print(songID)
                            print(cat)
                            print(distType)
                            print(portion)
                            print()
                            auxStream = reductByIndex(thisSong, reductedSongs[songID][cat][distType][portion], str(cat+' '+distType+' '+portion))
                            songStream.append(auxStream)
                        
                        auxStream = reductByIndex(thisSong, [], 'Original')
                        songStream.append(auxStream)
    
            else:
                
                for portion in reductedSongs[songID][cat]:
                   print(songID)
                   print(cat)
                   print(portion)
                   print()
                  
                   auxStream = reductByIndex(thisSong, reductedSongs[songID][cat][portion], str(cat+' '+portion))
                   songStream.append(auxStream)
                       
                auxStream = reductByIndex(thisSong, [], 'Original')
                songStream.append(auxStream)
                
                
        songStream.metadata = metadata.Metadata()
        songStream.metadata.title = thisSong['title']
        songStream.show()