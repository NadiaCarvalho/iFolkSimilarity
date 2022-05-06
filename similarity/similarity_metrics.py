    # -*- coding: utf-8 -*-
"""
Created on Mon May  2 15:32:06 2022

@author: Berit Janssen
@editor: Daniel Diogo

based on:
    https://github.com/BeritJanssen/MelodicOccurrences/blob/master/similarity.py
"""
import numpy as np
from scipy import spatial
from collections import Counter

def cardinality_score(seq1, seq2):
    """ calculates the cardinality score between two sequences """
    rset = set([(r['onset'],r['pitch']) for r in seq1])
    qset = set([(q['onset'],q['pitch']) for q in seq2])
    cSc = len(rset.intersection(qset))
    return cSc

def city_block_distance(seq1, seq2):
    """ calculates the city-block distance between two sequences"""
    dif = spatial.distance.cityblock(seq1, seq2)
    return dif/float(len(seq1))

def correlation(seq1, seq2):
    """ calculates the correlation distance between two sequences """
    # returns 1 - correlation coefficient
    cor = spatial.distance.correlation(seq1, seq2)
    return cor

def euclidean_distance(seq1, seq2):
    """ calculates the euclidean distance between two sequences """
    sim = spatial.distance.euclidean(seq1, seq2)
    return sim/float(len(seq1))

def hamming_distance(seq1, seq2): 
    """ calculates the hamming distance between two sequences """
    mm = spatial.distance.hamming(seq1, seq2)
    return mm

def match_distance_tuples(seq1, seq2, dist_func): 
    """returns the distance for multidimensional data points, using the chosen 
    distance function (dist_func) in scipy.spatial"""
    mm = spatial.distance.cdist(np.array(seq1), np.array(seq2), dist_func)
    return mm

def multi_dimensional(seq1, seq2, variances): 
    """euclidean distance of the points in local alignment"""
    return -spatial.distance.seuclidean(seq1, seq2, variances) + 1.0

#seq1, seq2: array of symbols (dictionaries)
#gap_score: float
#sim_score: function that takes two symbols and returns float
def local_alignment(seq1, seq2, insert_score, delete_score, sim_score, 
    return_positions, variances=[]):
    """ local alignment takes two sequences (the query comes first), 
    the insertion and deletion sore,
    and a function which defines match / mismatch
    returns the index where the match starts in the sequence, 
    and the normalized score of the match
    """
    #initialize dynamic programming matrix
    d = np.zeros([len(seq1)+1, len(seq2)+1])
    #initialize backtrace matrix
    b = np.zeros([len(seq1)+1, len(seq2)+1])
    max_score = 0.0
    #fill dynamic programming matrix
    for i in range(1, len(seq1) + 1):
        # query sequence, rows of dynamic programming matrix
        for j in range(1, len(seq2) + 1):
            # matched in longer sequence, columns of dynamic programming matrix
            from_left = d[i,j-1] + delete_score
            from_top = d[i-1,j] + insert_score
            diag = d[i-1,j-1] + sim_score(seq1[i-1], seq2[j-1], variances)
            d[i,j] = max(from_top, from_left, diag, 0.0)
            if d[i,j] > max_score:
                max_score = d[i,j]
            # store where the current entry came from in the backtrace matrix
            if d[i,j] == from_left:
                # deletion from longer sequence
                backtrace = 0
            elif d[i,j] == from_top:
                # insertion into longer sequence
                backtrace = 1
            elif d[i,j] == diag:
                # substitution
                backtrace = 2
            else:
                backtrace = -1
            b[i,j] = backtrace
    m,n = np.where(d == max_score)
    # convert from numpy array to integer
    similarity = max_score/float(len(seq1))
    if not return_positions:
        return [int(n[0]), 0, similarity]
    # store the length of the match as well to return 
    #(match length can be shorter than query length)
    match_list = []
    # do not return more than 5 matches
    if m.size>4:
        num_matches = 5
    else:
        num_matches = m.size
    for i in range(num_matches):
        row = int(m[i])
        column = int(n[i])
        match_length = 0
        while d[row,column] > 0 :
            if b[row,column] == 0:
                # deletion from longer sequence, move left
                column -= 1
                match_length += 1
            elif b[row,column] == 1:
                # insertion into longer sequence, move up
                row -= 1
            elif b[row,column] == 2:
                # substitution, move diagonally
                row -= 1
                column -= 1
                match_length += 1
            else :
                print(d, b, row, column)
        match_list.append([column, match_length, similarity])
    return match_list

def siam(melody_list,segment_list,music_representation,
 return_positions,scaling): 
    """ this function takes melodies and segments belonging 
    to the same tune family, 
	represented as lists of dictionaries,
	and finds occurrences using SIAM
	in the specified music representation (specified by music_representation)
    Optionally, the positions of the occurrences can be returned, if applicable,
    scaled by a scaling factor.
	"""
    result_list = []
    for seg in segment_list :
        start_onset = seg['symbols'][0]['onset']
        seg_points = [(s['onset'] - start_onset, s['pitch']) for 
         s in seg['symbols']]
        for mel in melody_list: 
            translation_vectors = []
            translation_vectors_with_position = []
            mel_points = np.array([(s['onset'], s['pitch']) for 
             s in mel['symbols']])
            for p in seg_points: 
                vectors = (mel_points - p)
                translation_vectors.extend([tuple(v) for v in vectors])
                translation_vectors_with_position.append((p[0], 
                 [tuple(v) for v in vectors]))
            grouped_vectors = dict(Counter(translation_vectors))
            # the similarity is the size of the maximal TEC
            similarity = max([grouped_vectors[k] for k in grouped_vectors])
            match_results = {'similarity': similarity / float(len(seg_points))} 
            if return_positions:
                match = {'similarity': similarity / float(len(seg_points))}
                match_results = []
                shifts = [key for key in grouped_vectors if 
                 grouped_vectors[key]==similarity]
                for shift in shifts:
                    onsets = [vec[0] for vec in 
                     translation_vectors_with_position if shift in vec[1]]
                    match_start_onset = min(onsets) + shift[0]
                    match_end_onset = max(onsets) + shift[0]
                    if 'onsets_multiplied_by' in mel:
                        match_start_onset = (match_start_onset / 
                         float(mel['onsets_multiplied_by']))
                        match_end_onset = (match_end_onset / 
                         float(mel['onsets_multiplied_by']))
                    match['match_start_onset'] = match_start_onset
                    match['match_end_onset'] = match_end_onset
                    match_results.append(match.copy())
            result_list.append({'tunefamily_id': seg['tunefamily_id'],
             'query_filename': seg['filename'],
             'match_filename': mel['filename'],
             'query_segment_id': seg['segment_id'],
             'query_length': len(seg_points),
             'matches': {'siam': match_results}})
    return result_list

""" Auxiliary Functions """

def pitch_rater(seq1, seq2, variances):
    """ subsitution score for local alignment"""
    if seq1 == seq2:
        return 1.0
    else:
        return -1.0

def pitch_difference(seq1, seq2, variances):
    """ subsitution score for local alignment: 
    returns the difference between pitches in two sequences"""
    return 2.0 - abs(seq1-seq2)

def label_diff(seq1, seq2) :
    """ called by ir_alignment """
    if seq1['IR_structure'] == seq2['IR_structure']: 
        return 0.0
    elif seq1['IR_structure'].strip('[]') == seq2['IR_structure'].strip('[]'): 
        return 0.801
    else: 
        return 1.0

def ir_alignment(seq1, seq2, variances): 
    """ substitution score for IR structure alignment """
    subsScore = .587*label_diff(seq1, seq2) + .095*abs((seq1['end_index'] - 
        seq1['start_index']) - (seq2['end_index'] - seq2['start_index']))
    + .343*abs(seq1['direction'] - seq2['direction'])
    + .112*abs(seq1['overlap'] - seq2['overlap'])
    return 1.0 - subsScore