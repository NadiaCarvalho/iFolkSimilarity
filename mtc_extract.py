import copy
import os
import time
from csv import DictReader

import matplotlib.pyplot as plt
import music21 as m21
import numpy as np
import pandas as pd
import progressbar as pb
import sklearn.metrics as skm
from MTCFeatures import MTCFeatureLoader

from MelodicOccurrences.evaluate import prepare_position_evaluation
from MelodicOccurrences.find_matches import (SIAM, distance_measures,
                                             local_aligner, matches_in_corpus)
from MelodicOccurrences.music_representations import filter_phrases, adjust_pitches
from src.reduction import Reduction

# plt.rcParams.update({
#     "text.usetex": True,
#     "font.family": "Helvetica"
# })


def get_features(song, m21_song):
    return {
        'midipitch': song['features']['midipitch'],
        'chromaticinterval': song['features']['chromaticinterval'],
        'duration': song['features']['duration'],
        'offsets': [n.offset for n in m21_song.flat.stripTies().notes],
        'ioi': song['features']['IOI'],
        'ioiR': song['features']['IOR'],
        'phrase_id': song['features']['phrase_ix'],
        'scale_degree': song['features']['scaledegree'],
        'metric_weight': song['features']['beatstrength'] if len(m21_song.recurse().getElementsByClass('Measure')) > 1 else [np.nan for _ in song['features']['midipitch']],
        'beatstrength': song['features']['beatstrength'] if len(m21_song.recurse().getElementsByClass('Measure')) > 1 else [n.beatStrength for n in m21_song.flat.stripTies().notes],
        'note_index': [i for i, _ in enumerate(song['features']['midipitch'])],
        'timesignature': song['features']['timesignature'],
        'phrasePosition': song['features']['phrasepos'],
    }


def get_note_features(feature_dict, i):
    """
    takes a dictionary with features for a melody
    """
    to_ret = {}

    for key, value in feature_dict.items():
        if key == 'midipitch':
            key = 'pitch'
        elif key == 'chromaticinterval':
            key = 'pitch_interval'
        elif key == 'beatstrength':
            key = 'beat_strength'
        elif key == 'offsets':
            key = 'onset'

        to_ret[key] = value[i]

    return to_ret


def extract_melodies_from_corpus(corpus_path, meta_dict=None, reduction='', algorithm='SIAM'):
    """
    takes a corpus path,
    and a dictionary with metadata about the corpus
    returns a dictionary with per melody:
    - tune family id
    - filename
    - per note:
        - midi note number
        - pitch interval to preceding note
        - onset
        - inter-onset interval
        - ioi ratio with preceding note
        - metric weight of note
        - in which phrase the note occurs
        - phrase position of note
        - scale degree of note
        - note index
    """
    fl = MTCFeatureLoader(corpus_path)

    reducer = Reduction()

    reduction = reduction.split('_')

    normalization = ''
    distance = ''
    if reduction[0] == 'metrical' or reduction[0] == 'intervallic':
        degree = float(reduction[1])
    elif reduction[0] == 'tonal':
        distance = reduction[1]
        degree = float(reduction[2])
    else:
        distance = reduction[1]
        normalization = reduction[2]
        degree = float(reduction[3])

    if meta_dict is None:
        songs = list(fl.applyFilter('labeled'))
    else:
        songs = list(fl.applyFilter(('inNLBIDs', meta_dict)))

    # loop through phrases per song, make dict
    mel_dict = []

    with pb.ProgressBar(max_value=len(songs)) as bar:
        for j, song in enumerate(songs):

            m21_song = m21.converter.parse(
                f'eval_data/MTCFeatures/krn/{song["id"]}.krn')

            symbols = get_features(song, m21_song)

            red = reducer.reduce(
                {'features': symbols}, reduction_type=reduction[0], degree=degree, distance=distance, normalization=normalization)
            if len(red) == 0:
                red = list(range(len(symbols['midipitch'])))

            mel_dict.append({
                'id': song['id'],
                'tunefamily_id': song['tunefamily'],
                'filename': f'eval_data/MTCFeatures/krn/{song["id"]}.krn',
                'symbols': [get_note_features(symbols, i) for i, _ in enumerate(symbols['midipitch']) if i in red]
            })

            bar.update(j + 1)
            time.sleep(0.001)

    np.save(
        f'eval_data/MTCFeatures/features/mtc_{"_".join(reduction)}.npy', mel_dict)


def similarities(reduction, algorithm='SIAM'):

    mel_dict = np.load(
        f'eval_data/MTCFeatures/features/mtc_{reduction}.npy', allow_pickle=True)

    mel_dict = adjust_pitches(mel_dict)
    segment_list = filter_phrases(mel_dict)

    if algorithm == 'SIAM':
        alg_result = matches_in_corpus(
            mel_dict, segment_list, measure=SIAM)  # type: ignore
    elif algorithm == 'LA':
        alg_result = matches_in_corpus(
            mel_dict, segment_list, measure=local_aligner, scaling=False, music_representation='scale_degree')
    else:
        alg_result = matches_in_corpus(
            mel_dict, segment_list, measure=distance_measures)  # type: ignore

    os.makedirs(f'eval_data/MTCFeatures/simil/{algorithm}', exist_ok=True)
    np.save(
        f'eval_data/MTCFeatures/simil/{algorithm}/mtc_{reduction}.npy', alg_result)


def eval(reduction, algorithm='SIAM', high_low=1):

    from csv import DictReader

    from MelodicOccurrences.evaluate import prepare_position_evaluation

    mel_dict = np.load(
        f'eval_data/MTCFeatures/features/mtc_{reduction}.npy', allow_pickle=True)

    result_list = np.load(
        f'eval_data/MTCFeatures/simil/{algorithm}/mtc_{reduction}.npy', allow_pickle=True)

    label_dict = list(DictReader(
        open('eval_data/MTCFeatures/MTC-ANN-phrase-similarity.csv', 'r')))
    for label in label_dict:
        label['tunefamily_id'] = next(
            item['tunefamily_id'] for item in mel_dict if item["id"] == label["songid"])
        label['filename'] = f'eval_data/MTCFeatures/krn/{label["songid"]}.krn'

    return prepare_position_evaluation(
        result_list, mel_dict, label_dict, sign=high_low)


def get_best_phi_scores(algorithm, df, thresholds):
    phis = {}

    tr_maj = df['majority'].to_numpy()

    with pb.ProgressBar(max_value=len(thresholds)) as bar:
        for i, tr in enumerate(thresholds):
            if algorithm in ['SIAM', 'LA']:
                tr_algo = df[f'{algorithm.lower()}'].apply(
                    lambda x: 1 if x > tr else 0).to_numpy()
            else:
                tr_algo = df[f'{algorithm.lower()}'].apply(
                    lambda x: 1 if x < tr else 0).to_numpy()

            if any(x == 1 for x in tr_algo):
                phis[tr] = skm.matthews_corrcoef(tr_maj, tr_algo)

            bar.update(i)
            time.sleep(0.001)

    max_phi = max(phis.keys(), key=(lambda k: phis[k]))

    if algorithm in ['SIAM', 'LA']:
        tr_best_algo = df[f'{algorithm.lower()}'].apply(
            lambda x: 1 if x > max_phi else 0).to_numpy()
    else:
        tr_best_algo = df[f'{algorithm.lower()}'].apply(
            lambda x: 1 if x < max_phi else 0).to_numpy()

    return [phis[max_phi],
            skm.recall_score(tr_maj, tr_best_algo),  # SEN
            skm.recall_score(tr_maj, tr_best_algo, pos_label=0),  # SPC
            skm.precision_score(tr_maj, tr_best_algo),  # PPV
            skm.precision_score(tr_maj, tr_best_algo, pos_label=0)  # NPV
            ]


def append_info(item, query):
    for info in ['match_filename', 'query_filename', 'query_segment_id', 'tunefamily_id']:
        item[info] = query[info]
    return item


def extract_scores_and_plot(ax, scores, reduction, algorithm):

    results = eval(reduction, algorithm=algorithm, high_low=-
                   1 if algorithm in ['LA', 'SIAM'] else 1)

    struct = [append_info(item, query) for query in results for item in query['position_eval']
              if query['match_filename'] != query['query_filename']]
    df = pd.DataFrame(struct, columns=struct[0].keys())

    fpr, tpr, thresholds = skm.roc_curve(
        df['majority'].to_numpy(), df[f'{algorithm.lower()}'].to_numpy(), pos_label=1, drop_intermediate=True)
    scores.loc[reduction, 'AUC'] = skm.auc(fpr, tpr)  # type: ignore
    scores.loc[reduction, ['\\phi', 'SEN', 'SPC', 'PPV', 'NPV']
               ] = get_best_phi_scores(algorithm, df, thresholds)

    ax.plot(fpr, tpr, label=reduction.split('_')[-1])


def reductions_main(algorithm='LA'):
    reductions_groups = ['metrical', 'intervallic']
    reductions_groups.extend(f'tonal_{d}' for d in ['euclidean', 'cosine'])
    reductions_groups.extend([f'combined_{d}_{n}' for d in [
                             'euclidean', 'cosine'] for n in ['minmax', 'zscore']])

    fold = f'eval_data/MTCFeatures/annotations/results/{algorithm}.AP.no_scaling'
    os.makedirs(fold, exist_ok=True)

    for reduction in reductions_groups:
        print()
        print(reduction)

        if reduction == 'metrical':
            reductions = [f'{reduction}_{i}' for i in [
                d/100 for d in range(0, 100, 25)]]
        else:
            reductions = [f'{reduction}_{i}' for i in [
                1.0, 0.75, 0.5, 0.25, 0.1]]

        fig, ax = plt.subplots()
        scores = pd.DataFrame(index=reductions, columns=[
            'AUC', "\\phi", 'SEN', 'SPC', 'PPV', 'NPV'])

        for red in reductions:
            print()
            print(red)
            extract_melodies_from_corpus(
                'eval_data/MTCFeatures/MTC-ANN-2.0.1_sequences-1.1.jsonl.gz', reduction=red, algorithm=algorithm)
            print()
            similarities(red, algorithm=algorithm)
            print()
            extract_scores_and_plot(ax, scores, red, algorithm)
            print(f'ended {red} extraction')

        scores.to_csv(
            f'{fold}/{reduction}.csv')

        plt.title(f'{reduction.capitalize()} Reduction')
        plt.legend()
        plt.savefig(
            f'{fold}/{reduction}_ROC.png')
        plt.close()


def test_original(algorithm='LA',):

    mel_dict = np.load('eval_data/MTCFeatures/melodies.pkl', allow_pickle=True)
    segment_list = np.load(
        'eval_data/MTCFeatures/phrases.pkl', allow_pickle=True)

    # from MelodicOccurrences.music_representations import *

    # mel_dict = adjust_meter(mel_dict)
    # mel_dict = adjust_pitches(mel_dict)

    # print(mel_dict[0])
    # exit()

    high_low = 1
    if algorithm == 'LA' or algorithm == 'SIAM':
        high_low = -1

    result_list = matches_in_corpus(
        mel_dict, segment_list, measure=local_aligner, music_representation='scale_degree')  # type: ignore

    label_dict = list(DictReader(
        open('eval_data/MTCFeatures/MTC-ANN-phrase-similarity.csv', 'r')))
    for label in label_dict:
        label['tunefamily_id'] = next(  # filename == id
            item['tunefamily_id'] for item in mel_dict if item["filename"] == label["songid"])
        #
        if os.sep in result_list[0].get('query_filename'):
            label['filename'] = f'eval_data/MTCFeatures/krn/{label["songid"]}.krn'
        else:
            label['filename'] = label['songid']
            label['phrase_id'] = int(label['phrase_id'])

    results = prepare_position_evaluation(
        result_list, mel_dict, label_dict, sign=high_low)

    struct = [append_info(item, query) for query in results for item in query['position_eval']
              if query['match_filename'] != query['query_filename']]
    df = pd.DataFrame(struct, columns=struct[0].keys())

    scores = pd.DataFrame(columns=['AUC', "\\phi", 'SEN', 'SPC', 'PPV', 'NPV'])

    reduction = 'original'
    fpr, tpr, thresholds = skm.roc_curve(
        df['majority'].to_numpy(), df[f'{algorithm.lower()}'].to_numpy(), pos_label=1)
    scores.loc[reduction, 'AUC'] = skm.auc(fpr, tpr)  # type: ignore
    scores_thr = get_best_phi_scores(algorithm, df, thresholds)
    scores.loc[reduction, ['\\phi', 'SEN', 'SPC', 'PPV', 'NPV']] = [scores_thr[max(scores_thr.keys(), key=(  # type: ignore
        lambda k: scores_thr[k]['\\phi']))][key] for key in ['\\phi', 'SEN', 'SPC', 'PPV', 'NPV']]

    print(scores)
    # ax.plot(fpr, tpr, label=reduction.split('_')[-1])


if __name__ == '__main__':

    reductions_main(algorithm='LA')
