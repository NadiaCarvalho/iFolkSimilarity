# -*- coding: utf-8 -*-
"""
Created on Tue May 24 22:23:05 2022

@author: Daniel Diogo
"""

import csv
import numpy as np

class TestSet:
    def __init__(self, nRaters, diffMetric=False):
        self.diffMetric = diffMetric
        
        self.contorno = [[] for x in range(nRaters)]
        self.ritmo = [[] for x in range(nRaters)]
        self.motivos = [[] for x in range(nRaters)]
        self.glb = [[] for x in range(nRaters)]
        
        self.matrixes = {}
        self.p = {}
        self.P = {}
        self.Pline = {}
        self.Pe = {}
        self.k = {}
        
    def insert(self, rater, valor, tag):
        if tag == "contorno":
            self.contorno[rater].append(valor)
        if tag == "ritmo":
            self.ritmo[rater].append(valor)
        if tag == "motivos":
            self.motivos[rater].append(valor)
        if tag == "global":
            self.glb[rater].append(valor)
    
    def fillMat(self, rates, nSubjects, nCategories):
        occurMat = np.zeros((int(nSubjects), int(nCategories)))
        
        for rater in rates:
            for index in range(nSubjects):
                cat = int((float(rater[index]) / 0.05))
                occurMat[index, cat] += 1
                
        return occurMat
    
    def fleissKappa(self, nRaters, tag):
        values = [[] for x in range(nRaters)]
        nCategories = (2/0.05) + 1
            
        if tag == "contorno":
            nSubjects = len(self.contorno[0])
            for rater in range(nRaters):
                values[rater] = self.contorno[rater]
        
        if tag == "ritmo":
            nSubjects = len(self.ritmo[0])    
            if self.diffMetric == True:
                nCategories = (1/0.05) + 1
            for rater in range(nRaters):
                values[rater] = self.ritmo[rater]
        
        if tag == "motivos":
            nSubjects = len(self.motivos[0])
            for rater in range(nRaters):
                values[rater] = self.motivos[rater]
        
        if tag == "global":
            nSubjects = len(self.glb[0])
            for rater in range(nRaters):
                values[rater] = self.glb[rater]
        
        mat = self.fillMat(values, nSubjects, nCategories)
        
        self.matrixes[tag] = mat
        
        p = []
        P = []
        
        for j in range(int(nCategories)): 
            p.append((1/(nRaters*nSubjects))*sum(mat[:,j])) 
        
        for i in range(nSubjects):
            P.append((1/(nRaters*(nRaters-1))) * (sum(mat[i,:]**2) - nRaters))
        
        self.p[tag] = p
        self.P[tag] = P
        
        Pline = (1/nSubjects) * sum(P)
        Pe = sum(e**2 for e in p)
        
        self.Pline[tag] = Pline
        self.Pe[tag] = Pe
        
        k = (Pline-Pe)/(1-Pe)
        
        self.k[tag] = k

    def allFleiss(self, nRaters):
        self.fleissKappa(nRaters, 'motivos')
        self.fleissKappa(nRaters, 'contorno')
        self.fleissKappa(nRaters, 'ritmo')
        self.fleissKappa(nRaters, 'global')
        

rows = []

with open('answers.csv', newline='') as csvfile:
     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
     for row in spamreader:
         rows.append(row)


binario = TestSet(2)
ternario = TestSet(2)
bin_ter = TestSet(2)

for i in range(len(rows[0])):
    if i <= 40:
        if "Contorno" in rows[0][i]:
            for j in range(len(rows)-1):
                binario.insert(j, rows[j+1][i], 'contorno')
            
        if "Ritmo" in rows[0][i]:
            for j in range(len(rows)-1):
                binario.insert(j, rows[j+1][i], 'ritmo')
            
        if "Motivos" in rows[0][i]:
            for j in range(len(rows)-1):
                binario.insert(j, rows[j+1][i], 'motivos')
        
        if "Global" in rows[0][i]:
            for j in range(len(rows)-1):
                binario.insert(j, rows[j+1][i], 'global')
        
    if i > 40 and i <= 80:
        if "Contorno" in rows[0][i]:
            for j in range(len(rows)-1):
                ternario.insert(j, rows[j+1][i], 'contorno')
            
        if "Ritmo" in rows[0][i]:
            for j in range(len(rows)-1):
                ternario.insert(j, rows[j+1][i], 'ritmo')
            
        if "Motivos" in rows[0][i]:
            for j in range(len(rows)-1):
                ternario.insert(j, rows[j+1][i], 'motivos')
        
        if "Global" in rows[0][i]:
            for j in range(len(rows)-1):
                ternario.insert(j, rows[j+1][i], 'global')
        
    else:
        if "Contorno" in rows[0][i]:
            for j in range(len(rows)-1):
                bin_ter.insert(j, rows[j+1][i], 'contorno')
            
        if "Ritmo" in rows[0][i]:
            for j in range(len(rows)-1):
                bin_ter.insert(j, rows[j+1][i], 'ritmo')
            
        if "Motivos" in rows[0][i]:
            for j in range(len(rows)-1):
                bin_ter.insert(j, rows[j+1][i], 'motivos')
        
        if "Global" in rows[0][i]:
            for j in range(len(rows)-1):
                bin_ter.insert(j, rows[j+1][i], 'global')
                
binario.allFleiss(2)
ternario.allFleiss(2)
bin_ter.allFleiss(2)
        
    
    