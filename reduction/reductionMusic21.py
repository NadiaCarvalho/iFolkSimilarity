# -*- coding: utf-8 -*-
"""
Created on Wed May 25 18:08:11 2022

@author: Daniel Diogo
"""
import sys
sys.path.append('C:/Users/User/Documents/Faculdade/5_Ano/2_Semestre/Python_Workstation/iFolkSimilarity/parsing')

from os import walk
import json
import json_generator as jsonGen
from music21 import *

reducPath = 'reductedSongs.json'
mei_path = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Datasets/I-Folk'

def loadReductedSongs(filePath):
    songReductions = {}
    f = open(filePath, "r")
    fileLines = f.readlines()

    for line in fileLines:
        songReductions = json.loads(line)
    
    return songReductions

""" MAIN STARTS HERE """

reductedSongs = loadReductedSongs(reducPath)

f_path = []
i = 0

for (dirpath, dirnames, filenames) in walk(mei_path):
    for f in filenames:
        
        print("File %d out of %d" %(i+1, len(filenames)))
        f_path.append(dirpath + '/' + f)
        
        if i < len(filenames): 
            s, meta, xml = jsonGen.parseMelody(f_path[i])
            
            for r in reductedSongs:
                if f[:17] == r:
                    for j in range(len(s.notes)):
                        
                        
                
            
        i += 1