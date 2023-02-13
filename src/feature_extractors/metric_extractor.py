# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:12:36 2023

@author: Nádia Carvalho
"""

from fractions import Fraction
from imapy_music import IMA


class MetricExtractor():

    def __init__(self, stream, musical_metadata=None):
        """
        """
        self.music_stream = stream

        self.metadata = {}
        if musical_metadata:
            self.metadata = musical_metadata

    def get_all_features(self):

        features = {
            'onsettick': self.get_onsettick(),
            'duration': self.get_durations(),
            'duration_frac': self.get_duration_fraction(),
            'duration_fullname': self.get_duration_fullname(),
        }

        return features

    def get_durations(self):
        """
        Get the durations of all notes in the stream
        """
        return [note.duration.quarterLength for note in self.music_stream.flat.notes]

    def get_duration_fraction(self):
        """
        Get the duration fraction of all notes in the stream
        """
        return [str(Fraction(note.duration.quarterLength)) for note in self.music_stream.flat.notes]

    def get_duration_fullname(self):
        """
        Get the duration fullname of all notes in the stream
        """
        return [note.duration.fullName for note in self.music_stream.flat.notes]

    def get_onsettick(self):
        """
        Get the onset tick of all notes in the stream
        """
        return [note.offset for note in self.music_stream.flat.notes]
