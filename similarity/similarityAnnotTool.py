# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 14:06:41 2022

@author: Daniel Diogo
"""

import csv
import similarity_metrics as sim
import simFunctions as simF
import numpy as np
from scipy.stats import pearsonr

def makeTable(stat, evaluator, simValues, corrValues):
    
    table = [[' '],[],[],[],[],[],[],[]]
    table[0].extend([redLev for redLev in simValues])
    firstColumn = [simMetric for simMetric in corrValues]

    for i in range(len(table)):
        for j in range(len(table[0])):
            if i > 0:
                if j == 0:
                    table[i].append(firstColumn[i-1])
                else:
                    redLevel = table[0][j]
                    simMetric = table[i][0]
                    toAppend = corrValues[simMetric][redLevel][stat][evaluator-1]
                    
                    if type(toAppend) is tuple:

                            if toAppend[1] > 0.05:
                                strToAppend = 'ns'
                            if toAppend[1] <= 0.05:
                                strToAppend = '*'
                            if toAppend[1] <= 0.01:
                                strToAppend = '**'
                            if toAppend[1] <= 0.001:
                                strToAppend = '***'
                            if toAppend[1] <= 0.0001:
                                strToAppend = '****'
                                
                            toAppend = (round(toAppend[0], 3), strToAppend)
                        
                    else:
                        toAppend = round(toAppend,3)
                        
                    table[i].append(toAppend)
    
    
    
    return table

def adjustOrder(arr):
    newOrder = [0,1,2,3,4,5,6,7,8,9,10,16,11,12,13,17,19,18,14,15]
    arr = [arr[i] for i in newOrder]
    return arr

jsonPath = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/ptParsingAnnotToolRight.json'
jsonReduc = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Python_Workstation/iFolkSimilarity/jsons/reductedSongs-AT-PT-m21.json'

""" MAIN STARTS HERE """


comparisons = []
comparisons.append([(0, 1), (2,3), (4,5), (6,7), (8,9), (0,9),(1,2),(3,4),(5,6),(7,8)])
comparisons.append([(10,11), (12,13), (14,15), (16,17), (18,19), (10,19),(11,12),(13,14),(15,16),(17,18)])
comparisons.append([(0,10), (1,11), (2,12), (3,13), (4,14), (5,15),(6,16),(7,17),(8,18),(9,19)])

songs = simF.loadFeatures(jsonPath)
reducSongs = simF.loadFeatures(jsonReduc)

metric = {'25':[], '50':[], '75':[]}
intervallic = {'25':[], '50':[], '75':[]}
tiv = {'Cos':{'25':[], '50':[], '75':[]}, 'Euc':{'25':[], '50':[], '75':[]}}
All = {'Cos':{'25':[], '50':[], '75':[]}, 'Euc':{'25':[], '50':[], '75':[]}}

for r in reducSongs:
    metric['25'].append(r['Metric']['0.25'])
    metric['50'].append(r['Metric']['0.5'])
    metric['75'].append(r['Metric']['0.75'])
    
    intervallic['25'].append(r['Intervallic']['0.25'])
    intervallic['50'].append(r['Intervallic']['0.5'])
    intervallic['75'].append(r['Intervallic']['0.75'])
    
    tiv['Cos']['25'].append(r['TIV']['Cosine']['0.25'])
    tiv['Cos']['50'].append(r['TIV']['Cosine']['0.5'])
    tiv['Cos']['75'].append(r['TIV']['Cosine']['0.75'])
    
    tiv['Euc']['25'].append(r['TIV']['Euclidean']['0.25'])
    tiv['Euc']['50'].append(r['TIV']['Euclidean']['0.5'])
    tiv['Euc']['75'].append(r['TIV']['Euclidean']['0.75'])
    
    All['Cos']['25'].append(r['All']['Cosine']['0.25'])
    All['Cos']['50'].append(r['All']['Cosine']['0.5'])
    All['Cos']['75'].append(r['All']['Cosine']['0.75'])
    
    All['Euc']['25'].append(r['All']['Euclidean']['0.25'])
    All['Euc']['50'].append(r['All']['Euclidean']['0.5'])
    All['Euc']['75'].append(r['All']['Euclidean']['0.75'])

songs = adjustOrder(songs)

for i in metric:
    metric[i] = adjustOrder(metric[i])

for i in intervallic:
    intervallic[i] = adjustOrder(intervallic[i])

for dist in tiv:
    for i in tiv[dist]:
        tiv[dist][i] = adjustOrder(tiv[dist][i])

for dist in All:
    for i in All[dist]:
        All[dist][i] = adjustOrder(All[dist][i])

songSet = {}
songSet['Original'] = songs

for i in metric:
    songSet['Metric' + i] = metric[i]

for i in intervallic:
    songSet['Intervallic' + i] = intervallic[i]

for dist in tiv:
    for i in tiv[dist]:
        songSet['TIV' + dist + i] = tiv[dist][i]

for dist in All:
    for i in All[dist]:
        songSet['All' + dist + i] = All[dist][i]

simValues = {}
counter = 0
for redLev in songSet:
    
    simValues[redLev] = []
    aux = False
    for compSet in comparisons:
        for i in compSet: 
            seq1 = songSet[redLev][i[0]]['features']
            seq2 = songSet[redLev][i[1]]['features']
            
            if aux == True:
                print(redLev)
                print(seq1['midipitch'])
                print(seq2['midipitch'])
                aux = False
                
            newSimValue = {}
            
            newSimValue['SIAM'] = simF.similar(seq1, seq2, "MIDIPITCH OFFSET DUR BSTR INT", sim.SIAM)
            
            newSimValue['Local Alignment'] = simF.similar(seq1, seq2, "MIDIPITCH DUR", sim.local_alignment)
            
            newSimValue['City Block'] = simF.similar(seq1, seq2, "MIDIPITCH", sim.city_block_distance)
            newSimValue['Euclidean'] = simF.similar(seq1, seq2, "MIDIPITCH", sim.euclidean_distance)
            newSimValue['Hamming'] = simF.similar(seq1, seq2, "MIDIPITCH", sim.hamming_distance)
            newSimValue['Correlation'] = simF.similar(seq1, seq2, "MIDIPITCH", sim.correlation)
            
            newSimValue['Cardinality'] = simF.similar(seq1, seq2, "MIDIPITCH ONSET", sim.cardinality_score)
            
            simValues[redLev].append(newSimValue)
            counter +=1
            print(counter)
 
rows = []
globalArr = [[],[],[]]

with open('answers3.csv', newline='') as csvfile:
     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
     for row in spamreader:
         rows.append(row)

for i in range(len(rows[0])):
    if rows[0][i] == 'Global':
        for j in range(len(rows)-1):
            globalArr[j].append(float(rows[j+1][i]))

corrValues = {}

for compMetric in simValues['Original'][0]:
    corrValues[compMetric] = {}
    for redLev in simValues:
        corrValues[compMetric][redLev] = {}

for redLev in simValues:
    for compMetric in corrValues:
        
        aux = [s[compMetric] for s in simValues[redLev]]
        for i in range(len(aux)):
            if np.isnan(aux[i]):
                aux[i] = 0
    
        corrValues[compMetric][redLev]['R^2'] = []
        corrValues[compMetric][redLev]['Pearson'] = []
        
        for annotator in globalArr:
            corr_matrix = np.corrcoef(annotator, aux)
            corr = corr_matrix[0,1]
            R_sq = corr**2
            corrValues[compMetric][redLev]['R^2'].append(R_sq)
            corrValues[compMetric][redLev]['Pearson'].append(pearsonr(annotator, aux))



R2tables = [0,0,0]
R2tables[0] = makeTable('R^2', 1, simValues, corrValues)
R2tables[1] = makeTable('R^2', 2, simValues, corrValues)
R2tables[2] = makeTable('R^2', 3, simValues, corrValues)

PearsonTables = [0,0,0]
PearsonTables[0] = makeTable('Pearson', 1, simValues, corrValues)
PearsonTables[1] = makeTable('Pearson', 2, simValues, corrValues)
PearsonTables[2] = makeTable('Pearson', 3, simValues, corrValues)

for i in range(0,3):    
    with open("R2tables2806feat5.csv","a") as my_csv:
        csvWriter = csv.writer(my_csv,delimiter=',')
        csvWriter.writerows(R2tables[i])
        
    with open("PearsonTables2806feat5.csv","a") as my_csv:
        csvWriter = csv.writer(my_csv,delimiter=',')
        csvWriter.writerows(PearsonTables[i])


