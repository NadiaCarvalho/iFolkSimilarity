# -*- coding: utf-8 -*-
"""
Created on Mon May  2 18:53:41 2022

@author: Daniel Diogo
"""
import ast
import json
import similarity_metrics as sim
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

for prev, curr in zip(songs, songs[1:]):
    
    seq1 = prev['features']['midipitch']
    seq2 = curr['features']['midipitch']

    cardinality = sim.cardinality_score(seq1, seq2)
    cityBlock = sim.city_block_distance(seq1, seq2)
    correlation = sim.correlation(seq1, seq2)
    euclidean = sim.euclidean_distance(seq1, seq2)
    hamming = sim.hamming_distance(seq1, seq2)
    irsa = sim.ir_alignment(seq1, seq2, variances)
    la = sim.local_alignment(seq1, seq2, insert_score, delete_score, sim_score, return_positions)
    distanceTuples = sim.match_distance_tuples(seq1, seq2, dist_func)
    multiDim = sim.multi_dimensional(seq1, seq2, variances)