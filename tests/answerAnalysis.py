# -*- coding: utf-8 -*-
"""
Created on Tue May 24 22:23:05 2022

@author: Daniel Diogo
"""

import csv
import pingouin as pg
import pandas as pd
class TestSet:
    def __init__(self, nRaters, diffMetric=False):
        self.diffMetric = diffMetric
        
        self.contorno = [[] for x in range(nRaters)]
        self.ritmo = [[] for x in range(nRaters)]
        self.motivos = [[] for x in range(nRaters)]
        self.glb = [[] for x in range(nRaters)]
        
        self.icc = {}
        
    def insert(self, rater, valor, tag):
        if tag == "contorno":
            self.contorno[rater].append(valor)
        if tag == "ritmo":
            self.ritmo[rater].append(valor)
        if tag == "motivos":
            self.motivos[rater].append(valor)
        if tag == "global":
            self.glb[rater].append(valor)
        
    def makeDataFrame(self, tag):
        auxDict = {}
        auxDict['exam'] = []
        auxDict['judge'] = []
        auxDict['rating'] = []
        
        if tag == "contorno":
            for rater in range(len(self.contorno)):
                for i in range(len(self.contorno[rater])):
                    auxDict['exam'].append(i+1)
                    auxDict['judge'].append(rater+1)
                    auxDict['rating'].append(self.contorno[rater][i])
                    
        if tag == "ritmo":
            for rater in range(len(self.ritmo)):
                for i in range(len(self.ritmo[rater])):
                    auxDict['exam'].append(i+1)
                    auxDict['judge'].append(rater+1)
                    auxDict['rating'].append(self.ritmo[rater][i])
                    
        if tag == "motivos":
            for rater in range(len(self.motivos)):
                for i in range(len(self.motivos[rater])):
                    auxDict['exam'].append(i+1)
                    auxDict['judge'].append(rater+1)
                    auxDict['rating'].append(self.motivos[rater][i])
                    
        if tag == "global":
            for rater in range(len(self.glb)):
                for i in range(len(self.glb[rater])):
                    auxDict['exam'].append(i+1)
                    auxDict['judge'].append(rater+1)
                    auxDict['rating'].append(self.glb[rater][i])
            
        df = pd.DataFrame(auxDict)
        icc = pg.intraclass_corr(data=df, targets='exam', raters='judge', ratings='rating')
        icc.set_index('Type')
        
        return icc
        
    def makeAllDataFrames(self):
    
        self.icc['contorno'] = self.makeDataFrame("contorno")
        self.icc['ritmo'] = self.makeDataFrame("ritmo")
        self.icc['motivos'] = self.makeDataFrame("motivos")
        self.icc['global'] = self.makeDataFrame("global")
        
rows = []

with open('answersGilbertoNadia.csv', newline='') as csvfile:
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

binario.makeAllDataFrames()
ternario.makeAllDataFrames()
bin_ter.makeAllDataFrames()
    
    