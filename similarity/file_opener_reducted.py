# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 18:59:10 2022

@author: Daniel Diogo
"""
import json
import similarity_metrics as sim

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

iFolkPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ifolk1406.json'
iFolkReductedPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ifolk1406reducted.json'



""" MAIN STARTS HERE """
reductedSongs1 = loadReductedSongs(iFolkReductedPath)
iFolkSongs1 = loadSongs(iFolkPath)

for song in iFolkSongs1:
    songID = song['name'][67:]
    reductedSong = reductedSongs1[songID]
