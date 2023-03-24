# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 11:47:38 2023

@author: Nádia Carvalho
"""

import os
import glob
import pandas as pd
import numpy as np

from scipy.stats import pearsonr, linregress


from ..similarity import SimilarityCalculator


def rsquared(x, y):
    """
    Calculates the R^2 value of two lists

    @param x: list of values
    @param y: list of values

    @return: (R^2 value, p-value)
    """
    _, _, r_value, p_value, _ = linregress(x, y)
    return (r_value**2, p_value)


def get_song_df(song, df):
    """
    Gets the similarity values for a song from a similarity dataframe

    @param song: tuple of song names
    @param df: similarity dataframe

    @return: similarity values for the song
    """
    try:
        return df.loc[song[0], song[1]]
    except KeyError:
        return df.loc[song[1], song[0]]


class AnnotationComparer:

    def __init__(self) -> None:
        """
        Constructor for AnnotationComparer
        """
        pass

    def compare_annotations(self, annotator_scores, name='annotator 1'):
        """
        Compares an annotator's scores with every algorithm's scores
        """
        os.makedirs(
            f'eval_data/annotations/{name.replace(" ", "-")}', exist_ok=True)

        algorithms = SimilarityCalculator().get_algorithms()
        reductions = {
            'first_level': ['metrical', 'intervallic', 'tonal cosine', 'tonal euclidean', 'combined cosine minmax', 'combined cosine zscore', 'combined euclidean minmax', 'combined euclidean zscore'],
            'second_level': ['0.0', '0.1', '0.25', '0.5', '0.75', '1.0'],
            'third_level': ['statistic', 'p-value']
        }

        reduction_cols = pd.MultiIndex.from_product(
            reductions.values()).to_list()
        reduction_cols = pd.MultiIndex.from_tuples(
            [('original', '', 'statistic'), ('original', '', 'p-value')] + reduction_cols)

        anotes_all = {}
        sims_all = {}

        for category in annotator_scores.index.levels[0]:
            print(category)

            songs = [tuple(x.split('_')) for x in list(
                annotator_scores.loc[category, :, 'Global'].index)]
            pearson_comparison_df = pd.DataFrame(
                index=algorithms, columns=reduction_cols)
            rsquared_comparison_df = pd.DataFrame(
                index=algorithms, columns=reduction_cols)

            all_sims = glob.glob(
                f'eval_data/{category.lower()}/similarity/**/*.xlsx', recursive=True)
            for sim in all_sims:
                alg = sim.split(os.sep)[-3]
                cat = ' '.join(sim.split(os.sep)[-1].split('_')[:-1])
                deg = '.'.join(sim.split(os.sep)
                               [-1].split('_')[-1].split('.')[:-1])

                df = pd.read_excel(sim, index_col=0, header=0)

                annote_values = [annotator_scores.loc[category, '_'.join(
                    song), 'Global'].iloc[0] for song in songs]
                sim_values = [get_song_df(song, df) for song in songs]

                if (alg, cat, deg) not in anotes_all:
                    anotes_all[(alg, cat, deg)] = annote_values
                    sims_all[(alg, cat, deg)] = sim_values
                else:
                    anotes_all[(alg, cat, deg)].extend(annote_values)
                    sims_all[(alg, cat, deg)].extend(sim_values)

                if any(np.isnan(x) for x in annote_values) or any(np.isnan(x) for x in sim_values):
                    continue

                pearson = pearsonr(annote_values, sim_values)
                rsq = rsquared(annote_values, sim_values)

                pearson_comparison_df.loc[alg,
                                          (cat, deg, 'statistic')] = pearson[0]
                pearson_comparison_df.loc[alg,
                                          (cat, deg, 'p-value')] = pearson[1]
                rsquared_comparison_df.loc[alg,
                                           (cat, deg, 'statistic')] = rsq[0]
                rsquared_comparison_df.loc[alg, (cat, deg, 'p-value')] = rsq[1]

            pearson_comparison_df.to_excel(
                f'eval_data/annotations/{name}/{category.lower()}_pearson.xlsx')
            rsquared_comparison_df.to_excel(
                f'eval_data/annotations/{name}/{category.lower()}_rsquare.xlsx')

        pearson_comparison_df = pd.DataFrame(
            index=algorithms, columns=reduction_cols)
        rsquared_comparison_df = pd.DataFrame(
            index=algorithms, columns=reduction_cols)

        for (alg, cat, deg) in anotes_all:

            if any(np.isnan(x) for x in anotes_all[(alg, cat, deg)]) or any(np.isnan(x) for x in sims_all[(alg, cat, deg)]):
                continue

            pearson = pearsonr(
                anotes_all[(alg, cat, deg)], sims_all[(alg, cat, deg)])
            rsq = rsquared(anotes_all[(alg, cat, deg)],
                           sims_all[(alg, cat, deg)])

            pearson_comparison_df.loc[alg,
                                      (cat, deg, 'statistic')] = pearson[0]
            pearson_comparison_df.loc[alg, (cat, deg, 'p-value')] = pearson[1]
            rsquared_comparison_df.loc[alg, (cat, deg, 'statistic')] = rsq[0]
            rsquared_comparison_df.loc[alg, (cat, deg, 'p-value')] = rsq[1]

        pearson_comparison_df.to_excel(
            f'eval_data/annotations/{name}/pearson.xlsx')
        rsquared_comparison_df.to_excel(
            f'eval_data/annotations/{name}/rsquare.xlsx')
