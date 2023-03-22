"""
Created on Mon Feb 27 13:12:18 2023

@author: Nádia Carvalho
"""
from scipy import spatial

from src.similarity.utils import check_same_size

from src.similarity.algorithms.local_alignment import local_alignment_score
from src.similarity.algorithms.siam import siam_score


def cardinality_score(song1, song2):
    """
    Compute cardinality score between two songs
    Uses only midipitch and onsettick

    @param song1: song 1
    @param song2: song 2

    @return: cardinality score
    """
    song1_set = set([tuple(x) for x in song1])
    song2_set = set([tuple(x) for x in song2])

    number_intersections = len(song1_set.intersection(song2_set))

    if len(song1_set) < len(song2_set):
        return number_intersections / len(song1_set)
    return number_intersections / len(song2_set)


def correlation_distance(song1, song2):
    """
    Compute correlation distance between two songs
    Uses only midipitch and onsets

    @param song1: song 1
    @param song2: song 2

    @return: correlation distance
    """
    song1, song2 = check_same_size(song1, song2)
    return spatial.distance.correlation(song1, song2)


def cityblock_distance(song1, song2):
    """
    Compute city block distance between two songs
    Uses only midipitch and onsettick

    @param song1: song 1
    @param song2: song 2

    @return: city block distance
    """
    song1, song2 = check_same_size(song1, song2)
    return spatial.distance.cityblock(song1, song2) / float(len(song1))


def euclidean_distance(song1, song2):
    """
    Compute euclidean distance between two songs
    Uses only midipitch and onsettick

    @param song1: song 1
    @param song2: song 2

    @return: euclidean distance
    """
    song1, song2 = check_same_size(song1, song2)
    return spatial.distance.euclidean(song1, song2) / float(len(song1))

def hamming_distance(song1, song2):
    """
    Compute hamming distance between two songs
    Uses only midipitch and onsettick

    @param song1: song 1
    @param song2: song 2

    @return: hamming distance
    """
    song1, song2 = check_same_size(song1, song2)
    return spatial.distance.hamming(song1, song2)
