# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 14:11:32 2023

@author: Nádia Carvalho
"""

import glob
from src.parse_mei import MeiParser

if __name__ == '__main__':

    mei_parser = MeiParser()

    mei_songs = sorted(glob.glob('data/original/*.mei'))

    for song in mei_songs[0:1]:
        mei_parser.parse_mei(song)