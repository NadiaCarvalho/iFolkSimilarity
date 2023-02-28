"""
Created on Mon Feb 27 09:46:28 2023

@author: Nádia Carvalho
"""
from collections import Counter
from fractions import Fraction

import music21 as m21
import numpy as np
import scipy

from src.TIVlib import TIV as tiv

import matplotlib.pyplot as plt


def normalize(array, alg='minmax'):
    """
    Normalize an np.array

    @param array: vector to be normalized
    @param alg: algorithm to be used ('minmax', 'linalg', 'zscore')

    @return: normalized vector
    """
    if alg == 'minmax':
        return (array-np.min(array))/(np.max(array)-np.min(array))
    elif alg == 'linalg':
        return array/np.linalg.norm(array)
    elif alg == 'zscore':
        return scipy.stats.zscore(array)
    else:
        raise ValueError(f'Algorithm "{alg}" not recognized')


def get_tonal_distance(midi_pitches, distance='euclidean'):
    """
    Get Tonal Distance between notes

    @param midi_pitches: MIDI Pitches
    @param distance: distance function to be used ('euclidean' or 'cosine')

    @return: Tonal Distance between notes
    """
    pitch_class_histogram = [0] * 12
    counter_pitch = Counter(midi_pitches)
    for pitch in counter_pitch:
        pitch_class_histogram[pitch % 12] += counter_pitch[pitch]
    song_tiv = tiv.from_pcp(pitch_class_histogram)

    pitch_tiv = [tiv.from_pcp([1 if pitch % 12 == i else 0 for i in range(
        0, 12, 1)]) for pitch in midi_pitches]
    if distance == 'euclidean':
        return [scipy.spatial.distance.euclidean(song_tiv.vector, p_tiv.vector) for p_tiv in pitch_tiv]
    elif distance == 'cosine':
        return [scipy.spatial.distance.cosine(song_tiv.vector, p_tiv.vector) for p_tiv in pitch_tiv]
    else:
        raise ValueError(
            f'Distance function "{distance}" not recognized')


class Reduction:

    def __init__(self) -> None:
        pass

    def reduce(self, song_features, reduction_type='intervallic', degree=0.75, distance='euclidean'):
        """
        Reduce Song Features according to specific type of reduction

        @param song_features: Song Features
        @param reduce_type: Type of reduction
            - Possible Values:
                - 'tonal' - Tonal Reduction, uses the Tonal Interval Space
                - 'metrical' - Metric Reduction, uses the metric weights of the notes
                - 'intervallic' - Intervallic Reduction, uses the intervals between the notes
                - 'combined' - Combined Reduction, uses a combination of the above
        @param degree: Degree of reduction
        @param distance: Distance function to be used ('euclidean' or 'cosine')

        @return: Reduced Song Features
        """
        if reduction_type == 'tonal':
            return self.reduce_tonal(song_features, degree=degree, distance=distance)
        elif reduction_type == 'metrical':
            return self.reduce_metric(song_features, degree=degree)
        elif reduction_type == 'intervallic':
            return self.reduce_intervallic(song_features, degree=degree)
        elif reduction_type == 'combined':
            return self.reduce_combined(song_features, degree=degree)
        else:
            raise ValueError('Reduction type not recognized')

    def show_reduced_song(self, song_features, indexes_to_retrieve, name=None):
        """
        Show Reduced Song Features

        @param song_features: Song Features
        @param indexes_to_retrieve: Indexes of the notes to be retrieved
        @param name: Name of the song

        @return: Reduced Music21 Stream-Part of Reduced Song Features
        """
        notes = [feat if i in indexes_to_retrieve else 'REMOVED' for i,
                 feat in enumerate(song_features['features']['pitch'])]
        durations = [m21.duration.Duration(quarterLength=float(Fraction(dur))) if dur != '0.0' else m21.duration.GraceDuration(
            0.25) for dur in song_features['features']['duration']]
        offsets = [float(Fraction(offset))
                   for offset in song_features['features']['offsets']]

        m21_notes = [m21.note.Note(pitch=note, duration=dur, offset=off) if note != 'REMOVED' else m21.note.Rest(
            duration=dur, offset=off) for note, dur, off in zip(notes, durations, offsets)]

        m21_stream = m21.stream.Part(m21_notes)  # type: ignore
        if name:
            m21_stream.partName = name
        return m21_stream

    def reduce_tonal(self, song_features, degree=0.75, distance='euclidean'):
        """
        Reduce Song Features according to Tonal Reduction

        @param song_features: Song Features
        @param degree: threshold of the maximal tonal distance to be taken into account
        @param distance: distance function to be used ('euclidean' or 'cosine')

        @return indexes_to_retrieve: Indexes of the notes to be retrieved
        """
        pitch_distances = sorted(list(enumerate(get_tonal_distance(
            song_features['features']['midipitch'], distance))), key=lambda x: x[1], reverse=False)
        return sorted([i for (i, _) in pitch_distances[:int(len(pitch_distances) * degree)]])

    def reduce_metric(self, song_features, degree=0.75):
        """
        Reduce Song Features according to Metric Reduction

        @param song_features: Song Features
        @param degree: threshold of the minimum metric weight to be taken into account

        @return indexes_to_retrieve: Indexes of the notes to be retrieved
        """
        return [i for i, beat_strength in enumerate(song_features['features']['beatstrength']) if beat_strength >= degree]

    def reduce_intervallic(self, song_features, degree=0.75):
        """
        Reduce Song Features according to Intervallic Reduction

        @param song_features: Song Features
        @param degree: percentage of notes to be removed (default: 0.75)
        @param return_intervals: return the intervals between the notes (default: False)

        @return indexes_to_retrieve: Indexes of the notes to be retrieved
        """
        intervals = sorted([(i, abs(interval)) if interval is not None else (i, 0.0) for i, interval in enumerate(
            song_features['features']['chromaticinterval'])], key=lambda x: x[1], reverse=True)
        return sorted([i for (i, _) in intervals[:int(len(intervals) * degree)]])

    def reduce_combined(self, song_features, degree=0.75, distance='euclidean', graphs=False):
        """
        Reduce Song Features according to Combined Reduction

        @param song_features: Song Features
        @param degree: percentage of notes to be removed
        @param distance: distance function to be used ('euclidean' or 'cosine')

        @return indexes_to_retrieve: Indexes of the notes to be retrieved
        """
        tonal_distances = get_tonal_distance(
            song_features['features']['midipitch'], distance)
        normalized_tonal_distances = normalize(tonal_distances, alg="zscore")

        metrical_beats = np.asarray(song_features['features']['beatstrength'])
        normalized_beats = normalize(metrical_beats, alg="zscore")

        intervals = np.asarray(song_features['features']['chromaticinterval'])
        intervals[intervals == None] = 0.0
        normalized_intervals = normalize(np.abs(intervals), alg="zscore")

        combined_weights = [(i, sum(values)/3.0) for i, values in enumerate(
            zip(normalized_tonal_distances, normalized_beats, normalized_intervals))]

        if graphs:
            self.plot_combined(song_features, normalized_tonal_distances,
                               normalized_beats, normalized_intervals, combined_weights)

        return sorted([i for (i, _) in sorted(combined_weights, key=lambda x: x[1], reverse=True)[:int(len(combined_weights) * degree)]])

    def plot_combined(self, song_features, normalized_tonal_distances, normalized_beats, normalized_intervals, combined_weights):
        """Plot the combined reduction values to verify best combined reduction weights"""

        with plt.style.context('Solarize_Light2'):  # type: ignore
            fig, axs = plt.subplots(2, 2)
            fig.set_size_inches(18, 12)

            ((ax1, ax2), (ax3, ax4)) = axs

            ax1.scatter(range(len(normalized_tonal_distances)),
                              normalized_tonal_distances, label='tonal', color='red')  # type: ignore
            ax1.set_title('Tonal Distance')  # type: ignore

            ax2.scatter(range(len(normalized_beats)), normalized_beats,
                              label='metrical', color='green')  # type: ignore
            ax2.set_title('Metrical Distance')  # type: ignore

            ax3.scatter(range(len(normalized_intervals)), normalized_intervals,
                              label='intervallic', color='blue')  # type: ignore
            ax3.set_title('Intervallic Distance')  # type: ignore

            ax4.scatter(range(len(combined_weights)), [
                              i[1] for i in combined_weights], label='combined', color='black')  # type: ignore
            ax4.set_title('Combined Distance')  # type: ignore

            for ax in axs.flat:  # type: ignore
                ax.set(xlabel='Timesteps', ylabel='Distance')

            # Hide x labels and tick labels for top plots and y ticks for right plots.
            for ax in axs.flat:  # type: ignore
                ax.label_outer()

            fig.savefig(
                f'data/combined_graphs/{song_features["id"]}.png', dpi=300)
            plt.close()
