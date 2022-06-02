# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 16:37:34 2022

Fleiss Kappa algorithms not used

@author: Daniel Diogo

"""

self.matrixes = {}
self.p = {}
self.P = {}
self.Pline = {}
self.Pe = {}
self.k = {}

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