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


def parse_files(category='binary', filter=None):
    """
    Parse all MEI songs in data/{category}/original and
    save the parsed data in data/{category}/parsed

    @param category: binary or ternary
    """
    from src.parser import MeiParser
    mei_parser = MeiParser()

    songs = sorted(set(SONGS_TO_EVAL[category.upper()]))
    if filter:
        songs = [song for song in songs if song in filter]

    for song in songs:
        song = song.replace("-v1", "").replace("-v2", "")
        song_features = mei_parser.parse_mei(
            f'eval_data/{category.lower()}/original/{song}.mei')

        if 'id' in song_features.keys():  # type: ignore
            dump_json_features(category, song, song_features)
        else:
            for key, song_features in song_features.items():  # type: ignore
                dump_json_features(category, f'{song}-{key}', song_features)


def make_reduction(song='data/parsed/PT-1981-BR-MG-004.json', cat='combined', distance='cosine', normalization='minmax', name: str | bool = False):
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

    return reduce_features(song, cat, distance, normalization, name, reduction, song_id, song_features)


def reduce_features(song, cat, distance, normalization, name, reduction, song_id, song_features):
    cat_degrees = [1.0, 0.75, 0.5, 0.25]
    # cat_degrees = sorted([(i+1)/10 for i in range(0, 10)], reverse=True)
    # if cat == 'metrical':
    #     cat_degrees = [d/100 for d in range(0, 100, 25)]

    import music21 as m21

    all_reduction_score = m21.stream.Score()  # type: ignore
    all_reduction_score.metadata = m21.metadata.Metadata(
        title=f'{cat.capitalize()} Reduc. {f"({distance} distance)," if cat in ["tonal", "combined", "combined_with_duration"]  else ""} {f" Norm. {normalization}," if "combined" in cat else ""} \n song {song_id}')

    indexes = {}

    for deg in cat_degrees:
        indexes_reduction = reduction.reduce(
            song_features, reduction_type=cat, degree=deg, distance=distance, normalization=normalization, graphs=name)
        reduced_song = reduction.show_reduced_song(
            song_features, indexes_reduction, name=f'Degree: {f"{str(int(deg*100))}%"}')  # if cat != "metrical" else f"{str(deg)}"}')
        all_reduction_score.insert(0.0, reduced_song)

        indexes[deg] = indexes_reduction

    path = song[:-5].replace('parsed', 'reductions')
    os.makedirs(path, exist_ok=True)

    # all_reduction_score.show()

    all_reduction_score.write(
        'musicxml', f'{path}/{song_id}-{cat}{f"-{distance}" if cat in ["tonal", "combined", "combined_with_duration"] else ""}{f"-{normalization}" if "combined" in cat else ""}.xml')

    return indexes


def reduce_all_songs(category='binary'):
    """
    Reduce all songs in data/{category}/parsed

    @param category: binary or ternary

    @return all_indexes: dict of songs and their reductions
    """
    all_indexes = {}

    songs = sorted(SONGS_TO_EVAL[category.upper()])
    with pb.ProgressBar(max_value=len(songs)*(3+2+2*2*2)) as bar:
        bar.update(0)
        for song in songs:
            if song[-3:] != '-v1' and song[-3:] != '-v2':
                song = song + '-v1'

            all_indexes[song] = {}

            for cat in ['metrical', 'intervallic', 'durational']:
                all_indexes[song][cat] = make_reduction(
                    song=f'eval_data/{category.lower()}/parsed/{song}.json', cat=cat)
                bar.update(bar.value + 1)  # type: ignore
                time.sleep(0.001)

            os.makedirs(
                f'eval_data/{category.lower()}/combined_graphs/{song}', exist_ok=True)

            for cat in ['tonal', 'combined', 'combined_with_duration']:
                all_indexes[song][cat] = {}
                for distance in ['cosine', 'euclidean']:
                    if cat == 'tonal':
                        all_indexes[song][cat][distance] = make_reduction(
                            song=f'eval_data/{category.lower()}/parsed/{song}.json', cat=cat, distance=distance)
                        bar.update(bar.value + 1)  # type: ignore
                        time.sleep(0.001)
                    else:
                        all_indexes[song][cat][distance] = {}
                        for norm in ['minmax', 'zscore']:
                            name = f'eval_data/{category.lower()}/combined_graphs/{song}/{song}-{distance}-{norm}.png'
                            all_indexes[song][cat][distance][norm] = make_reduction(
                                song=f'eval_data/{category.lower()}/parsed/{song}.json', cat=cat, distance=distance, normalization=norm, name=name)
                            bar.update(bar.value + 1)  # type: ignore
                            time.sleep(0.001)

    json.dump(all_indexes, open(
        f'eval_data/{category.lower()}/reductions.json', 'w'), ensure_ascii=False, indent=4)


def similarity_pairs():
    """
    Compute the similarity between all pairs of songs
    """
    from src.similarity import SimilarityCalculator
    similarity_calculator = SimilarityCalculator()

    _, reductions_binary = get_songs_category('binary')
    _, reductions_ternary = get_songs_category('ternary')

    number_of_pairs = len([item for x in pairs_songs.values() for item in x])
    number_reduction = len(
        reductions_binary['PT-1998-XX-DM-001-v1']['reductions'].keys())
    number_algorithms = len(similarity_calculator.get_algorithms())

    number_comparisons = number_of_pairs * number_reduction * number_algorithms

    df = pd.DataFrame(columns=[
                      'category', 'songs', 'reduction'] + similarity_calculator.get_algorithms())

    with pb.ProgressBar(max_value=number_comparisons) as bar:
        for cat, pairs in pairs_songs.items():

            if cat.lower() == 'binary':
                reductions = reductions_binary
            elif cat.lower() == 'ternary':
                reductions = reductions_ternary
            else:
                reductions = {**reductions_binary, **reductions_ternary}

            for (song1, song2) in pairs:
                # print('Calculating Similarities for', cat, 'between', song1, 'and', song2)

                for reduction in reductions[song1]['reductions'].keys():
                    row = {'category': cat, 'songs': f'{song1}-{song2}',
                           'reduction': reduction}
                    for algorithm in similarity_calculator.get_algorithms():
                        row[algorithm] = similarity_calculator.similarity_between_two_songs(
                            (reductions[song1]['features'],
                                reductions[song1]['reductions'][reduction]),
                            (reductions[song2]['features'],
                                reductions[song2]['reductions'][reduction]),
                            algorithm=algorithm,)
                        bar.update(bar.value + 1)  # type: ignore

                    df = pd.concat([df, pd.DataFrame([row])],
                                   axis=0, ignore_index=True)

    df.set_index(['category', 'songs', 'reduction'], inplace=True)
    df.to_excel('eval_data/copoem_similarity_pairs.xlsx', index=True)


def test_similarity():
    song = 'PT-1998-XX-DM-001-v1'
    features = json.load(open(f'eval_data/binary/parsed/{song}.json', 'r'))
    reduction = make_reduction(
        song=f'eval_data/binary/parsed/{song}.json', cat='metrical')

    from src.similarity import SimilarityCalculator
    similarity_calculator = SimilarityCalculator()
    algo = similarity_calculator.similarity_between_two_songs(
        (features, reduction[1.0]),
        (features, reduction[1.0]),
        algorithm='siam_score')

    print(algo)


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
                        bar.update(int(bar.value) + 1)  # type: ignore
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
                        bar.update(int(bar.value) + 1)  # type: ignore
                        time.sleep(0.01)

            df.to_excel(f'{fold}/{cat}.xlsx')


def violin_plots_annotator():
    from src.annotations import AnnotationComparer

    annotations = pd.read_excel(
        'eval_data/annotations/form-answers.xlsx', header=[0, 1, 2], index_col=0)

    comparer = AnnotationComparer()
    comparer.create_violin_plots(pd.DataFrame(annotations.iloc[[1, 2]]))

def evaluate():
    from itertools import combinations
    from src.annotations import AnnotationComparer

    annotations = pd.read_excel(
        'eval_data/annotations/form-answers.xlsx', header=[0, 1, 2], index_col=0)

    similarities = pd.read_excel(
        'eval_data/copoem_similarity_pairs.xlsx', index_col=[0, 1, 2], header=0)

    comparer = AnnotationComparer()

    for r in range(1, 4):
        for p in combinations(range(1, 4), r):
            if r == 1:
                comparer.compare_annotations_joined(pd.DataFrame(
                    annotations.iloc[p[0]-1]), similarities, name=f'Annotator-{p[0]}')
            else:
                media = pd.DataFrame(pd.DataFrame(
                    annotations.iloc[[px-1 for px in p]]).mean(axis=0))
                comparer.compare_annotations_joined(
                    media, similarities, name=f"Annotator-{'-'.join([str(i) for i in p])}")

    for r in range(1, 4):
        for p in combinations(range(1, 4), r):
            comparer.create_comparison_graphs(
                f'eval_data/annotations/Annotator-{"-".join([str(i) for i in p])}/global_pearson.xlsx')
            comparer.create_comparison_graphs(
                f'eval_data/annotations/Annotator-{"-".join([str(i) for i in p])}/global_rsquare.xlsx')


def general_graphs_combined():
    """Create general graphs"""
    df_an2 = pd.read_excel(
        'eval_data/annotations/Annotator-2/global_rsquare.xlsx', header=[0, 1, 2], index_col=0)
    df_an3 = pd.read_excel(
        'eval_data/annotations/Annotator-3/global_rsquare.xlsx', header=[0, 1, 2], index_col=0)
    df_an23 = pd.read_excel(
        'eval_data/annotations/Annotator-2-3/global_rsquare.xlsx', header=[0, 1, 2], index_col=0)

    # reductions = df_an2.columns.get_level_values(0).unique()
    # combined_red = sorted([c for c in reductions if 'combined' in c])

    # combined_red_minmax = sorted([c for c in combined_red if 'minmax' in c])
    # combined_red_zscore = sorted([c for c in combined_red if 'zscore' in c])

    # combined_red_euclidean = sorted([c for c in combined_red if 'euclidean' in c])

    # tonal_red =  sorted([c for c in reductions if 'tonal' in c])

    # ann = df_an3.loc[:, (combined_red_euclidean, slice(None), "statistic")] # type: ignore

    # new_df = pd.DataFrame(columns=['0.25', '0.5', '0.75'], index=ann.index)
    # for i in new_df.index:
    #     for j in new_df.columns:
    #         vals = list(ann.loc[i, (slice(None), j, 'statistic')].unstack().unstack().to_dict().values())[0]
    #         print(i, j, sorted(list(vals.items()), reverse=True))
    #         new_df[j][i] = sorted(list(vals.items()), reverse=True)[0][0]

    # print(new_df)#

    reds_to = ['original', 'tonal_euclidean', 'intervallic', 'metrical',
               'durational', 'combined_with_duration_euclidean_zscore']
    algos = {'cardinality_score': 'CS', 'correlation_distance': 'CD', 'city_block_distance': 'CBD',
             'euclidean_distance': 'ED', 'local_alignment_score': 'LA', 'siam_score_all': 'SIAM'}

    df_an3.rename(columns={'Unnamed: 1_level_1': '1.0',
                  'Unnamed: 2_level_1': '1.0'}, inplace=True)
    df_an3.rename(index=algos, inplace=True)
    pd.set_option('display.precision', 3)
    # df_an2.loc[:, (reds_to, slice(None), 'p-value')].stack().unstack(1).droplevel(2, axis=1)[reds_to].reindex(index=df_an2.index,columns=['1.0', '0.75', '0.5', '0.25'], level=1).apply(lambda x: x < 0.001).to_latex('ann2-r2-sign-it.tex', decimal='.', float_format="{:.3f}".format,)
    # df_an3.loc[:, (reds_to, slice(None), 'p-value')].stack().unstack(1).droplevel(2, axis=1)[reds_to].reindex(index=df_an2.index,columns=['1.0', '0.75', '0.5', '0.25'], level=1).apply(lambda x: x < 0.001).to_latex('ann3-r2-sign-it.tex', decimal='.', float_format="{:.3f}".format,)
    # df_an23.loc[:, (reds_to, slice(None), 'p-value')].stack().unstack(1).droplevel(2, axis=1)[reds_to].reindex(index=df_an2.index,columns=['1.0', '0.75', '0.5', '0.25'], level=1).apply(lambda x: x < 0.001).to_latex('ann23-r2-sign-it.tex', decimal='.', float_format="{:.3f}".format,)

    print(df_an3.loc[list(algos.values()), (reds_to, slice(None), 'statistic')].droplevel(2, axis=1)['original'].reindex( # type: ignore
        index=list(algos.values()), columns=['1.0', '0.75', '0.5', '0.25'], level=1))  # .apply(lambda x: x < .001))

def test_features_for_reduction(song='eval_data/binary/parsed/PT-1998-XX-DM-010-v1.json'):
    """Test features for reduction"""

    from fractions import Fraction
    from src.reduction import get_tonal_distance, Reduction

    features = json.load(open(song, 'r'))
    # print('PITCH: ', [(i, p) for i, p in zip(features['features']['phrase_ix'], features['features']['midipitch'])])

    print('BS: ', [bs for i, bs in zip(features['features']['phrase_ix'], features['features']['beatstrength']) if i == 1 or i == 2])
    print('DUR: ', [float(Fraction(dur)) for i, dur in zip(features['features']['phrase_ix'], features['features']['duration']) if i == 1 or i == 2])
    print('INT: ', [ci for i, ci in zip(features['features']['phrase_ix'], features['features']['chromaticinterval']) if i == 1 or i == 2])

    pitch_distances_euc = get_tonal_distance(
            (features['features']['midipitch'], features['features']['duration']), distance='euclidean')
    print('TONAL (EUC): ', [round(pd, 2) for i, pd in zip(features['features']['phrase_ix'], pitch_distances_euc) if i == 1 or i == 2])

    _, _, _, combined = Reduction().get_combined(features, 'euclidean', 'zscore', use_duration=True)
    print('COMBINED (EUC, ZSCORE, DUR): ', [round(pd[1], 2) for i, pd in zip(features['features']['phrase_ix'], combined) if i == 1 or i == 2])

if __name__ == '__main__':

    import sys

    try:
        if len(sys.argv) < 2 or sys.argv[1] == 'help':
            print('Possible Commands:')
            print('- parse <binary|ternary>')
            print('- reduce <binary|ternary>')
            print('- similarity_intra <binary|ternary>')
            print('- similarity_inter')
            print('- similarity_pairs')
            print('- evaluate')
            print('- graphs')
            print('- test')
            print('- violin_plots_annotator')
        if sys.argv[1] == 'parse':
            parse_files(sys.argv[2])
        elif sys.argv[1] == 'reduce':
            reduce_all_songs(sys.argv[2])
        elif sys.argv[1] == 'similarity_intra':
            similarity_intra_category(sys.argv[2])
        elif sys.argv[1] == 'similarity_inter':
            similarity_inter_category()
        elif sys.argv[1] == 'similarity_pairs':
            similarity_pairs()
        elif sys.argv[1] == 'evaluate':
            evaluate()
        elif sys.argv[1] == 'graphs':
            general_graphs_combined()
        elif sys.argv[1] == 'test':
            test_features_for_reduction()
        elif sys.argv[1] == 'violin_plots_annotator':
            violin_plots_annotator()
    except Exception as e:
        print(e)
