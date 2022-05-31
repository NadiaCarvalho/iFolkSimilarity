# -*- coding: utf-8 -*-
"""
Created on Thu May 12 11:03:36 2022

@author: User
"""

"""
ws(k)={2, 11, 17, 16, 19, 7}
"""

from TIVlib import TIV as tiv
from scipy import spatial
from collections import Counter
import json

jsonPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ifolk2405.json'

def loadFeatures(filePath):
    songFeatures = []
    f = open(filePath, "r")
    fileLines = f.readlines()

    for line in fileLines:
        songFeatures.append(json.loads(line))
    
    return songFeatures

def sortByDist(pitchDist):
    return pitchDist[1]

def sortByIndex(pitchDist):
    return pitchDist[0]

# Beat Reduction Functions

def getBeatArray(song):
    
    beatArray = []
    songLength = len(song['features']['beatstrength'])
    
    for i in range(songLength):
        beatArray.append((i, song['features']['beatstrength'][i]))
    
    return beatArray

def getBeatReduction(song, thresh):
    """
    thresh: threshold above which notes are taken into account (0.25, 0.5, 1)
    """
    beatsAbove = []
    beatArray = getBeatArray(song)
    
    for beat in beatArray:
        if beat[1] > thresh:
            beatsAbove.append(beat)
     
    return beatsAbove
    

# TIV Reduction Functions
    
def getDist(midiPitches, dist):
    """
    midiPitches: pitches to calculate the distance
    dist: method to use as distance measuring (euclidian or cosine)
    """
    auxHist = Counter(midiPitches)
    pitchClasses = [0] * 12
    
    for pitch in auxHist:
        index = pitch % 12
        pitchClasses[index] += auxHist[pitch]
    
    songTIV = tiv.from_pcp(pitchClasses)
    
    distArray = []
    
    songLength = len(midiPitches)
    
    for i in range(songLength):
        
        pitch = midiPitches[i]
        
        aux = [0] * 12
        aux[pitch % 12] += 1
        aux = tiv.from_pcp(aux)
        
        calcDist = dist(songTIV.vector, aux.vector)
        distArray.append((i,calcDist))
    
    return distArray

def getTivReduction(midiPitches, dist, level):
    """
    level: level of reduction wanted (0.25, 0.50 or 0.75)
    """
    
    distArray = getDist(midiPitches, dist) 
    songLength = len(distArray)
    
    distArray.sort(key=sortByDist)
    portion = round(songLength * level)
    
    reducted = distArray[:portion]
    
    return reducted

# Total Weighted Reduction Functions

def getWeightedArray(tonal, beat, tonalWeight):
    
    beatWeight = 1 - tonalWeight
    distArray = [tone[1] for tone in tonal]
    maxDist = max(distArray)
    if maxDist == 0:
        maxDist = 1
    weighted = []
    
    for i in range(len(tonal)):
        
        tonalAux = 1 - (tonal[i][1]/maxDist)    
        
        weightedValue = tonalWeight * tonalAux + beatWeight * beat[i][1]
        weighted.append((i, weightedValue))
    
    return weighted
    
def getTotalReduction(tonal, beat, tonalWeight, level):
    
    totalArray = getWeightedArray(tonal, beat, tonalWeight)
    
    songLength = len(totalArray)
    
    totalArray.sort(key=sortByDist)
    portion = round(songLength * level)
    
    reducted = totalArray[:portion]
    
    return reducted

""" MAIN STARTS HERE """

songs = loadFeatures(jsonPath)
pitchClasses = {}
reducted = {}

# Debugging
noMeasure = []
for song in songs:
    for beat in song['features']['beatstrength']:
        if beat == None:
            noMeasure.append(song)
            break
        
for song in songs:
    songID = song['name'][67:]
    reducted[songID] = {}
    
    
    print(songs.index(song))
    
    portion = 25
    
    reducted[songID]['TIV'] = {}
    reducted[songID]['TIV']['Euclidean'] = {}
    reducted[songID]['TIV']['Cosine'] = {}
    
    reducted[songID]['Metric'] = {}
    
    reducted[songID]['Both'] = {}
    reducted[songID]['Both']['Euclidean'] = {}
    reducted[songID]['Both']['Cosine'] = {}    
    
    auxToneEuc = getDist(song['features']['midipitch'], spatial.distance.euclidean)
    auxToneCos = getDist(song['features']['midipitch'], spatial.distance.cosine)
    auxBeat = getBeatArray(song)
    
    for portion in range(25,100,25):
        
        portion = portion/100
        
        reducted[songID]['TIV']['Euclidean'][portion] = getTivReduction(song['features']['midipitch'], spatial.distance.euclidean, portion)
        reducted[songID]['TIV']['Cosine'][portion] = getTivReduction(song['features']['midipitch'], spatial.distance.cosine, portion)
        
        reducted[songID]['Metric'][portion] = getBeatReduction(song, portion)
        
        reducted[songID]['Both']['Euclidean'][str(portion) + '% Tone'] = {}
        reducted[songID]['Both']['Cosine'][str(portion) + '% Tone'] = {}
        
        for subPortion in range(25,100,25):
            
            subPortion = subPortion/100
            
            reducted[songID]['Both']['Cosine'][str(portion) + '% Tone'][subPortion] = getTotalReduction(auxToneCos, auxBeat, portion, subPortion)
            reducted[songID]['Both']['Euclidean'][str(portion) + '% Tone'][subPortion] = getTotalReduction(auxToneEuc, auxBeat, portion, subPortion)
   

json_string = json.dumps(reducted)

with open('reductedSongs.json', 'w', encoding='utf8') as outfile:
    outfile.write(json_string)
    