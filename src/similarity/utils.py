    # -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 08:54:58 2023

@author: Nádia Carvalho
"""
import numpy as np

def check_same_size(seq1, seq2):
    """Check if two sequences have the same size. If not, pad with zeros"""
    max_size = max(len(seq1), len(seq2))

    if len(seq1) != max_size:
        seq1 = np.pad(seq1, (0, max_size - len(seq1)), 'constant', constant_values=(0, 0))
    if len(seq2) != max_size:
        seq2 = np.pad(seq2, (0, max_size - len(seq2)), 'constant', constant_values=(0, 0))

    return seq1, seq2