# -*- coding: utf-8 -*-
"""
Created on Thu May 12 11:03:36 2022

@author: User
"""

"""
ws(k)={2, 11, 17, 16, 19, 7}
"""

from TIVlib import TIV as tiv
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

""" MAIN STARTS HERE """
#             C C+  D D+  E  F F+  G G+  A A+  B


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

for song in songs:
    auxHist = Counter(song['features']['pitch'])
    songId = song['name'][67:]
    pitchClasses[songId] = [0] * 12
    for pitch in auxHist:
        index = 0
        for char in pitch:
            if char in notes:
                index += notes[char]
        pitchClasses[songId][index] += auxHist[pitch]
