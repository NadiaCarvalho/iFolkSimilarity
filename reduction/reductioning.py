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

jsonPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ptParsingAnnotToolRight.json'

# Help Functions

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

def normalizeTup(tupVec):
    
    vec = [t[1] for t in tupVec]
    maxVec = max(vec)
    minVec = min(vec)
    
    if maxVec == 0:
        maxVec = 1
    
    normal = [(v - minVec) for v in vec]
    normal = [(v/maxVec) for v in vec]
    
    return normal

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
        if beat[1] >= thresh:
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

# Intervallic Reduction Functions

def getIntervals(song):
    
    intervals = []
    songLength = len(song['features']['chromaticinterval'])
    
    for i in range(songLength):
        interval = song['features']['chromaticinterval'][i]
        
        if interval == None:
            interval = 0
            
        intervals.append((i, abs(interval)))
    
    return intervals

def getIntervallicReduc(song, level):
    """
    level: level of reduction wanted (0.25, 0.50 or 0.75)
    """
    
    intervals = getIntervals(song)
    songLength = len(intervals)
    
    intervals.sort(key=sortByDist)
    intervals.reverse()
    portion = round(songLength * level)
    
    reducted = intervals[:portion]
 
    return reducted


# Totality of Reduction Functions Combined

def getCombinedArray(tonal, beat, inter):
    
    interVec = normalizeTup(inter)
    tonalVec = normalizeTup(tonal)
    tonalVec = [(1 - t) for t in tonalVec]
    combined = []
    
    for i in range(len(tonal)):
        combinedValue = (interVec[i] + tonalVec[i] + beat[i][1])/3
        combined.append((i,combinedValue))
    
    return combined
    
def getCombinedReduction(tonal, beat, inter, level):
    
    totalArray = getCombinedArray(tonal, beat, inter)
    
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
    
    if song['alt_title'] == 'Voz 2':
        songID = songID + '-vox2'
    
    reducted[songID] = {}
    
    
    
    print(songs.index(song)+1)
    
    portion = 25
    
    reducted[songID]['TIV'] = {}
    reducted[songID]['TIV']['Euclidean'] = {}
    reducted[songID]['TIV']['Cosine'] = {}
    
    reducted[songID]['Metric'] = {}
    
    reducted[songID]['Intervallic'] = {}
    
    reducted[songID]['All'] = {}
    reducted[songID]['All']['Euclidean'] = {}
    reducted[songID]['All']['Cosine'] = {}
    
    auxToneEuc = getDist(song['features']['midipitch'], spatial.distance.euclidean)
    auxToneCos = getDist(song['features']['midipitch'], spatial.distance.cosine)
    auxBeat = getBeatArray(song)
    auxInter = getIntervals(song)
    
    for portion in range(75,0,-25):
        
        portion = portion/100
        
        reducted[songID]['Metric'][portion] = getBeatReduction(song, 1-portion)
        
        reducted[songID]['Intervallic'][portion] = getIntervallicReduc(song, portion)
        
        reducted[songID]['TIV']['Cosine'][portion] = getTivReduction(song['features']['midipitch'], spatial.distance.cosine, portion)
        reducted[songID]['TIV']['Euclidean'][portion] = getTivReduction(song['features']['midipitch'], spatial.distance.euclidean, portion)
                
        reducted[songID]['All']['Cosine'][portion] = getCombinedReduction(auxToneCos, auxBeat, auxInter, portion)
        reducted[songID]['All']['Euclidean'][portion] = getCombinedReduction(auxToneEuc, auxBeat, auxInter, portion)
   

json_string = json.dumps(reducted)

with open('reductedSongsPTAnnotTool.json', 'w', encoding='utf8') as outfile:
    outfile.write(json_string)
    