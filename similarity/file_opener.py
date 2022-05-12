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

def similar(seq1, seq2, elements, algorithm):
    
    if "PITCH" in elements:
        if "DUR" in elements:
            if "MIDI" in elements:
                seq1aux = [[seq1['midipitch'][i], seq1['duration'][i]] for i in range(len(seq1['midipitch']))]
                seq2aux = [[seq2['midipitch'][j], seq2['duration'][j]] for j in range(len(seq2['midipitch']))]
            else:
                seq1aux = [[seq1['pitch'][i], seq1['duration'][i]] for i in range(len(seq1['pitch']))]
                seq2aux = [[seq2['pitch'][j], seq2['duration'][j]] for j in range(len(seq2['pitch']))]
        if "ONSET" in elements:
            if "MIDI" in elements:
                seq1aux = [[seq1['midipitch'][i], seq1['onsettick'][i]] for i in range(len(seq1['midipitch']))]
                seq2aux = [[seq2['midipitch'][j], seq2['onsettick'][j]] for j in range(len(seq2['midipitch']))]
            else:
                seq1aux = [[seq1['pitch'][i], seq1['onsettick'][i]] for i in range(len(seq1['pitch']))]
                seq2aux = [[seq2['pitch'][j], seq2['onsettick'][j]] for j in range(len(seq2['pitch']))]
        
        else:
            if "MIDI" in elements:
                seq1aux = seq1['midipitch']
                seq2aux = seq2['midipitch']
            else:
                seq1aux = seq1['pitch']
                seq2aux = seq2['pitch']

    else:
        print("Function not called properly!")
    
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

""" MAIN STARTS HERE """

songs = loadFeatures(jsonPath)

i = 0
j = 0
filePath = 'C:/Users/User/Documents/Faculdade/5_Ano/2_Semestre/Python_Workstation/iFolkSimilarity/similarity/sim_values'
#f = open(filePath, "w")

simValues = {}

for seq1 in songs: 
    
    seq1Id = seq1['name'][67:]
    seq1 = seq1['features']
        
    
    for seq2 in songs:
        
        seq2Id = seq2['name'][67:]
        seq2 = seq2['features']
        
        simValues[seq2Id] = {}
        
        simValues[seq2Id]['SIAM'] = similar(seq1, seq2, "MIDIPITCH ONSET", sim.SIAM)
        simValues[seq2Id]['Local Alignment'] = similar(seq1, seq2, "PITCH", sim.local_alignment)
        
        simValues[seq2Id]['City BLock'] = similar(seq1, seq2, "MIDIPITCH", sim.city_block_distance)
        simValues[seq2Id]['Euclidean'] = similar(seq1, seq2, "MIDIPITCH", sim.euclidean_distance)
        simValues[seq2Id]['Hamming'] = similar(seq1, seq2, "MIDIPITCH", sim.hamming_distance)
        
        simValues[seq2Id]['Correlation'] = similar(seq1, seq2, "DUR MIDIPITCH", sim.correlation)
        simValues[seq2Id]['Cardinality'] = similar(seq1, seq2, "DUR MIDIPITCH", sim.cardinality_score)
        
        
        #irsa = similar(seq1, seq2, "PITCH", sim.ir_alignment)
        #distanceTuples = sim.match_distance_tuples(seq1, seq2, dist_func)
        #multiDim = sim.multi_dimensional(seq1, seq2, variances)
        
        #show_results([card, corr, cityBlock, euclidean, hamming, la, siam])
        
        
        print("Inner Cycle {}".format(j))
        j+=1
        
    break
    print("Outer Cycle %d", i)    
    i+=1