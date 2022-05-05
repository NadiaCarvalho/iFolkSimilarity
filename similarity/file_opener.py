# -*- coding: utf-8 -*-
"""
Created on Mon May  2 18:53:41 2022

@author: Daniel Diogo
"""
import ast
import json
# 2604 is the file with the "" before and after each song feature array
# 0205 is the file without the "" before and after each song feature array

#jsonPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/jsons/ifolk2604.json'
#jsonPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/jsons/ifolk0205.json'
jsonPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ifolk0505.json'


def loadFeatures(filePath):
    songFeatures = []
    f = open(filePath, "r")
    fileLines = f.readlines()

    for line in fileLines:
        songFeatures.append(json.loads(line))
    
    return songFeatures

songs = loadFeatures(jsonPath)