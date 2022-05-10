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
#from collections import Counter

""" AUXILIARY FUNCTIONS """

""" For Distances: """

def check_same_size(seq1, seq2):
    size1 = len(seq1)
    size2 = len(seq2)
    
    if size1 != size2:
        if size1 > size2:
            seq1 = seq1[:size2]
        else:
            seq2 = seq2[:size1]
    
    return seq1, seq2

""" For Carvalho's SIAM: """ 

def create_vector_table(datapoints_1, datapoints_2):
    vector_table = np.empty(
        (len(datapoints_1), len(datapoints_2), len(datapoints_1[0])))

    for i, vec_1 in enumerate(datapoints_1):
        for j, vec_2 in enumerate(datapoints_2):
            vector_table[i][j] = vec_1 - vec_2

    return vector_table


def MTP(vector_table, trans_vector):
    return np.count_nonzero(np.all(vector_table == trans_vector, axis=2))


""" For Local Alignment: """

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

""" For Implication-Realization Structure Alignment (IRSA): """

def label_diff(seq1, seq2) :
    """ called by ir_alignment """
    if seq1['IR_structure'] == seq2['IR_structure']: 
        return 0.0
    elif seq1['IR_structure'].strip('[]') == seq2['IR_structure'].strip('[]'): 
        return 0.801
    else: 
        return 1.0



def cardinality_score(seq1, seq2):
    """ calculates the cardinality score between two sequences """
    """ Pitch sequence and onset """
    rset = set(seq1)
    qset = set(seq2)
    cSc = len(rset.intersection(qset))
    return cSc

def city_block_distance(seq1, seq2):
    """ calculates the city-block distance between two sequences"""
    """" Only uses pitch sequence """
    
    seq1, seq2 = check_same_size(seq1, seq2)
    
    dif = spatial.distance.cityblock(seq1, seq2)
    return dif/float(len(seq1))

def correlation(seq1, seq2):
    """ calculates the correlation distance between two sequences """
    """ Paper says it uses both pitch sequence and onset """
    seq1, seq2 = check_same_size(seq1, seq2)
    
    # Correlation with both the pitch sequence and onset
    cor = spatial.distance.correlation(seq1, seq2)
    
    return cor

def euclidean_distance(seq1, seq2):
    """ calculates the euclidean distance between two sequences """
    
    seq1, seq2 = check_same_size(seq1, seq2)
    
    sim = spatial.distance.euclidean(seq1, seq2)
    return sim/float(len(seq1))

def hamming_distance(seq1, seq2): 
    """ calculates the hamming distance between two sequences """
    seq1, seq2 = check_same_size(seq1, seq2)
    
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
def local_alignment(seq_1, seq_2, insert_score=-0.5, delete_score=-0.5, sim_score=pitch_rater, variances=[]):
    """ local alignment takes two sequences (the query comes first), 
    the insertion and deletion sore,
    and a function which defines match / mismatch
    returns the index where the match starts in the sequence, 
    and the normalized score of the match
    """
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

#def ir_alignment(seq1, seq2, variances=[]): 
#    """ substitution score for IR structure alignment """
#    subsScore = .587*label_diff(seq1, seq2) + .095*abs((seq1['end_index'] - 
#        seq1['start_index']) - (seq2['end_index'] - seq2['start_index']))
#    + .343*abs(seq1['direction'] - seq2['direction'])
#    + .112*abs(seq1['overlap'] - seq2['overlap'])
#    return 1.0 - subsScore

""" SIAM as coded by Nádia Carvalho: """

def SIAM(seq_1, seq_2):
    """
    Structure induction algorithms's pattern matching algorithm
    """
    seq_1 = np.array(seq_1)
    seq_2 = np.array(seq_2)
    vector_table = create_vector_table(seq_1, seq_2)
    return max([MTP(vector_table, T) for T in vector_table[::]]) / len(seq_1)


""" SIAM as coded by Berit Janssen:
    
def SIAM(melody_list,segment_list,music_representation,
 return_positions,scaling): 
     this function takes melodies and segments belonging 
    to the same tune family, 
	represented as lists of dictionaries,
	and finds occurrences using SIAM
	in the specified music representation (specified by music_representation)
    Optionally, the positions of the occurrences can be returned, if applicable,
    scaled by a scaling factor.
	
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
"""