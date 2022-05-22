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

jsonPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ifolk0505.json'

def loadFeatures(filePath):
    songFeatures = []
    f = open(filePath, "r")
    fileLines = f.readlines()

    for line in fileLines:
        songFeatures.append(json.loads(line))
    
    return songFeatures

def sortByDist(pitchDist):
    return pitchDist['Dist']

def sortByIndex(pitchDist):
    return pitchDist['Index']

def getBeatReduction(song, thresh):
    """
    thresh: threshold above which notes are taken into account (0.25, 0.5, 1)
    """
    indexes = []
    songLength = len(song['features']['beatstrength'])
    for i in range(songLength):
        bs = song['features']['beatstrength'][i]
        if bs > thresh:
            indexes.append(i)
    return indexes

def reductSong(song, indexes):
    songLength = len(song['features']['midipitch'])
    
    for i in range(songLength):
        if i not in indexes:
            for feature in song['features']:
                song['features'][feature].pop(i)
    
    return song
    
    
def getTivReduction(midiPitches, dist, level):
    """
    midiPitches: pitches to calculate the distance
    level: level of reduction wanted in percentage (25, 50 or 75)
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
        distArray.append({"Index": i, "Pitch": pitch, "Dist": calcDist})
    
    distArray.sort(key=sortByDist)
    portion = round(songLength * (level/100))
    
    reducted = distArray[:portion]
    
    return reducted
    
""" MAIN STARTS HERE """

notes = {
    'C': 0,
    'D': 2,
    'E': 4,
    'F': 5,
    'G': 7,
    'A': 9,
    'B': 11,
    '+': 1,
    '-': -1
    }

songs = loadFeatures(jsonPath)
pitchClasses = {}
tivInfo = {}

for song in songs:
    songID = song['name'][67:]
    tivInfo[songID] = {}
    
    portion = 25
    
    while portion < 100:
        tivInfo[songID][portion] = {}
        tivInfo[songID][portion]['Euclidean'] = getTivReduction(song['features']['midipitch'], spatial.distance.euclidean, portion)
        tivInfo[songID][portion]['Cosine'] = getTivReduction(song['features']['midipitch'], spatial.distance.cosine, portion)
    
        portion += 25
    
    
        
    