# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 13:30:00 2023

@author: Nádia Carvalho
"""

import pandas as pd

pairs_songs = {
    'BINARY': [
        ('PT-1998-XX-DM-001-v1', 'PT-1998-XX-DM-002-v1'),
        ('PT-1998-XX-DM-003-v1', 'PT-1998-XX-DM-004-v1'),
        ('PT-1998-XX-DM-005-v1', 'PT-1998-XX-DM-006-v1'),
        ('PT-1998-XX-DM-007-v1', 'PT-1998-XX-DM-008-v1'),
        ('PT-1998-XX-DM-009-v1', 'PT-1998-XX-DM-010-v1'),
        ('PT-1998-XX-DM-001-v1', 'PT-1998-XX-DM-010-v1'),
        ('PT-1998-XX-DM-002-v1', 'PT-1998-XX-DM-003-v1'),
        ('PT-1998-XX-DM-004-v1', 'PT-1998-XX-DM-005-v1'),
        ('PT-1998-XX-DM-006-v1', 'PT-1998-XX-DM-007-v1'),
        ('PT-1998-XX-DM-008-v1', 'PT-1998-XX-DM-009-v1'),
    ],
    'TERNARY': [
        ('PT-1998-XX-DM-018-v1', 'PT-1998-XX-DM-018-v2'),
        ('PT-1998-XX-DM-032-v1', 'PT-1999-BR-DM-005-v1'),
        ('PT-1999-XX-DM-011-v1', 'PT-1999-XX-DM-011-v2'),
        ('PT-1999-XX-DM-019-v1', 'PT-1999-XX-DM-019-v2'),
        ('PT-1999-XX-DM-021-v1', 'PT-1999-XX-DM-022-v1'),
        ('PT-1998-XX-DM-018-v1', 'PT-1999-XX-DM-022-v1'),
        ('PT-1998-XX-DM-018-v2', 'PT-1998-XX-DM-032-v1'),
        ('PT-1999-BR-DM-005-v1', 'PT-1999-XX-DM-011-v1'),
        ('PT-1999-XX-DM-011-v2', 'PT-1999-XX-DM-019-v1'),
        ('PT-1999-XX-DM-019-v2', 'PT-1999-XX-DM-021-v1'),
    ],
    'INTERCATEGORIES': [
        ('PT-1998-XX-DM-001-v1', 'PT-1998-XX-DM-018-v1'),
        ('PT-1998-XX-DM-002-v1', 'PT-1998-XX-DM-018-v2'),
        ('PT-1998-XX-DM-003-v1', 'PT-1998-XX-DM-032-v1'),
        ('PT-1998-XX-DM-004-v1', 'PT-1999-BR-DM-005-v1'),
        ('PT-1998-XX-DM-005-v1', 'PT-1999-XX-DM-011-v1'),
        ('PT-1998-XX-DM-006-v1', 'PT-1999-XX-DM-011-v2'),
        ('PT-1998-XX-DM-007-v1', 'PT-1999-XX-DM-019-v1'),
        ('PT-1998-XX-DM-008-v1', 'PT-1999-XX-DM-019-v2'),
        ('PT-1998-XX-DM-009-v1', 'PT-1999-XX-DM-021-v1'),
        ('PT-1998-XX-DM-010-v1', 'PT-1999-XX-DM-022-v1'),
    ],
}

if __name__ == '__main__':
    df = pd.read_csv('../old_code/similarity/answers3.csv')

    headers_1 = [item for sublist in [[pv] * 40 for pv in pairs_songs.keys()]
                 for item in sublist]
    headers_2 = [item for sublist in [
        [f'{song1}_{song2}'] * 4 for pv in pairs_songs.values() for (song1, song2) in pv] for item in sublist]
    headers_3 = [item for sublist in [['Melodic Contour', 'Rhythm', 'Motives',
                                       'Global'] * 10 for _ in pairs_songs.keys()] for item in sublist]
    original_3 = {'Melodic Contour': 'Contorno Melódico',
                  'Rhythm': 'Ritmo', 'Motives': 'Motivos', 'Global': 'Global'}

    new_df = pd.DataFrame(index=df.index, columns=[
                          headers_1, headers_2, headers_3])

    for i, (category, pairs) in enumerate(pairs_songs.items()):
        for j, pair in enumerate(pairs):
            for header in headers_3:
                for k in df.index:
                    if i == 0 and j == 0:
                        new_df.at[k, (category, f'{pair[0]}_{pair[1]}',
                                      header)] = df[original_3[header]].iloc[k]
                    else:
                        new_df.at[k, (category, f'{pair[0]}_{pair[1]}', header)
                                  ] = df[f'{original_3[header]}.{i * 10 + j}'].iloc[k]

    new_df.to_excel('../eval_data/annotations/form-answers.xlsx')
