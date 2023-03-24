"""
Created on Mon Feb 27 12:57:13 2023

@author: Nádia Carvalho
"""
from fractions import Fraction

import numpy as np

import src.similarity.algorithms as sim_algorithms


class SimilarityCalculator:
    """
    Class to compute similarity between songs
    """

    def __init__(self):
        pass

    def get_features(self, song, feature_list=None):
        """
        Get features from song

        @param song: song
        @param feature_list: list of features to get

        @return: features
        """
        if feature_list is None or len(feature_list) == 0:
            feature_list = ['pitch', 'duration', 'midipitch', 'chromaticinterval', 'ioi', 'timesignature',
                            'duration_frac', 'diatonicpitch', 'onsettick', 'offsets', 'beatstrength', 'beat', 'tonic', 'mode']

        features = []
        for feature in feature_list:
            if feature in ['offsets', 'duration']:
                features.append([Fraction(f) for f in song['features'][feature]])
            else:
                features.append(song['features'][feature])

        return np.asarray(features, dtype=float).transpose()

    def get_song_features(self, song1, features=None):
        """
        Get features from song and reduce them

        @param song1: song (features, reduction)
        @param features: list of features to get
        """
        song_features, song_reduction = song1
        song_features = self.get_features(song_features, features)
        reduced_song = song_features[song_reduction, :]
        if features and len(features) == 1:
            reduced_song = reduced_song.flatten()
        return reduced_song

    def get_algorithms(self):
        """
        Get similarity algorithms

        @return: list of similarity algorithms
        """
        return ['cardinality_score', 'correlation_distance', 'city_block_distance', 'euclidean_distance', 'hamming_distance', 'local_alignment_score', 'siam_score']

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
        if algorithm == 'cardinality_score':
            return sim_algorithms.cardinality_score(
                self.get_song_features(
                song1, features=['midipitch', 'onsettick']),
                self.get_song_features(
                song2, features=['midipitch', 'onsettick']))
        elif algorithm == 'correlation_distance':
            return sim_algorithms.correlation_distance(
                self.get_song_features(
                song1, features=['midipitch']),
                self.get_song_features(
                song2, features=['midipitch']))
        elif algorithm == 'city_block_distance':
            return sim_algorithms.cityblock_distance(
                self.get_song_features(
                song1, features=['midipitch']),
                self.get_song_features(
                song2, features=['midipitch']))
        elif algorithm == 'euclidean_distance':
            return sim_algorithms.euclidean_distance(
                self.get_song_features(
                song1, features=['midipitch']),
                self.get_song_features(
                song2, features=['midipitch']))
        elif algorithm == 'hamming_distance':
            return sim_algorithms.hamming_distance(
                self.get_song_features(
                song1, features=['midipitch']),
                self.get_song_features(
                song2, features=['midipitch']))
        elif algorithm == 'local_alignment_score':
            return sim_algorithms.local_alignment_score(
                self.get_song_features(
                song1, features=['midipitch', 'offsets']),
                self.get_song_features(
                song2, features=['midipitch', 'offsets']))
        elif algorithm == 'siam_score':
            return sim_algorithms.siam_score(
                self.get_song_features(
                song1, features=['midipitch', 'offsets', 'duration', 'beatstrength', 'chromaticinterval']),
                self.get_song_features(
                song2, features=['midipitch', 'offsets', 'duration', 'beatstrength', 'chromaticinterval']))
        else:
            raise ValueError(f'Invalid algorithm "{algorithm}"')
