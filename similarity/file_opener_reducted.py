# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 18:59:10 2022

@author: Daniel Diogo
"""
import json
import similarity_metrics as sim
import simFunctions as simF

iFolkPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ifolk1406.json'
iFolkReductedPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ifolk1406reducted.json'



""" MAIN STARTS HERE """
reductedSongs1 = simF.loadReductedSongs(iFolkReductedPath)
iFolkSongs1 = simF.loadSongs(iFolkPath)
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
        
        simValues[song2ID]['SIAM'] = simF.similar(seq1, seq2, "ALL", sim.SIAM)
        simValues[song2ID]['Local Alignment'] = simF.similar(seq1, seq2, "ALL", sim.local_alignment)
        
        simValues[song2ID]['City Block'] = simF.similar(seq1, seq2, "MIDIPITCH", sim.city_block_distance)
        simValues[song2ID]['Euclidean'] = simF.similar(seq1, seq2, "MIDIPITCH", sim.euclidean_distance)
        simValues[song2ID]['Hamming'] = simF.similar(seq1, seq2, "MIDIPITCH", sim.hamming_distance)
        
        simValues[song2ID]['Correlation'] = simF.similar(seq1, seq2, "DUR MIDIPITCH", sim.correlation)
        simValues[song2ID]['Cardinality'] = simF.similar(seq1, seq2, "DUR MIDIPITCH", sim.cardinality_score)
        
