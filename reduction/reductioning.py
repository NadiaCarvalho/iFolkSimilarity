# -*- coding: utf-8 -*-
"""
Created on Thu May 12 11:03:36 2022

@author: User
"""

from TIVlib import TIV as tiv
from os import walk
mei_path = 'C:/Users/User/Documents/Faculdade/5_ano/2_Semestre/Datasets/I-Folk'

i=0
f_path = []
for (dirpath, dirnames, filenames) in walk(mei_path):
    for f in filenames:
        print("File %d out of %d" %(i+1, len(filenames)))
        f_path.append(dirpath + '/' + f)
        fHpcp = file_to_hpcp(f_path)
        fileTiv = tiv.from_pcp(fHpcp)
        print("tiv.mag: " + str(fileTiv.mags()))
        print("tiv.diatonicity: " + str(fileTiv.diatonicity()))
        print("tiv.chromacity: " + str(fileTiv.chromaticity()))
        print("tiv.dissonance: " + str(fileTiv.dissonance()))
        i+=1

