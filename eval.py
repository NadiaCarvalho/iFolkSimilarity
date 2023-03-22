# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 14:40:32 2023

@author: Nádia Carvalho
"""

import json
import os
import sys

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


def make_reduction(song='data/parsed/PT-1981-BR-MG-004.json', cat='combined', distance='cosine'):
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

    path = song[:-5].replace('parsed', 'reductions')
    os.makedirs(path, exist_ok=True)

    all_reduction_score.write(
        'musicxml', f'{path}/{song_id}-{cat}-{distance}.xml')


def reduce_all_songs(category='binary'):
    """
    Reduce all songs in data/{category}/parsed
    """
    for song in sorted(SONGS_TO_EVAL[category.upper()]):
        if song[-3:] != '-v1' and song[-3:] != '-v2':
            song = song + '-v1'

        for cat in ['metrical', 'intervallic']:
            make_reduction(
                song=f'eval_data/{category.lower()}/parsed/{song}.json', cat=cat)

        for cat in ['tonal', 'combined']:
            for distance in ['cosine', 'euclidean']:
                make_reduction(
                    song=f'eval_data/{category.lower()}/parsed/{song}.json', cat=cat, distance=distance)


if __name__ == '__main__':

    # parse_files('binary')
    # parse_files('ternary')

    make_reduction(song='eval_data/binary/parsed/PT-1998-XX-DM-001-v1.json',
                   cat='metrical', distance='cosine')

    reduce_all_songs('ternary')
