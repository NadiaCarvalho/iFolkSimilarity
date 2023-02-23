# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 14:11:32 2023

@author: Nádia Carvalho
"""

import glob
import json
import os
import sys


def parse_mei_songs():
    """Parse all MEI songs in data/original and save the parsed data in data/parsed"""

    from src.parser.parse_mei import MeiParser
    mei_parser = MeiParser()

    # mei_songs = sorted(glob.glob('data/original/*.mei'))
    song = 'PT-1998-XX-DM-002'
    mei_songs = [f'data/original/{song}.mei']

    for song in mei_songs:
        song_features = mei_parser.parse_mei(song)
        if song_features:
            try:
                json.dump(song_features, open('data/parsed/' + song.split('/')
                                              [-1].split('.')[0] + '.json', 'w'), ensure_ascii=False, indent=4)
            except:
                print('Error parsing song: ' + song)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[ # type: ignore
                    1]
                print(exc_type, fname, exc_tb.tb_lineno)  # type: ignore
                print()


if __name__ == '__main__':

    parse_mei_songs()
