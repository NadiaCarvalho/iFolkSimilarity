# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 11:08:53 2022

@author: Nádia Carvalho
@editor: Daniel Diogo
"""

import base64
import os
import sys
from xml.etree import ElementTree as ET
import ast

import music21

NAME_SPACE = {'mei': 'http://www.music-encoding.org/ns/mei'}
ID_SPACE = '{http://www.w3.org/XML/1998/namespace}id'

NEW_GENRES = {
        'Canción De Cuna': 'Lullaby',
        'Canción Cuna': 'Lullaby',
        'Cuna': 'Lullaby',
        'Lullaby': 'Lullaby',
        'Ninna Nanna': 'Lullaby',
        'Canción Infantil, Juego De Palmas': 'Children song',
        'Canción Infantil': 'Children song',
        'Canción Infatil': 'Children song',
        'Corro': 'Children song',
        'Canción De Corro': 'Children song',
        'De Corro': 'Children song',
        'Canción De Columpio': 'Children song',
        'De Columpio': 'Children song',
        'Canción De Rueda': 'Children song',
        'De Rueda': 'Children song',
        'Canción De Comba': 'Children song',
        'De Comba': 'Children song',
        'Canción De Procesión': 'Children song',
        'Filastrocca': 'Children song',
        'De Baile': 'Dance song',
        'Canción De Baile': 'Dance song',
        'Danza': 'Dance song',
}

MEILINKS = {
    'title': ".//mei:title[@type='main']",
    'alt_title': ".//mei:incip[@type='lyrics']//mei:head",
    'author': ".//mei:author",
    'source': ".//mei:meiHead/mei:fileDesc/mei:sourceDesc/mei:source//mei:title",
    'source_subtitle': ".//mei:title[@type='subordinate']",
    'compiler': ".//mei:persName[@role='compiler']",
    'informer': ".//mei:persName[@role='informante']",
    'encoder': ".//mei:persName[@role='encoder']",
    'date': ".//mei:biblStruct//mei:date",
    'city': ".//mei:term[@type='localidad']",
    'district': ".//mei:term[@type='distrito']",
    'region': ".//mei:term[@type='distrito']",
    'genre': ".//mei:term[@type='genre']",
    'meter': ".//mei:meter",
    'tempo': ".//mei:tempo",
    'real_key': ".//mei:key",
    'mode': ".//mei:key",
    'time_signature': ".//mei:scoreDef",
    'ambitus_low': ".//mei:ambNote[@type='lowest']",
    'ambitus_high': ".//mei:ambNote[@type='highest']",
    'rhythm_pattern': ".//mei:supplied[@type='rythymn pattern']//mei:note",
    'lyrics': ".//mei:workList//mei:annot",
}

MEILINKS_extra = {
    'colaborador': ".//mei:persName[@role='prólogo y estudio']",
    'region': ".//mei:term[@type='regione']",
    'district': ".//mei:term[@type='provincia']",
    'city': ".//mei:term[@type='città']",
}


def alternativeLocals(mei_file, key, info):
    """
    Parse Locals
    """
    res = None
    if not info or not info[0].get('label'):
        info = mei_file.getroot().findall(
            MEILINKS_extra[key], NAME_SPACE)
        if info:
            res = info[0].text
    else:
        res = info[0].get('label')
    return res


def parseTitle(mei_file, key, info):
    """
    Parse Title
    """
    title = ''
    if len(info) == 0 or info[0].text == None or info[0].text == 'No title':
        info = mei_file.getroot().findall(
            MEILINKS_extra[key], NAME_SPACE)
        if len(info) > 0:
            title = info[0].text
    if len(info) > 0 and info[0].text[0].isdigit():
        title = ' '.join(info[0].text.split(' ')[1:])
    return title

def parseTitle2(info):
    """
    Get Correct Title
    """
    title = 'No Title'
    if len(info) > 0 and info[0].text:
        if info[0].text[0].isdigit():
            title = ' '.join(info[0].text.split(' ')[1:])
        else:
            title = info[0].text
    return title.capitalize()

def parseTimeSignatures(info):
    """
    Parse Time Signature
    """
    tss = list(set([str(ts.get('meter.count')) + '/' +
                    str(ts.get('meter.unit')) for ts in info]))
    tss.sort()
    if 'None/None' in tss:
        tss.remove('None/None')
    tss = ', '.join(tss)
    return tss


def getMetadataFromMEI(mei_file):
    """
    Get METADATA FROM MEI Files
    """
    metadata = {}
    for key, mei_link in MEILINKS.items():
        info = mei_file.getroot().findall(mei_link, NAME_SPACE)
        if len(info) > 0:
            metadata[key] = info[0].text
            if key == 'mode':
                metadata[key] = info[0].get('mode')
            elif key == 'title' or key == 'alt_title':
                metadata[key] = parseTitle2(info)
            elif key == 'author' and info[0].text == None:
                metadata[key] = 'Anonymous'
            elif key == 'time_signature':
                metadata[key] = parseTimeSignatures(info)
            elif 'ambitus' in key:
                metadata[key] = str(info[0].get('pname')) + \
                    str(info[0].get('oct'))
            elif key == 'rhythm_pattern':
                metadata[key] = ' '.join([str(note.get('dur')) + '.' * int(note.get(
                    'dots')) if note.get('dots') else str(note.get('dur')) for note in info])
            elif key == 'genre' and metadata[key].lower() == 'romance de corro':
                metadata[key] = 'corro'
            elif key == 'lyrics' and info[0].text:
                lyrics = ' '.join(info[0].text.split('                  '))
                if lyrics[0] == '\n':
                    lyrics = lyrics[1:]
                metadata[key] = lyrics
        elif key in ['region', 'district', 'city']:
            metadata[key] = alternativeLocals(mei_file, key, info)
        else:
            metadata[key] = None

        if metadata[key]:
            if key != 'lyrics':
                metadata[key] = ' '.join([s.capitalize()
                                          for s in metadata[key].split(' ')])
            if key != 'time_signature':
                metadata[key] = metadata[key].replace('/', '')
                if metadata[key][0] == ' ':
                    metadata[key] = metadata[key].replace(' ', '', 1)

    return metadata


def clean_meter(meter, time_signature):
    """
    Clean Meter
    """
    if meter.lower() == 'binario' or meter.lower() == 'birnario':
        meter = 'binary'
    if '6/8' in time_signature and ',' not in time_signature:
        meter = 'binary'
    if meter.lower() == 'ternarioo' or meter.lower() == 'ternario':
        meter = 'ternary'
    if meter.lower() == 'polirrítmica' or meter.lower() == 'polirrítmico':
        meter = 'polyrhythmic'
    if meter.lower() == 'sin compás':
        meter = 'free'
    return meter.capitalize()


def get_phrase_info(song):
    """
    GET Phrases and Note IDs of delimitations and cadence type for last note of phrase
    """
    phrases = {}

    try:
        phrases_tags = song.getroot().findall(".//mei:phrase", NAME_SPACE)
        cadence_tags = song.getroot().findall(".//mei:note[@type]", NAME_SPACE)
        cadences = {'#' + ct.get(ID_SPACE): ct.get('type')
                    for ct in cadence_tags}

        for phrase in phrases_tags:
            phrases[phrase.get('n')] = {
                'start': phrase.get('startid'),
                'end': phrase.get('endid'),
                'type': phrase.get('type'),
                'cadence': cadences[phrase.get('endid')] if phrase.get('endid') in cadences else None
            }
    except Exception as e:
        print("Exception of Phrases - line {} - {}".format(sys.exc_info()
              [-1].tb_lineno, str(e)))

    return phrases


def parseSongMetadata(song):
    """
    Parse MEI File's Metadata from Song
    """
    identification = song[song.rfind(os.sep) + 1: -4]
    print("Started " + identification)

    song_tree = ET.parse(song)
    metadata = getMetadataFromMEI(song_tree)
    metadata['meter'] = clean_meter(
        metadata['meter'], metadata['time_signature'])

    metadata['phrases'] = get_phrase_info(song_tree)
     
    if metadata['genre'] in NEW_GENRES:
        metadata['genre'] = NEW_GENRES[metadata['genre']]
    # [67:69] for Daniel's PC
    # [:2] the original array indexes

    if identification[67:69] == "ES":
        metadata['country'] = "Spain"
    elif identification[67:69] == "IT":
        metadata['country'] = "Italy"
    else:
        metadata['country'] = "Portugal"

    metadata['name'] = identification
    metadata['mei'] = song_tree
    return metadata


def parseEndings(song):
    """
    Parse the Ending Tag of MEI that was giving errors
    """
    ending_streams = {}

    mei_file = ET.parse(song)
    score_def = mei_file.getroot().findall('.//mei:scoreDef', NAME_SPACE)

    string_scoredef = ET.tostring(score_def[0], encoding="unicode")
    string_begin = """
                    <mei meiversion="4.0.0" xmlns="http://www.music-encoding.org/ns/mei" xmlns:xlink="http://www.w3.org/1999/xlink">
                        <music>
                            <score>
                    """
    string_end = """</score></music></mei>"""

    endings = mei_file.getroot().findall('.//mei:ending', NAME_SPACE)

    for end in endings:
        string_child = "<section>"
        for child in end:
            string_child += ET.tostring(child, encoding="unicode")
        string_child += "</section>"

        mei_string = string_begin + string_scoredef + string_child + string_end
        score = music21.converter.parse(
            mei_string, format='mei', forceSource=True)
        ending_streams[end[0].get('n')] = (score, end.get('n'))
    return ending_streams


def check_if_repend_repstart(measures):
    """
    Check if Double Repetitions
    """
    for i, meas in enumerate(measures[:-1]):
        if (meas.rightBarline and hasattr(meas.rightBarline, 'direction') and meas.rightBarline.direction == 'end'):
            if (measures[i+1].leftBarline and hasattr(measures[i+1].leftBarline, 'direction') and measures[i+1].leftBarline.direction == 'start'):
                meas.rightBarline = music21.bar.Barline()
    return False


def musicXMLFromMEI(song, identification):
    """
    Export MusicXML from MEI
    """
    try:
        score = music21.converter.parse(song, format='mei', forceSource=True)

        try:
            score.expandRepeats()
        except Exception as e:
            # print("Song {} has endings!".format(identification['name']))
            endings_streams = parseEndings(song)

            for key, (stream, end) in endings_streams.items():
                for i, part in enumerate(stream.getElementsByClass(music21.stream.Part)):
                    if key is None:
                        key = str(stream.parts[i].getElementsByClass(
                            music21.stream.Measure)[0].number)
                    last_measure = score.parts[i].measure(int(key)-1)
                    ho = last_measure.offset + last_measure.highestTime

                    measures_to_add = part.getElementsByClass(
                        music21.stream.Measure)
                    measures_to_add[0].timeSignature = None
                    measures_to_add[0].removeByClass(['Clef', 'KeySignature'])

                    for meas in measures_to_add:
                        score.parts[i].insertAndShift(ho, meas)
                        ho += meas.highestTime

                    first_m = measures_to_add[0].number
                    last_m = measures_to_add[-1].number

                    if end == "2" or end == "3":
                        score.parts[i].measure(
                            last_m).removeByClass(['RepeatMark'])

                    if "..." in end:
                        num_endings = [int(s)
                                       for s in end.split('-') if s.isdigit()]
                        music21.repeat.insertRepeatEnding(
                            score.parts[i], first_m, last_m, num_endings, inPlace=True)
                        score.recurse().getElementsByClass(
                            'RepeatBracket')[-1].overrideDisplay = end
                    else:
                        music21.repeat.insertRepeatEnding(
                            score.parts[i], first_m, last_m, end, inPlace=True)

        check_if_repend_repstart(
            score.recurse().getElementsByClass(music21.stream.Measure))

        score.metadata = music21.metadata.Metadata(otl=str(identification['title']), alternativeTitle=str(
            identification['alt_title']), subtitle=identification['name'])
        score.metadata.composer = identification['author']
        if identification['date']:
            score.metadata.date = identification['date']

        non_prep_lyrics = score.lyrics(recurse=True, ignoreBarlines=False)
        lyrics = prepareLyrics(non_prep_lyrics)

        GEX = music21.musicxml.m21ToXml.GeneralObjectExporter(score)
        mxScore = GEX.parse()
        outStr = mxScore.decode('utf-8')

        return outStr.strip(), bool(non_prep_lyrics), lyrics, score
    except Exception as e:
        print("Music21 can't parse song {}:\n- line {} - {}".format(
            identification['name'], sys.exc_info()[-1].tb_lineno, str(e)))
        return '', False, '', None


def prepareLyrics(non_prep_lyrics):
    """
    Prepare Lyrics as Text
    """
    prep_lyrics = {}
    for part, lycs in non_prep_lyrics.items():
        for phrase in lycs:
            for meas in phrase:
                for sil in meas[0]:
                    if part not in prep_lyrics:
                        prep_lyrics[part] = ''
                    if sil:
                        prep_lyrics[part] += sil.text + ' '
            prep_lyrics[part] += '\n '
    return '\n\n '.join(prep_lyrics.values())[:-1]


def midiFromMEI(song, score):
    """
    Export MIDI from MEI
    """
    if score is None:
        return ''

    try:
        score.expandRepeats()
    except:
        for part in score.getElementsByClass(music21.stream.Part):
            part.measure(-1).rightBarline = music21.bar.Repeat(direction='end')
    try:
        mf = music21.midi.translate.streamToMidiFile(score)
        return base64.b64encode(mf.writestr())
    except Exception as e:
        print("Music21 can't transform to MIDI {}:\n- line {} - {}".format(song,
                                                                           sys.exc_info()[-1].tb_lineno, str(e)))
        return ''


def mei_to_string(mei):
    return ET.tostring(mei.getroot(), encoding="unicode")


def phrases_to_viewpoints(parser, phrases):
    """
    Add Phrase Info to Viewpoints
    """
    if len(parser.get_part_events().keys()) == 0:
        return

    events = parser.get_part_events()[list(
        parser.get_part_events().keys())[0]]

    phr_dict = ast.literal_eval(phrases[0][0])
    for phrase in phr_dict.values():

        start_view = [i for i, ev in enumerate(
            events) if '#' + ev.get_viewpoint('id') == phrase['start']]
        end_view = [i for i, ev in enumerate(events)
                    if '#' + ev.get_viewpoint('id') == phrase['end']]

        for i, j in enumerate(start_view):
            end_i = -1
            if i < len(end_view):
                end_i = end_view[i]

            events[j].add_viewpoint('phrase.boundary', 1)
            events[j].add_viewpoint('phrase.length', end_i - j + 1)
            events[j].add_viewpoint('phrase.type', phrase['type'])

            for event in events[j + 1:end_i]:
                event.add_viewpoint('phrase.boundary', 0)
                event.add_viewpoint('phrase.length', end_i - j + 1)
                event.add_viewpoint('phrase.type', phrase['type'])

            events[end_i].add_viewpoint('phrase.boundary', -1)
            events[end_i].add_viewpoint('phrase.length', end_i - j + 1)
            events[end_i].add_viewpoint('phrase.type', phrase['type'])
            events[end_i].add_viewpoint(
                'phrase.cadence', phrase['cadence'])

    # import app.composition.representation.utils.printing as printUtils
    # print(printUtils.show_sequence_of_viewpoint_without_offset(
    #     events, 'phrase.boundary'))