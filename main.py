# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 14:11:32 2023

@author: Nádia Carvalho
"""

import glob
import json
import os
import sys
import time


def parse_mei_songs():
    """Parse all MEI songs in data/original and save the parsed data in data/parsed"""

    from src.parser import MeiParser
    mei_parser = MeiParser()

    mei_songs = sorted(glob.glob('data/original/*.mei'))

    for song in mei_songs:
        song_features = mei_parser.parse_mei(song)
        if song_features:
            try:
                json.dump(song_features, open('data/parsed/' + song.split('/')
                                              [-1].split('.')[0] + '.json', 'w'), ensure_ascii=False, indent=4)
            except:
                print('Error parsing song: ' + song)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[  # type: ignore
                    1]
                print(exc_type, fname, exc_tb.tb_lineno)  # type: ignore
                print()

            # View ties/ligatures in notes


def test_reduction(song='data/parsed/PT-1981-BR-MG-004.json', cat='combined', distance='cosine'):
    """Test Reduction for song"""

    from src.reduction import Reduction
    reduction = Reduction()

    song_id = song.split('/')[-1].split('.')[0]
    song_features = json.load(open(song, 'r'))

    cat_degrees = [1.0, 0.75, 0.5, 0.25, 0.1]
    if cat == 'metrical':
        cat_degrees = [d/100 for d in range(0, 100, 25)]

    import music21 as m21

    all_reduction_score = m21.stream.Score()  # type: ignore
    all_reduction_score.metadata = m21.metadata.Metadata(
        title=f'{cat.capitalize()} Reduction {f"({distance} distance)" if cat in ["tonal", "combined"]  else ""} \n song {song_id}')

    for deg in cat_degrees:
        indexes_reduction = reduction.reduce(
            song_features, reduction_type=cat, degree=deg, distance=distance)
        reduced_song = reduction.show_reduced_song(
            song_features, indexes_reduction, name=f'Degree: {f"{str(int(deg*100))}%" if cat != "metrical" else f"{str(deg)}"}')
        all_reduction_score.insert(0.0, reduced_song)

    all_reduction_score.show()


def reduce_songs():
    """Reduce all parsed songs in data/parsed and save the reduced data in data/reduced"""

    from src.reduction import Reduction
    reduction = Reduction()

    parsed_songs = sorted(glob.glob('data/parsed/*.json'))

    reductions = {}

    import progressbar as pb
    with pb.ProgressBar(max_value=len(parsed_songs)) as p_bar:
        for i, song in enumerate(parsed_songs):
            song_id = song.split('/')[-1].split('.')[0]
            song_features = json.load(open(song, 'r'))

            os.makedirs(f'data/reduced/{song_id}/', exist_ok=True)

            import music21 as m21

            reductions[song_id] = {}
            for cat in ['intervallic', 'tonal', 'metrical', 'combined']:

                # all_reduction_score = m21.stream.Score()  # type: ignore
                # all_reduction_score.metadata = m21.metadata.Metadata(
                #     title=f'{song_id} - {cat}')

                reductions[song_id][cat] = {}
                cat_degrees = [1.0, 0.75, 0.5, 0.25, 0.1]
                if cat == 'metrical':
                    cat_degrees = [d/100 for d in range(0, 100, 25)]

                for deg in cat_degrees:
                    if cat in ['tonal', 'combined']:
                        reductions[song_id][cat][str(deg)] = {}
                        for distance in ['euclidean', 'cosine']:
                            red = reduction.reduce(
                                song_features, reduction_type=cat, degree=deg, distance=distance)
                            reductions[song_id][cat][str(deg)][distance] = red

                            # reduced_song = reduction.show_reduced_song(
                            #     song_features, red, name=f'D{deg*100}% - {distance}')
                            # all_reduction_score.insert(0.0, reduced_song)
                    else:
                        red = reduction.reduce(
                            song_features, reduction_type=cat, degree=deg)
                        reductions[song_id][cat][str(deg)] = red

                        # reduced_song = reduction.show_reduced_song(
                        #     song_features, red, name=f'D{f"{deg*100}%" if cat != "metrical" else f"{deg}"}')
                        # all_reduction_score.insert(0.0, reduced_song)

                # type: ignore
                # all_reduction_score.write('musicxml', f'data/reduced/{song_id}/{cat.replace(" ", "-")}.musicxml')
            p_bar.update(i)
            time.sleep(0.01)

    json.dump(reductions, open('data/reductions.json', 'w'),
              ensure_ascii=False, indent=4)


def test_compute_similarity_values(song1, song2, cat='intervallic', degree=1.0, distance='cosine', algorithm='cardinality_score'):
    """Test compute_similarity_values for song1 and song2"""

    from src.similarity import SimilarityCalculator
    similarity_calculator = SimilarityCalculator()

    song1_id = song1.split('/')[-1].split('.')[0]
    song2_id = song2.split('/')[-1].split('.')[0]

    reductions = json.load(open('data/reductions.json', 'r'))

    indexes_reduction1 = reductions[song1_id][cat][str(degree)]
    if cat in ['tonal', 'combined']:
        indexes_reduction1 = reductions[song1_id][cat][str(degree)][distance]

    indexes_reduction2 = reductions[song2_id][cat][str(degree)]
    if cat in ['tonal', 'combined']:
        indexes_reduction2 = reductions[song2_id][cat][str(degree)][distance]

    song1_features = json.load(open(song1, 'r'))
    song2_features = json.load(open(song2, 'r'))

    score = similarity_calculator.similarity_between_two_songs(
        song1=(song1_features, indexes_reduction1),
        song2=(song2_features, indexes_reduction2),
        algorithm=algorithm)

    print(score)

if __name__ == '__main__':

    # parse_mei_songs() # DONE for the Portuguese songs :D
    #reduce_songs()

    test_reduction(song='data/parsed/PT-1998-XX-DM-002.json', cat='combined', distance='cosine')
    # test_compute_similarity_values(song1='data/parsed/PT-1998-BR-DM-021.json', song2='data/parsed/PT-1998-BR-DM-022.json')

