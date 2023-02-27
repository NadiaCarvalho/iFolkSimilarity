"""
Created on Mon Feb 27 13:12:18 2023

@author: Nádia Carvalho
"""


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
