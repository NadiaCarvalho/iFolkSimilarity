# -*- coding: utf-8 -*-
"""
Created on Tue May 24 22:23:05 2022

@author: Daniel Diogo
"""

import csv

class TestSet:
    def __init__(self, nAvaliadores):
        self.contorno = [[] for x in range(nAvaliadores)]
        self.ritmo = [[] for x in range(nAvaliadores)]
        self.motivos = [[] for x in range(nAvaliadores)]
        self.glb = [[] for x in range(nAvaliadores)]
        
    def inserir(self, avaliador, valor, tag):
        if tag == "contorno":
            self.contorno[avaliador].append(valor)
        if tag == "ritmo":
            self.ritmo[avaliador].append(valor)
        if tag == "motivos":
            self.motivos[avaliador].append(valor)
        if tag == "global":
            self.glb[avaliador].append(valor)

rows = []

with open('answers.csv', newline='') as csvfile:
     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
     for row in spamreader:
         rows.append(row)


binario = TestSet(3)
ternario = TestSet(3)
bin_ter = TestSet(3)

for i in range(len(rows[0])):
    if i <= 40:
        if "Contorno" in rows[0][i]:
            for j in range(len(rows)-1):
                binario.inserir(j, rows[j+1][i], 'contorno')
            
        if "Ritmo" in rows[0][i]:
            for j in range(len(rows)-1):
                binario.inserir(j, rows[j+1][i], 'ritmo')
            
        if "Motivos" in rows[0][i]:
            for j in range(len(rows)-1):
                binario.inserir(j, rows[j+1][i], 'motivos')
        
        if "Global" in rows[0][i]:
            for j in range(len(rows)-1):
                binario.inserir(j, rows[j+1][i], 'global')
        
    if i > 40 and i <= 80:
        if "Contorno" in rows[0][i]:
            for j in range(len(rows)-1):
                ternario.inserir(j, rows[j+1][i], 'contorno')
            
        if "Ritmo" in rows[0][i]:
            for j in range(len(rows)-1):
                ternario.inserir(j, rows[j+1][i], 'ritmo')
            
        if "Motivos" in rows[0][i]:
            for j in range(len(rows)-1):
                ternario.inserir(j, rows[j+1][i], 'motivos')
        
        if "Global" in rows[0][i]:
            for j in range(len(rows)-1):
                ternario.inserir(j, rows[j+1][i], 'global')
        
    else:
        if "Contorno" in rows[0][i]:
            for j in range(len(rows)-1):
                bin_ter.inserir(j, rows[j+1][i], 'contorno')
            
        if "Ritmo" in rows[0][i]:
            for j in range(len(rows)-1):
                bin_ter.inserir(j, rows[j+1][i], 'ritmo')
            
        if "Motivos" in rows[0][i]:
            for j in range(len(rows)-1):
                bin_ter.inserir(j, rows[j+1][i], 'motivos')
        
        if "Global" in rows[0][i]:
            for j in range(len(rows)-1):
                bin_ter.inserir(j, rows[j+1][i], 'global')
                

        
    
    