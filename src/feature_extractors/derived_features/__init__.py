# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 16:20:06 2023

@author: Nádia Carvalho
"""

from collections import defaultdict

import numpy as np

class DerivationsExtractor():

    def __init__(self, stream, musical_metadata=None, features={}):
        """
        Initialize PhraseExtractor
        """
        self.music_stream = stream

        self.metadata = {}
        if musical_metadata:
            self.metadata = musical_metadata

        self.base_features = features

    def get_all_features(self):
        """Get all derivated features from the stream"""

        self.base_features.update(self.get_all_IOI_features())
        self.base_features.update(self.get_all_gpr_features())
        self.base_features.update(self.get_all_lbdm_features())

        return self.base_features

    def get_all_IOI_features(self):
        """Get all IOI derivated features from the stream"""
        from .ioi_extractor import IOIExtractor
        return IOIExtractor(self.music_stream, self.base_features).get_all_features()

    def get_all_gpr_features(self):
        """Get all gpr derivated features from the stream"""
        from .gpr_extractor import GPRExtractor
        return GPRExtractor(self.music_stream, self.base_features).get_all_features()

    def get_all_lbdm_features(self):
        """Get all lbdm derivated features from the stream"""
        from .lbdm_extractor import LBDMExtractor
        return LBDMExtractor(self.music_stream, self.base_features).get_all_features()

