# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 11:47:38 2023

@author: Nádia Carvalho
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

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

    def create_violin_plots_multiple(self, annotator_scores, features=['Global', 'Rhythm']):
        """Creates violin plots of all annotators' scores by type of song (binary, ternary, etc.) for multiple features"""
        if len(features) <= 1:
            print('Please select more than one feature')
            return

        fig, ax = plt.subplots(2, 1)

        for ann in annotator_scores.index:
            annotator = annotator_scores.iloc[ann-1]
            print('Making plot for annotator', ann)

            df = pd.DataFrame(
                columns=['pair_songs', 'Feature', 'Category', 'Score'])
            df['pair_songs'] = annotator.index.get_level_values(1)
            df['Feature'] = annotator.index.get_level_values(2)
            df['Category'] = annotator.index.get_level_values(
                0).str.capitalize()
            df['Score'] = annotator.values

            sns.set(style="darkgrid")

            sns.violinplot(data=df.loc[df['Feature'].isin(features)], x='Feature',
                            y='Score', hue='Category', palette="Pastel1", ax=ax[ann-1], scale='count', inner='quartile', cut=0)
            ax[ann-1].get_legend().remove()
            ax[ann-1].set_title(f'Annotator {ann}')

        handles, labels = plt.gca().get_legend_handles_labels()
        fig.legend(handles, labels, loc='lower center', ncol=3, title='Category',
                    fancybox=True, shadow=True)
        plt.subplots_adjust(top=0.9, bottom=0.2, hspace=0.7)

        return fig


    def create_violin_plots_single(self, annotator_scores, feature='Global', palette='Pastel1'):

        fig, ax = plt.subplots(1, 1)

        #print(annotator_scores)

        df = pd.DataFrame(columns=['pair_songs', 'Feature', 'Category', 'Score Ann 1', 'Score Ann 2'])
        df['pair_songs'] = annotator_scores.columns.get_level_values(1)
        df['Feature'] = annotator_scores.columns.get_level_values(2)
        df['Category'] = annotator_scores.columns.get_level_values(0).str.capitalize().str.replace('Intercategories', 'Mixed')
        df['Score Ann 1'] = annotator_scores.iloc[0].values
        df['Score Ann 2'] = annotator_scores.iloc[1].values
        df = df.loc[df['Feature'] == feature].drop(columns=['Feature', 'pair_songs'])

        new_df = pd.DataFrame(columns=['Category', 'Annotator', 'Score'])
        new_df['Annotator'] = ['Annotator 1'] * len(df) + ['Annotator 2'] * len(df)
        new_df['Category'] = df['Category'].values.tolist() * 2
        new_df['Score'] = df['Score Ann 1'].values.tolist() + df['Score Ann 2'].values.tolist()

        sns.set(style="darkgrid")

        sns.violinplot(data=new_df, x='Annotator',
                           y='Score', hue='Category', palette=palette, ax=ax, scale='count')#, inner='quartile', cut=0)

        plt.legend(loc='upper center', ncol=3, title='', fancybox=True, shadow=True, bbox_to_anchor=(0.5, 1.12))
        plt.xlabel('')
        plt.savefig(f'eval_data/annotations/annotator_1_vs_2_{feature}.jpg', dpi=300, bbox_inches='tight')

        return fig

    def create_violin_plots(self, annotator_scores, features=['Global'], palette='Pastel1'):
        """Creates violin plots of an annotator's scores by type of song (binary, ternary, etc.)"""
        if len(features) > 1:
            fig = self.create_violin_plots_multiple(annotator_scores, features)
        else:
            fig = self.create_violin_plots_single(annotator_scores, features[0], palette)

        plt.show()

    def create_comparison_graphs(self, path, name='annotator 1'):
        """
        Creates graphs comparing an annotator's scores with every algorithm's scores for reduction levels
        """
        df = pd.read_excel(path, index_col=0, header=[0, 1, 2])
        os.makedirs(
            path[:-5] + '_graphs', exist_ok=True)

        original_red = df['original'].loc[:,
                                          (slice(None), "statistic")].T  # type: ignore

        for reduction in df.columns.levels[0]:  # type: ignore
            if reduction != 'original':
                to_plot = df[reduction].loc[:, (slice(None), "statistic")].T
                to_plot.index = to_plot.index.droplevel(1)

                to_plot.loc[(1.0, to_plot.columns)
                            ] = original_red.unstack().values
                to_plot.plot(title=f'{reduction} reduction', figsize=(15, 10))
                plt.xlabel('Reduction level')
                plt.ylabel(
                    f'{"Pearson" if "pearson" in path else "R^2"} correlation')

                plt.savefig(
                    f'{path[:-5]}_graphs/{reduction.replace(" ", "-")}.jpg')
                plt.close()

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
                if 'distance' in alg:
                    sim_values = [1 - x for x in sim_values]

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

            pearson_comparison_df.loc[:, ('original', '', 'statistic')
                                      ] = pearson_comparison_df.loc[:, ('metrical', '0.0', 'statistic')]
            pearson_comparison_df.loc[:, ('original', '', 'p-value')
                                      ] = pearson_comparison_df.loc[:, ('metrical', '0.0', 'p-value')]
            rsquared_comparison_df.loc[:, ('original', '', 'statistic')
                                       ] = rsquared_comparison_df.loc[:, ('metrical', '0.0', 'statistic')]
            rsquared_comparison_df.loc[:, ('original', '', 'p-value')
                                       ] = rsquared_comparison_df.loc[:, ('metrical', '0.0', 'p-value')]

            pearson_comparison_df.dropna(axis=1, how='all', inplace=True)
            rsquared_comparison_df.dropna(axis=1, how='all', inplace=True)

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

        pearson_comparison_df.loc[:, ('original', '', 'statistic')] = pearson_comparison_df.loc[:, (
            'metrical', '0.0', 'statistic')]  # type: ignore
        pearson_comparison_df.loc[:, ('original', '', 'p-value')] = pearson_comparison_df.loc[:,
                                                                                              ('metrical', '0.0', 'p-value')]  # type: ignore
        rsquared_comparison_df.loc[:, ('original', '', 'statistic')] = rsquared_comparison_df.loc[:, (
            'metrical', '0.0', 'statistic')]  # type: ignore
        rsquared_comparison_df.loc[:, ('original', '', 'p-value')] = rsquared_comparison_df.loc[:,
                                                                                                ('metrical', '0.0', 'p-value')]  # type: ignore

        pearson_comparison_df.dropna(axis=1, how='all', inplace=True)
        rsquared_comparison_df.dropna(axis=1, how='all', inplace=True)

        pearson_comparison_df.to_excel(
            f'eval_data/annotations/{name}/pearson.xlsx')
        rsquared_comparison_df.to_excel(
            f'eval_data/annotations/{name}/rsquare.xlsx')

    def compare_annotations_joined(self, annotator_scores, similarity_scores, name='annotator 1'):
        """Compare annotations, using an excel with all songs comparisons."""

        os.makedirs(
            f'eval_data/annotations/{name.replace(" ", "-")}', exist_ok=True)

        new_index = list(similarity_scores.columns)
        new_cols = pd.MultiIndex.from_tuples(
            [('original', '', 'statistic'), ('original', '', 'p-value')] + pd.MultiIndex.from_product(
                [set(['_'.join(red.split('_')[:-1]) for red in similarity_scores.index.levels[2]]),
                    ['0.25', '0.5', '0.75'], ['statistic', 'p-value']]).to_list())

        all_annote_values = {}

        for category in annotator_scores.index.levels[0]:

            song_pairs = [tuple(x.split('_')) for x in list(
                annotator_scores.loc[category, :, 'Global'].index)]

            pearson_comparison_df = pd.DataFrame(
                index=new_index, columns=new_cols)
            rsquared_comparison_df = pd.DataFrame(
                index=new_index, columns=new_cols)

            category_sim = similarity_scores.loc[category].unstack()
            notes = [annotator_scores.loc[(category, f'{song1}_{song2}', 'Global')].iloc[0] for (
                song1, song2) in song_pairs]

            for (algo, red) in category_sim.columns.to_list():
                deg = red.split('_')[-1]
                red_name = '_'.join(red.split('_')[:-1])
                if deg == '1.0':
                    if red == 'metrical_1.0':
                        red_name = 'original'
                    else:
                        continue

                sim_values = category_sim[(algo, red)].values
                notes_temp = notes
                if 'distance' in algo:
                    sim_values = max(sim_values) - sim_values

                if any(np.isnan(x) for x in notes) or any(np.isnan(x) for x in sim_values):
                    n_n_nan = [i for i, v in enumerate(
                        notes) if not np.isnan(v)]
                    s_n_nan = [i for i, v in enumerate(
                        sim_values) if not np.isnan(v)]
                    index_nan = list(set(n_n_nan) & set(s_n_nan))

                    notes_temp = np.take(notes_temp, index_nan)
                    sim_values = np.take(sim_values, index_nan)

                if len(notes_temp) == 0 or len(sim_values) == 0:
                    continue

                if red_name == 'original':
                    deg = ''

                if (algo, red_name, deg) not in all_annote_values:
                    all_annote_values[(algo, red_name, deg)] = [
                        notes_temp, sim_values]
                else:
                    all_annote_values[(algo, red_name, deg)][0] = np.concatenate(
                        (all_annote_values[(algo, red_name, deg)][0], notes_temp))
                    all_annote_values[(algo, red_name, deg)][1] = np.concatenate(
                        (all_annote_values[(algo, red_name, deg)][1], sim_values))

                pearson = pearsonr(notes_temp, sim_values)
                pearson_comparison_df.loc[algo,
                                          (red_name, deg, 'statistic')] = pearson[0]
                pearson_comparison_df.loc[algo,
                                          (red_name, deg, 'p-value')] = pearson[1]

                rsq = rsquared(notes_temp, sim_values)
                rsquared_comparison_df.loc[algo,
                                           (red_name, deg, 'statistic')] = rsq[0]
                rsquared_comparison_df.loc[algo,
                                           (red_name, deg, 'p-value')] = rsq[1]

            pearson_comparison_df.dropna(axis=1, how='all', inplace=True)
            rsquared_comparison_df.dropna(axis=1, how='all', inplace=True)
            pearson_comparison_df.to_excel(
                f'eval_data/annotations/{name}/{category.lower()}_pearson.xlsx')
            rsquared_comparison_df.to_excel(
                f'eval_data/annotations/{name}/{category.lower()}_rsquare.xlsx')

        pearson_global_df = pd.DataFrame(
            index=new_index, columns=new_cols)
        rsquared_global_df = pd.DataFrame(
            index=new_index, columns=new_cols)

        for (alg, cat, deg) in all_annote_values:
            notes = all_annote_values[(alg, cat, deg)][0]
            sim_values = all_annote_values[(alg, cat, deg)][1]

            pearson = pearsonr(notes.flatten(), sim_values.flatten())
            pearson_global_df.loc[alg,
                                  (cat, deg, 'statistic')] = pearson[0]
            pearson_global_df.loc[alg,
                                  (cat, deg, 'p-value')] = pearson[1]

            rsq = rsquared(notes.flatten(), sim_values.flatten())
            rsquared_global_df.loc[alg,
                                   (cat, deg, 'statistic')] = rsq[0]
            rsquared_global_df.loc[alg, (cat, deg, 'p-value')] = rsq[1]

        pearson_global_df.to_excel(
            f'eval_data/annotations/{name}/global_pearson.xlsx')
        rsquared_global_df.to_excel(
            f'eval_data/annotations/{name}/global_rsquare.xlsx')
