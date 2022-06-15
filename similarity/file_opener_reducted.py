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

def unNumberedToInt(array):
    aux = list(set(array))
    arraySize = len(array)
    for i in range(arraySize):
        array[i] = aux.index(array[i]) 
    return array

def similar(seq1, seq2, elements, algorithm):
    
    size1 = len(seq1['pitch'])
    seq1aux = []

    size2 = len(seq2['pitch'])
    seq2aux = []
    
    for i in range(size1):
        seq1aux.append([])
        
        if "ALL" in elements:
                seq1aux[i].append(seq1['midipitch'][i])
                seq1aux[i].append(seq1['duration'][i])
                seq1aux[i].append(seq1['onsettick'][i])
                seq1aux[i].append(seq1['beatstrength'][i])
                seq1aux[i].append(seq1['contour5'][i])
        
        if "PITCH" in elements:
            if "MIDI" in elements:
                seq1aux[i].append(seq1['midipitch'][i])
            else:
                seq1aux[i].append(seq1['pitch'][i])
        
        if "DUR" in elements:
            seq1aux[i].append(seq1['duration'][i])
        
        if "ONSET" in elements:
            seq1aux[i].append(seq1['onsettick'][i])
        
        if "IMAWEIGTH" in elements:
            seq1aux[i].append(seq1['imaweight'][i])
            
        if "BEAT" in elements:
            seq1aux[i].append(seq1['beat'][i])
    
    for j in range(size2):
        seq2aux.append([])
        
        if "ALL" in elements:
            for feature in seq2:
                if not isinstance(seq2[feature][j], (int,float)):
                    seq2[feature] = unNumberedToInt(seq2[feature])
                    
                seq2aux[j].append(seq2[feature][j])
        
        if "PITCH" in elements:
            if "MIDI" in elements:
                seq2aux[j].append(seq2['midipitch'][j])
            else:
                seq2aux[j].append(seq2['pitch'][j])
        
        if "DUR" in elements:
            seq2aux[j].append(seq2['duration'][j])
        
        if "ONSET" in elements:
            seq2aux[j].append(seq2['onsettick'][j])
        
        if "IMAWEIGTH" in elements:
            seq2aux[j].append(seq2['imaweight'][j])
            
        if "BEAT" in elements:
            seq2aux[j].append(seq2['beat'][j])
        
    return algorithm(seq1aux, seq2aux)

iFolkPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ifolk1406.json'
iFolkReductedPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ifolk1406reducted.json'



""" MAIN STARTS HERE """
reductedSongs1 = loadReductedSongs(iFolkReductedPath)
iFolkSongs1 = loadSongs(iFolkPath)
simValues = {}

for song1 in iFolkSongs1:
    song1ID = song1['name'][67:]
    reductedSong = reductedSongs1[song1ID]
    seq1 = song1['features']
    
    simValues[song1ID] = {}
    
    for song2 in iFolkSongs1:
        
        song2ID = song2['name'][67:]
        seq2 = song2['features']
        
        simValues[song1ID][song2ID] = {}
        
        simValues[song2ID]['SIAM'] = similar(seq1, seq2, "ALL", sim.SIAM)
        simValues[song2ID]['Local Alignment'] = similar(seq1, seq2, "ALL", sim.local_alignment)
        
        simValues[song2ID]['City Block'] = similar(seq1, seq2, "MIDIPITCH", sim.city_block_distance)
        simValues[song2ID]['Euclidean'] = similar(seq1, seq2, "MIDIPITCH", sim.euclidean_distance)
        simValues[song2ID]['Hamming'] = similar(seq1, seq2, "MIDIPITCH", sim.hamming_distance)
        
        simValues[song2ID]['Correlation'] = similar(seq1, seq2, "DUR MIDIPITCH", sim.correlation)
        simValues[song2ID]['Cardinality'] = similar(seq1, seq2, "DUR MIDIPITCH", sim.cardinality_score)
        
