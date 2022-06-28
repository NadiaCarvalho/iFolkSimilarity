# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 14:12:27 2022

@author: Daniel Diogo
"""

import json
from fractions import Fraction

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
        
        for feature in seq1:
            if seq1[feature][i] == None:
                seq1[feature][i] = 0
        
        
        if "PITCH" in elements:
            if "MIDI" in elements:
                seq1aux[i].append(seq1['midipitch'][i])
            else:
                seq1aux[i].append(seq1['pitch'][i])
        
        if "DUR" in elements:
            seq1aux[i].append(seq1['duration'][i])
        
        if "INT" in elements:
            if seq1['chromaticinterval'][i] == None:
                aux = 0
            else:
                aux = seq1['chromaticinterval'][i]
            seq1aux[i].append(aux)
        
        if "IOI" in elements:
            if seq1['IOI'][i] == None:
                aux = 0
            else:
                aux = seq1['IOI'][i]
            seq1aux[i].append(aux)
        
        
        if "TS" in elements:
            seq1aux[i].append(Fraction(seq1['timesignature'][i]))
            
        if "DUR_FRAC" in elements:
            seq1aux[i].append(Fraction(seq1['duration_frac'][i]))
        
        if "DIATONIC" in elements:
            seq1aux[i].append(seq1['diatonicpitch'][i])
        
        if "ONSET" in elements:
            seq1aux[i].append(seq1['onsettick'][i])
        
        if "OFFSET" in elements:
            seq1aux[i].append(Fraction(seq1['offsets'][i]))
        
        if "BSTR" in elements:
            seq1aux[i].append(seq1['beatstrength'][i])
            
        if "BEAT" in elements:
            seq1aux[i].append(seq1['beat'][i])
        
        if "TONIC" in elements:
            tRes = 0
            for t in seq1['tonic'][i]:
                tRes += ord(t)
            
            seq1aux[i].append(tRes)
        
        if "MODE" in elements:
            mRes = 0
            for m in seq1['mode'][i]:
                mRes += ord(m)
            
            seq1aux[i].append(mRes)
        
    
    for i in range(size2):
        seq2aux.append([])
        """
        for feature in seq2:
            if not isinstance(seq2[feature][i], (int,float)):
                seq2[feature] = unNumberedToInt(seq2[feature])
        """
        
        if "PITCH" in elements:
            if "MIDI" in elements:
                seq2aux[i].append(seq2['midipitch'][i])
            else:
                seq2aux[i].append(seq2['pitch'][i])
        
        if "DUR" in elements:
            seq2aux[i].append(float(seq2['duration'][i]))
        
        if "INT" in elements:
            if seq2['chromaticinterval'][i] == None:
                aux = 0
            else:
                aux = seq2['chromaticinterval'][i]
            seq2aux[i].append(aux)
        
        if "IOI" in elements:
            if seq2['IOI'][i] == None:
                aux = 0
            else:
                aux = seq2['IOI'][i]
            seq2aux[i].append(aux)
        
        if "TS" in elements:
            seq2aux[i].append(Fraction(seq2['timesignature'][i]))
            
        if "DUR_FRAC" in elements:
            seq2aux[i].append(Fraction(seq2['duration_frac'][i]))
        
        if "DIATONIC" in elements:
            seq2aux[i].append(seq2['diatonicpitch'][i])
        
        if "ONSET" in elements:
            seq2aux[i].append(seq2['onsettick'][i])
        
        if "OFFSET" in elements:
            seq2aux[i].append(Fraction(seq2['offsets'][i]))
        
        if "BSTR" in elements:
            seq2aux[i].append(seq2['beatstrength'][i])
            
        if "BEAT" in elements:
            seq2aux[i].append(seq2['beat'][i])
        
        if "TONIC" in elements:
            tRes = 0
            for t in seq2['tonic'][i]:
                tRes += ord(t)
            
            seq2aux[i].append(tRes)
        
        if "MODE" in elements:
            mRes = 0
            for m in seq2['mode'][i]:
                mRes += ord(m)
            
            seq2aux[i].append(mRes)
        
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
