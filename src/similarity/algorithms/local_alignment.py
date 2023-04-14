# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 09:22:00 2023

@author: Berit Janssen
@editor: Nádia Carvalho

based on:
    https://github.com/BeritJanssen/MelodicOccurrences/blob/master/similarity.py
"""

import numpy as np
from scipy import spatial

""" For Implication-Realization Structure Alignment (IRSA): """


def label_diff(seq1, seq2):
    """ called by ir_alignment """
    if seq1['IR_structure'] == seq2['IR_structure']:
        return 0.0
    elif seq1['IR_structure'].strip('[]') == seq2['IR_structure'].strip('[]'):
        return 0.801
    else:
        return 1.0


def ir_alignment(seq1, seq2, variances):
    """ substitution score for IR structure alignment """
    return 1.0 - .587*label_diff(seq1, seq2) + .095*abs((seq1['end_index'] -
                                                         seq1['start_index']) - (seq2['end_index'] - seq2['start_index'])) + .343*abs(seq1['direction'] - seq2['direction']) + .112*abs(seq1['overlap'] - seq2['overlap'])


def multi_dimensional(seq1, seq2, variances):
    """euclidean distance of the points in local alignment"""
    return - spatial.distance.seuclidean(seq1, seq2, variances) + 1.0


def pitch_rater(seq1, seq2, variances):
    """ subsitution score for local alignment"""
    if isinstance(seq1, np.ndarray) and all(x1 == x2 for (x1, x2) in zip(seq1, seq2)):
        return 1.0
    elif not isinstance(seq1, np.ndarray) and seq1 == seq2:
        return 1.0
    else:
        return -1.0


def pitch_difference(seq1, seq2, variances):
    """ subsitution score for local alignment:
    returns the difference between pitches in two sequences"""
    return 2.0 - abs(seq1-seq2)


def local_alignment_score(song1, song2, insert_score=-0.5, delete_score=-0.5, sim_score=pitch_rater, variances=[], return_match=False):
    """
    Local Alignment Algorithm

    Takes two sequences and returns the similarity score between them.

    @param song1: song 1 (query)
    @param song2: song 2
    @param insert_score: weight for insertions in the alignment
    @param delete_score: weight for deletions in the alignment
    @param sim_score: fuction to calculate match and mismatch between scores
    @param variances: list of variances for similarity score algorithm
    @param return_match: if True, returns all the matches between the two sequences

    @return: normalized score of query match in song2
    @return: list of matches (index, length, score) of query match starting in song2 (not yet implemented)
    """
    if len(song1) > len(song2):
        # print("song1 (query) is longer than song2. Exchanging them.")
        return local_alignment_score(song2, song1, insert_score, delete_score, sim_score, variances, return_match)

    # initialize dynamic programming matrix
    dp_matrix = np.zeros((len(song1)+1, len(song2)+1))
    # initialize backtrace matrix
    bk_matrix = np.zeros((len(song1)+1, len(song2)+1))

    max_score = 0.0

    # fill dynamic programming matrix
    for i, ev_1 in enumerate(song1):
        for j, ev_2 in enumerate(song2):
            from_left = dp_matrix[i+1, j] + delete_score
            from_top = dp_matrix[i, j-1] + insert_score
            from_diag = dp_matrix[i, j] + sim_score(ev_1, ev_2, variances)

            dp_matrix[i+1, j+1] = max(from_left, from_top, from_diag, 0.0)

            if dp_matrix[i+1, j+1] > max_score:
                max_score = dp_matrix[i+1, j+1]

            # store where the current entry
            # came from in the backtrace matrix
            if dp_matrix[i+1, j+1] == from_left:
                bk_matrix[i+1, j+1] = 0
            elif dp_matrix[i+1, j+1] == from_top:
                bk_matrix[i+1, j+1] = 1
            elif dp_matrix[i+1, j+1] == from_diag:
                bk_matrix[i+1, j+1] = 2
            else:
                bk_matrix[i+1, j+1] = -1

    score = max_score / float(len(song1))
    if not return_match:
        return score
    return find_all_matches(dp_matrix, bk_matrix, max_score, score)


def find_all_matches(dp_matrix, bk_matrix, max_score, score):
    """
    Find all matches in the dynamic programming matrix

    @param dp_matrix: dynamic programming matrix
    @param bk_matrix: backtrace matrix
    @param max_score: maximum score in the dynamic programming matrix
    @param score: normalized score of query match in song2

    @return: list of matches (index, length, score) of query match starting in song2
    """
    match_r, match_c = np.where(dp_matrix == max_score)

    match_list = []

    num_matches = match_r.size
    if match_r.size > 4:
        num_matches = 5

    for i in range(num_matches):
        row = int(match_r[i])
        col = int(match_c[i])

        match_len = 0
        while dp_matrix[row, col] > 0:
            if bk_matrix[row, col] == 0:  # deletion from longer sequence, move left
                col -= 1
                match_len += 1
            elif bk_matrix[row, col] == 1:  # insertion into longer sequence, move up
                row -= 1
            elif bk_matrix[row, col] == 2:  # substitution, move diagonally
                row -= 1
                col -= 1
                match_len += 1
            else:
                print(dp_matrix, bk_matrix, row, col)

        match_list.append([col, match_len, score])
    return match_list
