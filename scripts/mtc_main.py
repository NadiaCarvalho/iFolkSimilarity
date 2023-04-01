# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:20:12 2023

@author: Nádia Carvalho
"""

from collections.abc import MutableMapping
import json
import os
import sys
import time

import music21 as m21
import pandas as pd
import progressbar as pb
from MTCFeatures import MTCFeatureLoader

from src.reduction import Reduction


def reduce_features(song_features, reduction, cat, distance=None, normalization=None, name=None):
    cat_degrees = [1.0, 0.75, 0.5, 0.25, 0.1]
    if cat == 'metrical':
        cat_degrees = [d/100 for d in range(0, 100, 25)]

    return {
        deg: reduction.reduce(
            song_features, reduction_type=cat, degree=deg, distance=distance, normalization=normalization, graphs=name)
        for deg in cat_degrees
    }


def reduct_MTCs(fl, families):
    """
    Reduces all MTCs in the MTCFeatureLoader and saves them in a json file per family of songs.
    """

    os.makedirs(f'eval_data/MTCFeatures/reductions', exist_ok=True)
    reduction = Reduction()

    for fam in families:
        print(fam)

        all_indexes = {}

        for song in fl.applyFilter(('inTuneFamilies', fam)):
            song_id = song['id']
            all_indexes[song_id] = {}

            for cat in ['metrical', 'intervallic']:
                all_indexes[song_id][cat] = reduce_features(
                    song, reduction=reduction, cat=cat)

            for cat in ['tonal', 'combined']:
                all_indexes[song_id][cat] = {}
                for distance in ['cosine', 'euclidean']:
                    if cat == 'tonal':
                        all_indexes[song_id][cat][distance] = reduce_features(
                            song, reduction=reduction, cat=cat, distance=distance)
                    else:
                        all_indexes[song_id][cat][distance] = {}
                        for norm in ['minmax', 'zscore']:
                            all_indexes[song_id][cat][distance][norm] = reduce_features(
                                song, reduction=reduction, cat=cat, distance=distance, normalization=norm)

        with open(f'eval_data/MTCFeatures/reductions/{fam}.json', 'w') as f:
            json.dump(all_indexes, f)


def song_show(fl, reduction, fam, reducts, song):
    """
    Prints all reductions of a song.
    """
    song_feats = list(fl.applyFilter(('inNLBIDs', [song])))[0]

    path = f'eval_data/MTCFeatures/reductions/{fam}/{song}'
    os.makedirs(path, exist_ok=True)

    for cat in reducts[song]:
        all_reduction_score = m21.stream.Score()  # type: ignore
        if cat == 'metrical' or cat == 'intervallic':
            all_reduction_score.metadata = m21.metadata.Metadata(
                title=f'{cat.capitalize()} Reduc. \n song {song}')
            for deg in reducts[song][cat]:
                reduction_score = reduction.show_reduced_song(
                    song_feats, reducts[song][cat][deg],
                    name=f'Degree: {f"{str(int(float(deg)*100))}%" if cat != "metrical" else f"{str(deg)}"}')
                all_reduction_score.insert(0, reduction_score)
            all_reduction_score.write(
                'musicxml', f'{path}/{song}-{cat}.xml')
        else:
            for distance in reducts[song][cat]:
                for norm in reducts[song][cat][distance]:
                    all_reduction_score.metadata = m21.metadata.Metadata(
                        title=f'{cat.capitalize()} Reduc. {f"({distance} distance),"} {f" Norm. {norm}," if cat == "combined" else ""} \n song {song}')

                    if cat == 'tonal':
                        indexes = reducts[song][cat][distance]
                    else:
                        indexes = reducts[song][cat][distance][norm]

                    for deg in indexes:
                        reduction_score = reduction.show_reduced_song(
                            song_feats, indexes[deg], name=f'Degree: {f"{str(int(float(deg)*100))}%"}')
                        all_reduction_score.insert(0, reduction_score)
                    all_reduction_score.write(
                        'musicxml', f'{path}/{song}-{cat}-{distance}{f"-{norm}" if cat == "combined" else ""}.xml')


def print_reductions_MTCs(fl, families):
    """
    Prints all reductions of all MTCs in the MTCFeatureLoader.
    """
    from src.reduction import Reduction
    reduction = Reduction()

    for fam in sorted(list(families)):
        reducts = json.load(
            open(f'eval_data/MTCFeatures/reductions/{fam}.json', 'r'))

        print(fam, len(reducts.keys()))

        with pb.ProgressBar(max_value=len(reducts.keys())) as bar:
            for song in sorted(reducts):

                try:
                    song_show(fl, reduction, fam, reducts, song)
                except Exception as e:
                    print('Error parsing song: ' + song)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[  # type: ignore
                        1]
                    print(exc_type, fname, exc_tb.tb_lineno)  # type: ignore
                    print()

                # input('Press enter to continue...')
                bar.update(bar.value + 1)  # type: ignore
                time.sleep(0.001)


def calculate_similarities_MTCs(fl, families):
    """
    Calculates similarities between all MTCs in the MTCFeatureLoader and saves them in a json file per family of songs.
    """
    from src.similarity import SimilarityCalculator
    similarity_calculator = SimilarityCalculator()

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

    for fam in families:
        print(fam)

        reducts = json.load(
            open(f'eval_data/MTCFeatures/reductions/{fam}.json', 'r'))
        fam_reductions = {song: flatten(
            reducts[song]) for song in reducts.keys()}

        fam_songs = list(fam_reductions.keys())
        for algorithm in similarity_calculator.get_algorithms():
            for cat in fam_reductions[fam_songs[0]].keys():
                print('Calculating similarities for category',
                      cat, 'with', algorithm)

                fold = f'eval_data/MTCFeatures/similarity/{fam}/{algorithm}/{cat.split("_")[0]}/'
                os.makedirs(
                    fold, exist_ok=True)

                df = pd.DataFrame(columns=fam_songs, index=fam_songs)

                with pb.ProgressBar(max_value=len(fam_songs)*len(fam_songs)) as bar:
                    for song1 in fam_songs:
                        for song2 in fam_songs:
                            song_features = [seq for seq in fl.applyFilter(
                                ('inNLBIDs', [song1, song2]))]
                            if song1 == song2:
                                song_features = [
                                    song_features[0], song_features[0]]

                            df[song1][song2] = similarity_calculator.similarity_between_two_songs(
                                (song_features[0],
                                 fam_reductions[song1][cat]),
                                (song_features[1],
                                 fam_reductions[song2][cat]),
                                algorithm=algorithm,)

                            bar.update(int(bar.value) + 1)  # type: ignore
                            time.sleep(0.01)

                df.to_excel(f'{fold}/{cat}.xlsx')


if __name__ == '__main__':

    fl = MTCFeatureLoader(
        'eval_data/MTCFeatures/MTC-ANN-2.0.1_sequences-1.1.jsonl.gz')

    families = set([seq['tunefamily']
                   for seq in fl.minClassSizeFilter('tunefamily', 5)])

    families = [
        # 'Daar_ging_een_heer_1', # ERRORS: NLB073743_01, NLB073822_01, NLB076625_01, NLB076632_01
        # 'Daar_reed_een_jonkheer_1',
        # 'Daar_was_laatstmaal_een_ruiter_2',
        # 'Daar_zou_er_een_maagdje_vroeg_opstaan_2',
        # 'Een_lindeboom_stond_in_het_dal_1',
        # 'Een_Soudaan_had_een_dochtertje_1', # ERRORS: NLB076426_01
        # 'En_er_waren_eens_twee_zoeteliefjes',
        # 'Er_reed_er_eens_een_ruiter_1',
        # 'Er_was_een_herderinnetje_1',
        # 'Er_was_een_koopman_rijk_en_machtig',
        # 'Er_was_een_meisje_van_zestien_jaren_1',
        # 'Er_woonde_een_vrouwtje_al_over_het_bos',
        # 'Femmes_voulez_vous_eprouver',
        # 'Heer_Halewijn_2',
        # 'Heer_Halewijn_4',
        # 'Het_vrouwtje_van_Stavoren_1',
        # 'Het_was_laatst_op_een_zomerdag',
        # 'Het_was_op_een_driekoningenavond_1',
        # 'Ik_kwam_laatst_eens_in_de_stad',
        # 'Kom_laat_ons_nu_zo_stil_niet_zijn_1',
        # 'Lieve_schipper_vaar_me_over_1',
        'O_God_ik_leef_in_nood',
        'Soldaat_kwam_uit_de_oorlog',
        'Vaarwel_bruidje_schoon',
        'Wat_zag_ik_daar_van_verre_1',
        'Zolang_de_boom_zal_bloeien_1',
    ]

    sim_df = pd.read_csv('eval_data/MTCFeatures/MTC-ANN-phrase-similarity.csv', sep=',', header=0, index_col=0)
    #print(sim_df)

    # for song in fl.applyFilter(('inTuneFamilies', families[0])):
    #     song_id = song['id']
    #     print(song_id, sim_df.loc[song_id])
    #     print()



    # reduct_MTCs(fl, families)
    # calculate_similarities_MTCs(fl, families)
    # print_reductions_MTCs(fl, families)
