# -*- coding: utf-8 -*-
"""
Created on Mon May  2 18:53:41 2022

@author: Daniel Diogo
"""

import json
import similarity_metrics as sim
import simFunctions as simF
# 2604 is the file with the "" before and after each song feature array
# 0205 is the file without the "" before and after each song feature array

#jsonPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/jsons/ifolk2604.json'
#jsonPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/jsons/ifolk0205.json'
jsonPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ifolk1406.json'



""" MAIN STARTS HERE """

songs = simF.loadFeatures(jsonPath)
newSongs = []

for song in songs:
    if song['name'][67:69] == 'PT':
        newSongs.append(song)

songs = newSongs

i = 0
j = 0
filePath = 'C:/Users/User/Documents/Faculdade/5_Ano/2_Semestre/Python_Workstation/iFolkSimilarity/similarity/sim_values'
#f = open(filePath, "w")

simValues = {}

for seq1 in songs: 
    
    seq1Id = seq1['name'][67:]
    seq1 = seq1['features']
    
    simValues[seq1Id] = {}
    
    for seq2 in songs:
        
        seq2Id = seq2['name'][67:]
        seq2 = seq2['features']
        
        simValues[seq1Id][seq2Id] = {}
        # Só usar umas 5 features no ALL (ver nos papers)
        simValues[seq1Id][seq2Id]['SIAM'] = simF.similar(seq1, seq2, "ALL", sim.SIAM)
        simValues[seq1Id][seq2Id]['Local Alignment'] = simF.similar(seq1, seq2, "MIDIPITCH", sim.local_alignment)
        
        simValues[seq1Id][seq2Id]['City Block'] = simF.similar(seq1, seq2, "MIDIPITCH", sim.city_block_distance)
        simValues[seq1Id][seq2Id]['Euclidean'] = simF.similar(seq1, seq2, "MIDIPITCH", sim.euclidean_distance)
        simValues[seq1Id][seq2Id]['Hamming'] = simF.similar(seq1, seq2, "MIDIPITCH", sim.hamming_distance)
        simValues[seq1Id][seq2Id]['Correlation'] = simF.similar(seq1, seq2, "MIDIPITCH", sim.correlation)
        
        simValues[seq1Id][seq2Id]['Cardinality'] = simF.similar(seq1, seq2, "MIDIPITCH ONSET", sim.cardinality_score)
        
        # PITCHxCosine
        
        #irsa = similar(seq1, seq2, "PITCH", sim.ir_alignment)
        #distanceTuples = sim.match_distance_tuples(seq1, seq2, dist_func)
        #multiDim = sim.multi_dimensional(seq1, seq2, variances)
        
        #show_results([card, corr, cityBlock, euclidean, hamming, la, siam])
        
        
        #print("Inner Cycle {}".format(j))
        #j+=1
        
    print("Outer Cycle %d", i)
    i+=1
    
json_string = json.dumps(simValues)

with open('simValuesSimple.json', 'w', encoding='utf8') as outfile:
    outfile.write(json_string)