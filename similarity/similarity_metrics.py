# -*- coding: utf-8 -*-
"""
Created on Mon May  2 15:32:06 2022

@author: Daniel Diogo

based on:
    https://github.com/NadiaCarvalho/co-poem/blob/master/backend/app/composition/representation/utils/similarity.py
    https://github.com/BeritJanssen/MelodicOccurrences/blob/master/similarity.py
"""
import numpy as np
from scipy import spatial

# Auxiliary Functions:
    # For Local Alignment
def pitch_rater(seq1, seq2, variances=[]):
    """ subsitution score for local alignment"""
    if np.all(seq1 == seq2):
        return 1.0
    else:
        return -1.0

# Similarity Metrics:
    # Correlation Distance
def correlation(seq1, seq2):
    """ calculates the correlation distance between two sequences """
    # returns 1 - correlation coefficient
    cor = spatial.distance.correlation(seq1, seq2)
    return cor


    # City Block Distance
def city_block_distance(seq1, seq2):
    """ calculates the city-block distance between two sequences"""
    dif = spatial.distance.cityblock(seq1, seq2)
    return dif/float(len(seq1))


    # Euclidean Distance
def euclidean_distance(seq1, seq2):
    """ calculates the euclidean distance between two sequences """
    sim = spatial.distance.euclidean(seq1, seq2)
    return sim/float(len(seq1))

    # Local Alignment
def local_alignment(seq_1, seq_2, insert_score=-.5, delete_score=-.5,
                    sim_score=pitch_rater, variances=[]):
    """
    Local Alignent Algorithm (Janssen/Kranenburg/Volk)
    based on https://github.com/BeritJanssen/MelodicOccurrences/blob/master/similarity.py
    """
    if len(seq_1) > len(seq_2):
        temp_seq = seq_1
        seq_1 = seq_2
        seq_2 = temp_seq

    # initialize dynamic programming matrix
    dyn_matrix = np.zeros([len(seq_1) + 1, len(seq_2) + 1])
    # initialize backtrace matrix
    back_matrix = np.zeros([len(seq_1) + 1, len(seq_2) + 1])

    max_score = 0.0

    for i, ev_1 in enumerate(seq_1):
        for j, ev_2 in enumerate(seq_2):
            from_left = dyn_matrix[i + 1, j] + delete_score
            from_top = dyn_matrix[i, j - 1] + insert_score

            diag = dyn_matrix[i, j] + sim_score(ev_1[0:], ev_2[0:], variances)
            dyn_matrix[i + 1, j + 1] = max(from_top, from_left, diag, 0.0)

            if dyn_matrix[i + 1, j + 1] > max_score:
                max_score = dyn_matrix[i + 1, j + 1]
            # store where the current entry came from in the backtrace matrix
            if dyn_matrix[i + 1, j + 1] == from_left:
                # deletion from longer sequence
                backtrace = 0
            elif dyn_matrix[i + 1, j + 1] == from_top:
                # insertion into longer sequence
                backtrace = 1
            elif dyn_matrix[i + 1, j + 1] == diag:
                # substitution
                backtrace = 2
            else:
                backtrace = -1
            back_matrix[i + 1, j + 1] = backtrace

    return max_score / float(min(len(seq_1), len(seq_2)))