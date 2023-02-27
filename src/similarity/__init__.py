"""
Created on Mon Feb 27 12:57:13 2023

@author: Nádia Carvalho
"""
import numpy as np

from src.similarity.algorithms import cardinality_score

class SimilarityCalculator:
    """
    Class to compute similarity between songs
    """

    def __init__(self):
        pass

    def get_features(self, song, feature_list=None):
        """
        Get features from song
        """
        if feature_list is None or len(feature_list) == 0:
            feature_list = ['pitch', 'duration', 'midipitch', 'chromaticinterval', 'ioi', 'timesignature',
                            'duration_frac', 'diatonicpitch', 'onsettick', 'offset', 'beatstrength', 'beat', 'tonic', 'mode']

        features = []
        for feature in feature_list:
            features.append(song['features'][feature])

        return np.asarray(features).transpose()

    def similarity_between_two_songs(self, song1, song2, algorithm='cardinality_score'):
        """
        Compute similarity between two songs

        @param song1: song 1 (features, reduction)
        @param song2: song 2 (features, reduction)
        @param algorithm: similarity algorithm
            - Possible Values:
                - 'cardinality_score'
                - 'correlation_distance'
                - 'city_block_distance'
                - 'euclidean_distance'
                - 'hamming_distance'
                - 'local_alignment_score', Local Alignment Algorithm
                - 'siam_score', Structure Induction Matching Algorithm
        """
        song1_features, song1_reduction = song1
        song2_features, song2_reduction = song2

        if algorithm == 'cardinality_score':
            song1_features = self.get_features(song1_features, ['midipitch', 'onsettick'])
            song1_features = song1_features[song1_reduction, :]

            song2_features = self.get_features(song2_features, ['midipitch', 'onsettick'])
            song2_features = song2_features[song2_reduction, :]

            return cardinality_score(song1_features, song2_features)
        elif algorithm == 'correlation_distance':
            pass
        elif algorithm == 'city_block_distance':
            pass
        elif algorithm == 'euclidean_distance':
            pass
        elif algorithm == 'hamming_distance':
            pass
        elif algorithm == 'local_alignment_score':
            pass
        elif algorithm == 'siam_score':
            pass
        else:
            raise ValueError(f'Invalid algorithm "{algorithm}"')
