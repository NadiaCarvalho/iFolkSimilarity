import random
import json

import pandas as pd
from MTCFeatures import MTCFeatureLoader

from src.similarity import SimilarityCalculator

if __name__ == '__main__':

    similarity_calculator = SimilarityCalculator()

    fl = MTCFeatureLoader(
        'eval_data/MTCFeatures/MTC-ANN-2.0.1_sequences-1.1.jsonl.gz')

    sim_df = pd.read_csv(
        'eval_data/MTCFeatures/MTC-ANN-phrase-similarity.csv', sep=',', header=0, index_col=0)

    fam = 'O_God_ik_leef_in_nood'

    songs = sorted(list(fl.applyFilter(
        ('inTuneFamilies', fam))), key=lambda x: x['id'])
    reductions =  json.load(
            open(f'eval_data/MTCFeatures/reductions/{fam}.json', 'r'))

    for song1 in songs[0:1]:
        song1_feats = (song1, reductions[song1['id']]['metrical']['0.75'])

        for song2 in songs[1:2]:
            song2_feats = (song2, reductions[song2['id']]['metrical']['0.75'])

            seg = similarity_calculator.matches_melody_segment(song1_feats, song2_feats, 'cardinality_score')

            print(sim_df.loc[[song1['id'], song2['id']]])
