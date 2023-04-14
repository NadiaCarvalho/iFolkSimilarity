# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 09:22:00 2023

@author: Nádia Carvalho
"""

import itertools

import numpy as np
import pandas as pd


def create_vector_table(datapoints_1, datapoints_2):
    """
    Create a table of vectors between two sets of datapoints.

    @param datapoints_1: set of datapoints 1
    @param datapoints_2: set of datapoints 2

    @return: table of vectors
    """
    vector_table = np.empty(
        (len(datapoints_1), len(datapoints_2), len(datapoints_1[0])))
    for i, vec_1 in enumerate(datapoints_1):
        for j, vec_2 in enumerate(datapoints_2):
            vector_table[i][j] = vec_1 - vec_2
    return vector_table


def MTPs(vector_table):
    """
    Calculate the number of times each translation vector appears in the vector table.

    @param vector_table: table of vectors

    @return: list of number of times each translation vector appears in the vector table
    """
    set_tuples = set(tuple(i) for i in list(itertools.chain(*vector_table)))
    sorted_translations = sorted([np.array(tp)
                                 for tp in set_tuples], key=lambda x: x[0])
    mtps = []
    # i=1
    for st in sorted_translations:
        str_vector_table = np.array(
            [[str(vt) for vt in vt_c] for vt_c in vector_table])
        indexes = np.where(str_vector_table[::] == str(st))[1]
        mtps.append(len(indexes))
        # print(i)
        # i+=1
    return mtps


def MTPnew(vector_table):
    """
    Calculate the number of times each translation vector appears in the vector table.

    @param vector_table: table of vectors

    @return: list of number of times each translation vector appears in the vector table
    """
    str_vector_table = np.array([[str(vt) for vt in vt_c]
                                for vt_c in vector_table]).flatten()
    return np.unique(str_vector_table, return_counts=True)[1]


def MTP(vector_table, trans_vector):
    """
    Calculate the number of times a translation vector appears in the vector table.

    @param vector_table: table of vectors

    @return: number of times a translation vector appears in the vector table
    """
    return np.count_nonzero(np.all(vector_table == trans_vector, axis=2))


def print_vector_table(vector_table, seq_1, seq_2):
    str_vector_table = [[str(vt) for vt in vt_c] for vt_c in vector_table]
    df = pd.DataFrame(str_vector_table, index=[str(
        s) for s in seq_1], columns=[str(s) for s in seq_2])
    print(df)
    return df


def print_lexicographical_table(vector_table, seq_2):
    set_tuples = set(tuple(i) for i in list(itertools.chain(*vector_table)))
    sorted_translations = sorted([np.array(tp)
                                 for tp in set_tuples], key=lambda x: x[0])

    for st in sorted_translations:
        str_vector_table = np.array(
            [[str(vt) for vt in vt_c] for vt_c in vector_table])
        indexes = np.where(str_vector_table[::] == str(st))[1]
        print(f'{st} -> ' +
              ', '.join([f"{np.array(seq_2[i])}" for i in indexes]))


def siam_score(song1, song2):
    """
    Structure induction algorithms's pattern matching algorithm

    @param song1: song 1 (query)
    @param song2: song 2

    @return: normalized score of query match in song2
    """
    song1 = np.array(song1)
    song2 = np.array(song2)

    vector_table = create_vector_table(song1, song2)
    #vc = print_vector_table(vector_table, song1, song2)
    #vc.to_excel('vector_table.xlsx')
    #print_lexicographical_table(vector_table, song2)

    mtps_1 = MTPnew(vector_table)
    return max(mtps_1) / max(len(song1), len(song2))
