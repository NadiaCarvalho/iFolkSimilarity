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
        "PT-1998-XX-DM-018",  # 'A Rolinha Andou, Andou - Voz inferior',
        "PT-1998-XX-DM-018",  # 'A Rolinha Andou, Andou - Voz superior',
        "PT-1998-XX-DM-032",  # 'Disse o Galo para a Galinha',
        "PT-1999-BR-DM-005",  # 'Teresinha de Jesus',
        'PT-1999-XX-DM-011',  # 'Os Passarinhos - Voz inferior',
        'PT-1999-XX-DM-011',  # 'Os Passarinhos - Voz superior',
        'PT-1999-XX-DM-019',  # 'Lá Vai o Comboio - Voz inferior',
        'PT-1999-XX-DM-019',  # 'Lá Vai o Comboio - Voz superior',
        'PT-1999-XX-DM-021',  # "Sant' Antóino Se Levantou",
        'PT-1999-XX-DM-022',  # 'Senhores Donos Da Casa',
    ]
}


def parse_files(category='binary'):
    """
    Parse all MEI songs in data/{category}/original and
    save the parsed data in data/{category}/parsed

    @param category: binary or ternary
    """
    from src.parser import MeiParser
    mei_parser = MeiParser()

    for song in set(SONGS_TO_EVAL[category.upper()]):
        song_features = mei_parser.parse_mei(
            f'eval_data/{category.lower()}/original/{song}.mei')
        try:
            json.dump(song_features, open(
                f'eval_data/{category.lower()}/parsed/{song}.json', 'w'), ensure_ascii=False, indent=4)
        except:
            print('Error parsing song: ' + song)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[ # type: ignore
                1]
            print(exc_type, fname, exc_tb.tb_lineno)  # type: ignore
            print()

if __name__ == '__main__':

    from src.parser import MeiParser
    mei_parser = MeiParser()
    song_features = mei_parser.parse_mei(
            f'eval_data/binary/original/PT-1998-XX-DM-002.mei')
    json.dump(song_features, open(
                f'eval_data/binary/parsed/PT-1998-XX-DM-002.json', 'w'), ensure_ascii=False, indent=4)

    #parse_files('binary')
    #parse_files('ternary')
