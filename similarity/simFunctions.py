# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 14:12:27 2022

@author: Daniel Diogo
"""

import json

def loadFeatures(filePath):
    songFeatures = []
    f = open(filePath, "r")
    fileLines = f.readlines()

    for line in fileLines:
        songFeatures.append(json.loads(line))
    
    return songFeatures

def loadReductedSongs(filePath):
    songReductions = {}
    f = open(filePath, "r")
    fileLines = f.readlines()

    for line in fileLines:
        songReductions = json.loads(line)
    
    return songReductions

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
            for feature in seq1:
                if not isinstance(seq1[feature][i], (int,float)):
                    seq1[feature] = unNumberedToInt(seq1[feature])
                
                seq1aux[i].append(seq1[feature][i])
        
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
            
        if "BEATSTR" in elements:
            seq2aux[j].append(seq2['beatstrength'][j])
        
    return algorithm(seq1aux, seq2aux)

def show_results(results):
    print("Cardinality Score: " + str(results[0]))
    print("Correlation Distance: " + str(results[1]))
    print("City Block Distance: " + str(results[2]))
    print("Euclidean Distance: " + str(results[3]))
    print("Hamming Distance: " + str(results[4]))
    print("Local Alignment Score: " + str(results[5]))
    print("Structure Induction Matching Algorithm Score': " + str(results[6]))
    #print("Implication-Realization Structure Alignment Score: " + str(results[7]))
    print()
