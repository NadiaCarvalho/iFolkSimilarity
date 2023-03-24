# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 14:40:32 2023

@author: Nádia Carvalho
"""

from collections.abc import MutableMapping
import json
import os
import sys
import time

import pandas as pd
import progressbar as pb

SONGS_TO_EVAL = {
    'BINARY': [
        'PT-1998-XX-DM-001',  # 'A Barca Virou',
        'PT-1998-XX-DM-010',  # 'Rosa Branca ao Peito',
        'PT-1998-XX-DM-002',  # 'Lá Vai uma, Lá vão Duas',
        'PT-1998-XX-DM-003',  # 'Senhora D. Anica',
        'PT-1998-XX-DM-004',  # 'Pantaleão',
        'PT-1998-XX-DM-005',  # 'Passa, Passa, Gabriel',
        'PT-1998-XX-DM-006',  # 'Ó Terrá, Tá, Tá',
        'PT-1998-XX-DM-007',  # 'Que Linda Falua',
        'PT-1998-XX-DM-008',  # 'Fui Ao Jardim da Celeste',
        'PT-1998-XX-DM-009',  # 'Marcha Soldado',

    ],
    'TERNARY': [
        "PT-1998-XX-DM-018-v1",  # 'A Rolinha Andou, Andou - Voz inferior',
        "PT-1998-XX-DM-018-v2",  # 'A Rolinha Andou, Andou - Voz superior',
        "PT-1998-XX-DM-032",  # 'Disse o Galo para a Galinha',
        "PT-1999-BR-DM-005",  # 'Teresinha de Jesus',
        'PT-1999-XX-DM-011-v1',  # 'Os Passarinhos - Voz inferior',
        'PT-1999-XX-DM-011-v2',  # 'Os Passarinhos - Voz superior',
        'PT-1999-XX-DM-019-v1',  # 'Lá Vai o Comboio - Voz inferior',
        'PT-1999-XX-DM-019-v2',  # 'Lá Vai o Comboio - Voz superior',
        'PT-1999-XX-DM-021',  # "Sant' Antóino Se Levantou",
        'PT-1999-XX-DM-022',  # 'Senhores Donos Da Casa',
    ]
}


def flatten(d, parent_key='', sep='_'):
    """
    Flatten a dictionary

    @param d: dictionary
    @param parent_key: parent key
    @param sep: separator

    @return: flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def dump_json_features(category, song, song_features):
    """
    Dump the song features to a json file

    @param category: binary or ternary
    @param song: song id
    @param song_features: song features
    """
    try:
        json.dump(song_features, open(
            f'eval_data/{category.lower()}/parsed/{song}.json', 'w'), ensure_ascii=False, indent=4)
    except:
        print('Error parsing song: ' + song)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[  # type: ignore
            1]
        print(exc_type, fname, exc_tb.tb_lineno)  # type: ignore
        print()


def get_songs_category(category='binary'):
    """
    Get all songs and their features and reductions

    @param category: binary or ternary

    @return songs: list of songs
    @return cats_songs: dict of songs and their features and reductions
    """
    reduction_indexes = json.load(
        open(f'eval_data/{category.lower()}/reductions.json', 'r'))
    songs = sorted(reduction_indexes.keys())
    cats_songs = {}
    for song in songs:
        cats_songs[song] = {
            'features': json.load(open(f'eval_data/{category.lower()}/parsed/{song}.json', 'r')),
            'reductions': flatten(reduction_indexes[song])
        }
    return songs, cats_songs


def parse_files(category='binary'):
    """
    Parse all MEI songs in data/{category}/original and
    save the parsed data in data/{category}/parsed

    @param category: binary or ternary
    """
    from src.parser import MeiParser
    mei_parser = MeiParser()

    for song in sorted(set(SONGS_TO_EVAL[category.upper()])):
        print(song)
        song_features = mei_parser.parse_mei(
            f'eval_data/{category.lower()}/original/{song}.mei')

        if 'id' in song_features.keys():  # type: ignore
            dump_json_features(category, song, song_features)
        else:
            for key, song_features in song_features.items():  # type: ignore
                dump_json_features(category, f'{song}-{key}', song_features)


def make_reduction(song='data/parsed/PT-1981-BR-MG-004.json', cat='combined', distance='cosine', normalization='minmax', name=False):
    """
    Test Reduction for song

    @param song: song id
    @param cat: tonal, intervallic, metrical, combined
    @param distance: euclidean, cosine, manhattan
    @param normalization: minmax, zscore
    @param name: name of the reduction

    @return: reduction indexes
    """

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
        title=f'{cat.capitalize()} Reduc. {f"({distance} distance)," if cat in ["tonal", "combined"]  else ""} {f" Norm. {normalization}," if cat == "combined" else ""} \n song {song_id}')

    indexes = {}

    for deg in cat_degrees:
        indexes_reduction = reduction.reduce(
            song_features, reduction_type=cat, degree=deg, distance=distance, normalization=normalization, graphs=name)
        reduced_song = reduction.show_reduced_song(
            song_features, indexes_reduction, name=f'Degree: {f"{str(int(deg*100))}%" if cat != "metrical" else f"{str(deg)}"}')
        all_reduction_score.insert(0.0, reduced_song)

        indexes[deg] = indexes_reduction

    path = song[:-5].replace('parsed', 'reductions')
    os.makedirs(path, exist_ok=True)

    all_reduction_score.write(
        'musicxml', f'{path}/{song_id}-{cat}{f"-{distance}" if cat in ["tonal", "combined"] else ""}{f"-{normalization}" if cat == "combined" else ""}.xml')

    return indexes


def reduce_all_songs(category='binary'):
    """
    Reduce all songs in data/{category}/parsed

    @param category: binary or ternary

    @return all_indexes: dict of songs and their reductions
    """
    all_indexes = {}

    for song in sorted(SONGS_TO_EVAL[category.upper()]):
        if song[-3:] != '-v1' and song[-3:] != '-v2':
            song = song + '-v1'

        all_indexes[song] = {}

        for cat in ['metrical', 'intervallic']:
            all_indexes[song][cat] = make_reduction(
                song=f'eval_data/{category.lower()}/parsed/{song}.json', cat=cat)

        os.makedirs(
            f'eval_data/{category.lower()}/combined_graphs/{song}', exist_ok=True)

        for cat in ['tonal', 'combined']:
            all_indexes[song][cat] = {}
            for distance in ['cosine', 'euclidean']:
                if cat == 'tonal':
                    all_indexes[song][cat][distance] = make_reduction(
                        song=f'eval_data/{category.lower()}/parsed/{song}.json', cat=cat, distance=distance)
                else:
                    all_indexes[song][cat][distance] = {}
                    for norm in ['minmax', 'zscore']:
                        all_indexes[song][cat][distance][norm] = make_reduction(
                            song=f'eval_data/{category.lower()}/parsed/{song}.json', cat=cat, distance=distance, normalization=norm, name=f'eval_data/{category.lower()}/combined_graphs/{song}/{song}-{distance}-{norm}.png')

    json.dump(all_indexes, open(
        f'eval_data/{category.lower()}/reductions.json', 'w'), ensure_ascii=False, indent=4)


def similarity_intra_category(category='binary'):
    """
    Compute the similarity between songs in the same category

    @param category: binary or ternary
    """
    from src.similarity import SimilarityCalculator
    similarity_calculator = SimilarityCalculator()

    songs, cats_songs = get_songs_category(category)

    for algorithm in similarity_calculator.get_algorithms():
        for cat in cats_songs[songs[0]]['reductions'].keys():
            print('Calculating Similarities for', cat, 'with', algorithm)

            fold = f'eval_data/{category.lower()}/similarity/{algorithm}/{cat.split("_")[0]}'
            os.makedirs(fold, exist_ok=True)

            df = pd.DataFrame(columns=songs, index=songs)

            with pb.ProgressBar(max_value=len(songs)*len(songs)) as bar:
                for song_1, all_song_1 in cats_songs.items():
                    for song_2, all_song_2 in cats_songs.items():
                        df[song_1][song_2] = similarity_calculator.similarity_between_two_songs(
                            (all_song_1['features'],
                             all_song_1['reductions'][cat]),
                            (all_song_2['features'],
                             all_song_2['reductions'][cat]),
                            algorithm=algorithm,
                        )
                        bar.update(int(bar.value) + 1) # type: ignore
                        time.sleep(0.01)

            df.to_excel(f'{fold}/{cat}.xlsx')


def similarity_inter_category():
    """
    Compute the similarity between songs in different categories

    @param category: binary or ternary
    """
    from src.similarity import SimilarityCalculator
    similarity_calculator = SimilarityCalculator()

    songs_binary, cats_songs_binary = get_songs_category('binary')
    songs_ternary, cats_songs_ternary = get_songs_category('ternary')

    for algorithm in similarity_calculator.get_algorithms():
        for cat in cats_songs_binary[songs_binary[0]]['reductions'].keys():
            print('Calculating Similarities for', cat, 'with', algorithm)

            fold = f'eval_data/intercategories/similarity/{algorithm}/{cat.split("_")[0]}'
            os.makedirs(fold, exist_ok=True)

            df = pd.DataFrame(columns=songs_binary, index=songs_ternary)

            with pb.ProgressBar(max_value=len(songs_binary)*len(songs_ternary)) as bar:
                for song_1, all_song_1 in cats_songs_binary.items():
                    for song_2, all_song_2 in cats_songs_ternary.items():
                        df[song_1][song_2] = similarity_calculator.similarity_between_two_songs(
                            (all_song_1['features'],
                             all_song_1['reductions'][cat]),
                            (all_song_2['features'],
                             all_song_2['reductions'][cat]),
                            algorithm=algorithm,
                        )
                        bar.update(int(bar.value) + 1) # type: ignore
                        time.sleep(0.01)

            df.to_excel(f'{fold}/{cat}.xlsx')


if __name__ == '__main__':
    # parse_files('ternary')
    # reduce_all_songs('ternary')
    # similarity_intra_category('ternary')
    similarity_inter_category()
