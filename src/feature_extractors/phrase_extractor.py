# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 16:20:06 2023

@author: Nádia Carvalho
"""

from fractions import Fraction

import numpy as np


class PhraseExtractor():

    def __init__(self, stream, musical_metadata=None):
        """
        Initialize PhraseExtractor
        """
        self.music_stream = stream

        self.metadata = {}
        if musical_metadata:
            self.metadata = musical_metadata

    def get_all_features(self):
        """Get all features phrase related features from the stream"""
        phrases, phrase_ix = self.get_phrases()
        features = {
            'phrasepos': self.get_phrase_position(phrases),
            'phrase_ix': phrase_ix,
            'phrase_end': self.get_phrase_end(),
        }

        features['beatinsong'] = self.get_beat_in_song()
        # features['beatinphrase'], features['beatfractioninphrase'] = self.get_beat_in_phrase()

        return features

    def get_phrases(self):
        """Get phrase position for each note"""
        self.metadata_phrases = [tuple(phrase[1:-1].split(', '))
                                 for phrase in self.metadata['phrases'].split('; ')]

        phrase_starts = [phrase[1] for phrase in self.metadata_phrases]
        phrase_ends = [phrase[2] for phrase in self.metadata_phrases]

        phrase_pos = np.zeros(
            len(self.music_stream.recurse().notes), dtype=int)
        phrase_ix = []

        last_phrase = -1
        for i, note in enumerate(self.music_stream.recurse().notes):

            if f"#{note.id}" in phrase_starts:
                phrase_pos[i] = 1
                last_phrase += 1
            elif f"#{note.id}" in phrase_ends:
                phrase_pos[i] = -1

            phrase_ix.append(last_phrase)

        return list(phrase_pos), phrase_ix

    def get_phrase_position(self, phrases):
        """Get phrase position for each note"""
        total_duration = self.music_stream.duration.quarterLength
        if all(x == 0 for x in phrases):
            print("No phrases found")
            return [note.quarterLength/total_duration for note in self.music_stream.recurse().notes]

        start_indexes = [i for i, x in enumerate(phrases) if x == 1]
        end_indexes = [i for i, x in enumerate(phrases) if x == -1]

        all_notes = self.music_stream.flat.notes
        phrase_pos = []
        for i, end_ind in enumerate(end_indexes):
            start_offset = all_notes[start_indexes[i]].offset
            total_phrase_duration = all_notes[end_ind].offset - start_offset
            phrase_pos.extend([(note.offset - start_offset) /
                              total_phrase_duration for note in all_notes[start_indexes[i]:end_ind+1]])
        return phrase_pos

    def get_phrase_end(self):
        """Get phrase position for each note"""
        phrase_ends = [phrase[2] for phrase in self.metadata_phrases]
        return [True if f"#{note.id}" in phrase_ends else False for note in self.music_stream.recurse().notes]

    def get_beat_in_song(self):
        """Get beat in phrase for each note"""
        start_beat = Fraction(self.music_stream.recurse().notesAndRests[0].beat)
        print(start_beat)

    def get_beat_in_phrase(self, ):
        """Get beat in phrase for each note"""
        pass

