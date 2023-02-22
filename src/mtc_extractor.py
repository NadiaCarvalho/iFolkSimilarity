# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 15:45:52 2023

@author: Nádia Carvalho
"""

import music21 as m21
import converter21 as c21
import verovio

from collections import defaultdict


from src.feature_extractors import PitchExtractor, MetricExtractor, PhraseExtractor, DerivationsExtractor


class MTCExtractor():
    """
    """

    def __init__(self, path, musical_metadata=None):
        """
        Parse MEI file and extract features
        """
        # self.tk = verovio.toolkit()
        # self.tk.setOptions({"xmlIdChecksum": False, "xmlIdSeed": 0})
        # self.tk.loadFile(path)

        # m21.environment.Environment('converter21.mei.base')['warnings'] = 0 # type: ignore
        converter = c21.MEIConverter()
        self.music_stream = converter.parseFile(path, verbose=False)

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
            features.update(MetricExtractor(self.music_stream,
                            self.metadata).get_all_features())

            # Phrasic Features
            features.update(PhraseExtractor(self.music_stream,
                            self.metadata).get_all_features())

            # Mixed Features
            features.update(DerivationsExtractor(self.music_stream,
                            self.metadata, features).get_all_features())

            return features
        except Exception as e:
            print("Error processing stream")
            print(e)
            return None

