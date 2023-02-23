# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 15:45:52 2023

@author: Nádia Carvalho
"""

from collections import defaultdict

import converter21 as c21
import music21 as m21
import verovio

from .feature_extractors import (GPRExtractor, IOIExtractor, LBDMExtractor,
                                    MetricExtractor, PhraseExtractor,
                                    PitchExtractor)
from .utils import has_meter


class MTCExtractor():
    """
    """

    def __init__(self, path, musical_metadata=None):
        """
        Parse MEI file and extract features
        """
        self.tk = verovio.toolkit()
        self.tk.setOptions({"xmlIdChecksum": False, "xmlIdSeed": 0})
        self.tk.loadFile(path)
        # self.tk.renderToSVGFile('data/temp.svg')

        # m21.environment.Environment('converter21.mei.base')['warnings'] = 0 # type: ignore
        converter = c21.MEIConverter()
        self.music_stream = converter.parseFile(path, verbose=False)

        # self.music_stream.show()

        try:
            self.music_stream = self.music_stream.expandRepeats()
        except:
            print('Error expanding repeats in: ' + path)
            return None

        self.metadata = {}
        if musical_metadata:
            self.metadata = musical_metadata

    def process_stream(self):
        """
        Process Music21 stream to extract JSON data
        """
        try:
            features = defaultdict(list)

            # Scale/Key Features
            features.update(PitchExtractor(self.music_stream,
                            self.metadata).get_all_features())

            # Metric Features
            features.update(MetricExtractor(
                self.music_stream).get_all_features())

            # Phrasic Features
            features.update(PhraseExtractor(self.music_stream,
                            self.metadata).get_all_features())

            # Derived Features
            features.update(IOIExtractor(self.music_stream,
                            features).get_all_features())
            features.update(GPRExtractor(self.music_stream,
                            features).get_all_features())
            features.update(LBDMExtractor(
                self.music_stream, features).get_all_features())

            return features
        except Exception as e:
            print("Error processing stream")

            import os
            import sys

            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] # type: ignore
            print(exc_type, fname, exc_tb.tb_lineno) # type: ignore

            print()

            return None

    def has_meter(self):
        """
        Check if stream has meter
        """
        return has_meter(self.music_stream)

    def has_lyrics(self):
        """
        Check if stream has lyrics
        """
        text = m21.text.assembleLyrics(self.music_stream)
        return 'Vocal' if text is not None else 'Instrumental'