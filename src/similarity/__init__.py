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

        if 'offsets' in feature_list and 'offsets' not in song['features']:
            feature_list.remove('offsets')
            feature_list.append('onsettick')

        features = []
        for feature in feature_list:
            if feature in ['offsets', 'duration']:
                features.append([Fraction(f)
                                for f in song['features'][feature]])
            else:
                features.append(song['features'][feature])

        return np.asarray(features, dtype=float).transpose()

    def get_song_features(self, song, features=None):
        """
        Get features from song and reduce them

        @param song: song (features, reduction)
        @param features: list of features to get
        """
        song_features, song_reduction = song
        song_features = self.get_features(song_features, features)

        song_reduction = [
            r for r in song_reduction if r < song_features.shape[0]]
        reduced_song = song_features[song_reduction, :]
        if features and len(features) == 1:
            reduced_song = reduced_song.flatten()
        return reduced_song

    def get_segment_features(self, song, segment=0, features=None):
        """
        Get segments from song

        @param song: song (features, reduction)
        @param segment: segment to get
        @param features: list of features to get

        @return: segments
        """
        song_features, song_reduction = song
        phrases = song_features['features']['phrase_ix']
        song_features = self.get_features(song_features, features)
        song_reduction = [r for r in song_reduction if r <
                          song_features.shape[0] and phrases[r] == segment]
        reduced_song = song_features[song_reduction, :]
        if features and len(features) == 1:
            reduced_song = reduced_song.flatten()
        return reduced_song

    def get_all_segments_features(self, song, features=None):
        """
        Get all segments from song
        """
        song_features, song_reduction = song
        phrases = song_features['features']['phrase_ix']
        song_features = self.get_features(song_features, features)

        reduced_song = {}

        for segment in sorted(list(set(phrases))):
            song_reduction = [r for r in song_reduction if r <
                              song_features.shape[0] and phrases[r] == segment]
            reduced_song[segment] = song_features[song_reduction, :]
            if features and len(features) == 1:
                reduced_song[segment] = reduced_song[segment].flatten()

        return reduced_song

    def get_algorithms(self):
        """
        Get similarity algorithms

        @return: list of similarity algorithms
        """
        return ['cardinality_score', 'correlation_distance', 'city_block_distance', 'euclidean_distance', 'hamming_distance', 'local_alignment_score', 'local_alignment_score_onsets', 'siam_score', 'siam_score_all']

    def features_per_algorithm(self, algorithm):
        """
        Get features required by similarity algorithm
        """
        if algorithm == 'cardinality_score':
            return ['midipitch', 'onsettick']
        if algorithm == 'local_alignment_score' or algorithm == 'siam_score':
            return ['midipitch', 'offsets']
        if algorithm == 'siam_score_all':
            return ['midipitch', 'offsets', 'duration', 'beatstrength'] #, 'chromaticinterval']
        return ['midipitch']

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
        song1_features = self.get_song_features(
            song1, features=self.features_per_algorithm(algorithm))
        song2_features = self.get_song_features(
            song2, features=self.features_per_algorithm(algorithm))

        if algorithm == 'cardinality_score':
            return sim_algorithms.cardinality_score(song1_features, song2_features)
        elif algorithm == 'correlation_distance':
            return sim_algorithms.correlation_distance(song1_features, song2_features)
        elif algorithm == 'city_block_distance':
            return sim_algorithms.cityblock_distance(song1_features, song2_features)
        elif algorithm == 'euclidean_distance':
            return sim_algorithms.euclidean_distance(song1_features, song2_features)
        elif algorithm == 'hamming_distance':
            return sim_algorithms.hamming_distance(song1_features, song2_features)
        elif 'local_alignment_score' in  algorithm:
            return sim_algorithms.local_alignment_score(song1_features, song2_features)
        elif 'siam_score' in algorithm:
            return sim_algorithms.siam_score(song1_features, song2_features)
        else:
            raise ValueError(f'Invalid algorithm "{algorithm}"')

    def matches_melody_segment(self, song1, song2, algorithm):
        """
        Compute similarity between melody and segments
        """

        song1_features = self.get_song_features(
            song1, features=self.features_per_algorithm(algorithm))

        song2_segment_features = self.get_all_segments_features(
            song2, features=self.features_per_algorithm(algorithm))


