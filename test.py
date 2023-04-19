from collections import Counter
import glob
import json
import os
import sys
from xml.etree import ElementTree as ET

import music21 as m21

from src.parser.mtc_extractor import MTCExtractor


def main(path='eval_data/binary/original/PT-1998-XX-DM-001.mei'):
    tree = ET.parse(path)
    root = tree.getroot()
    mtc = MTCExtractor(path, root)
    features = mtc.process_stream()
    print(features[0]['beatstrength'])  # type: ignore


def test_meter():
    s = m21.stream.Stream([m21.note.Note('C', quarterLength=2/3), m21.note.Note('D', quarterLength=1/3),  # type: ignore
                          m21.note.Note('E', quarterLength=1/3), m21.note.Note('F', quarterLength=2/3)])
    s.insert(0, m21.meter.TimeSignature('3/4'))  # type: ignore
    s.show()
    from src.parser.feature_extractors.metric_extractor import MetricExtractor
    print(MetricExtractor(s).get_all_features())
    print([n.beatStrength for n in s.recurse().getElementsByClass(m21.note.Note)])


def dump_json_features(song, song_features):
    """
    Dump the song features to a json file

    @param category: binary or ternary
    @param song: song id
    @param song_features: song features
    """
    try:
        json.dump(song_features, open(
            song.replace('.mei', '.json').replace('original', 'parsed'), 'w'), ensure_ascii=False, indent=4)
    except:
        print('Error parsing song: ' + song)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[  # type: ignore
            1]
        print(exc_type, fname, exc_tb.tb_lineno)  # type: ignore
        print()


def get_all_songs(dump_json_features):
    from src.parser import MeiParser
    mei_parser = MeiParser()

    songs = glob.glob('data/original/*.mei')

    for song in songs:
        song = song.replace("-v1", "").replace("-v2", "")
        song_features = mei_parser.parse_mei(
            song)

        if 'id' in song_features.keys():  # type: ignore
            dump_json_features(song, song_features)
        else:
            for key, song_features in song_features.items():  # type: ignore
                dump_json_features(f'{song[:-4]}-{key}.mei', song_features)

if __name__ == '__main__':
    # main()
    # test_meter()
    # get_all_songs(dump_json_features)

    songs = glob.glob('data/parsed/*-v1.json')
    print(len(songs))
    genres = []
    for song in songs:
        song_features = json.load(open(song))
        genres.append(song_features['genre'].lower())

    counter = Counter(genres)
    print(counter.most_common())