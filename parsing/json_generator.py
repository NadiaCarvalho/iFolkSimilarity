# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 16:04:37 2022

@author: Daniel Diogo
"""

import json
from song_features import *
from music21 import * 
import mei_parsing as mei

"""
Methods to use from mei_parsing.py:
    musicXMLfromMEI(song, id)
    midiFromMEI(song, score)
    mei_to_string(mei)
    parseSongMetadata(song)

"""

# Pre-processing functions

def padSplittedBars(s):
    # Alternative made by Daniel
    
    for part in s.parts:
        measures = list(part.getElementsByClass('Measure'))
        for m in zip(measures,measures[1:]): 
            if m[0].quarterLength + m[0].paddingLeft + m[1].quarterLength == m[0].barDuration.quarterLength: 
                m[1].paddingLeft = m[0].quarterLength
    
    # Original 'For' Cycle
    
    #for partId in partIds:
    #partIds = [part.id for part in s.parts]
    
    #    measures = list(s.parts[str(partId)].getElementsByClass('Measure')) 
    #    for m in zip(measures,measures[1:]): 
    #        if m[0].quarterLength + m[0].paddingLeft + m[1].quarterLength == m[0].barDuration.quarterLength: 
    #            m[1].paddingLeft = m[0].quarterLength 
    
    return s

def removeGrace(s):
    ixs = [s.index(n) for n in s.notes if n.quarterLength == 0.0]
    for ix in reversed(ixs):
        s.pop(ix)
    return s
"""
Old parseMelody method:

def parseMelody(path):
    try:
        s = m21.converter.parse(path)
    except m21.converter.ConverterException:
        raise ParseError(path)
    #add padding to partial measure caused by repeat bar in middle of measure
    #s = padSplittedBars(s)
    s_noties = s.stripTies()
    m = s_noties.flat
    removeGrace(m)
    return m
"""

def noStreamErrorSolver(s):
    firstPartFound = False
    newScore = stream.Score()
    partEx = stream.Part()
    for element in s:
        if type(partEx) == type(element):
            if firstPartFound == True:
                continue
            else:
                firstPartFound = True
        newScore.append(element)
    return newScore

def checkChords(s, metadata):
    createNewStream = False
    for x in s.notes:
        if (x.isChord):
            createNewStream = True
            ImportantIDs = []
            for i in metadata['phrases']:
                ImportantIDs.append(metadata['phrases'][str(i)]['start'][1:])
                ImportantIDs.append(metadata['phrases'][str(i)]['end'][1:])
            #for 
    
    if(createNewStream):
        exChord = chord.Chord()
        newStream = stream.Stream()
        for element in s:
            newNote = note.Note()
            if(type(element) == type(exChord)):
                for n in element.notes:
                    if n.pitch == element.root():
                        #n.duration = element.duration
                        newNote = n
                        newNote.duration = element.duration
                        
                    elif n.id in ImportantIDs:
                        newNote.id = n.id
                        
                newStream.append(newNote)                                
            else:
                newStream.append(element)
        
        s = newStream

    return s

# New parse melody method using co-poem's methods:

def parseMelody(path):
    metadata = mei.parseSongMetadata(path)
    #print(metadata['phrases'])
    if metadata['title'] == '':
        metadata['title'] = metadata['alt_title']
    
    musicXML = mei.musicXMLFromMEI(path, metadata)    
    # Debugging
    #musicXML[3].show()
    
    # If there are various instruments it is needed only the first one
    s = instrument.partitionByInstrument(musicXML[3])
    
    
    # If there are various voices for the same instrument takes the upper voice
    # Solving of the "Stream == None" type of Error
    # TO DO: SOLVE THIS
    if s == None:    
        s = musicXML[3]
        s = noStreamErrorSolver(s)
        #s.show()
    #s.show()  
    #add padding to partial measure caused by repeat bar in middle of measure
    s = padSplittedBars(s)
    
    s = s.flat
    
    s = checkChords(s, metadata)
    
    s_noties = s.stripTies()
    
    #melody = s_noties.flat
    melody = removeGrace(s)
    
    #melody.show()
    
    return melody, metadata, musicXML[0]

"""
def get_tunefamily(file_name):
    j=0
    k=0
    for char in file_name:
        if (char ==  "-"):
            j+=1
        if j == 4:
            return file_name[8:k]
        k+=1
    return "No Tune Family"
"""

def mei_to_mtc(path, filename):

    #Correct Path Checking
    
    try:
        s, meta, xml = parseMelody(path)
    except ParseError:
        print(path, "does not exist")
        return None
    
    f = open('bugging' + '.xml', "w")
    f.write(xml)
    f.close()
    
    #s.show()
    
    # Tonic and mode calculations
    
    
    if meta['real_key']:        
        if 'flat' in meta['real_key']:
            addAccidental = 'b'
        elif 'sharp' in meta['real_key']:
            addAccidental = '#'
        else:
            addAccidental = ''
        
        trueTonic = meta['real_key'][0] + addAccidental
        tonicPitch = note.Note(trueTonic)
        tonicPitch = tonicPitch.pitch
        
        tonic = []
        mode = []
        
        for n in s.notes:
            tonic.append(trueTonic)
            mode.append(meta['mode'])
    
    else:
        tonic, mode = m21TOKey(s)
        trueTonic = tonic[0]
        tonicPitch = note.Note(tonic[0])
        tonicPitch = tonicPitch.pitch
        
        if meta['mode']:
            
            if mode[0] == 'major':
                if meta['mode'] == 'Dorian':
                    tonicPitch = tonicPitch.transpose(2)
                    trueTonic = tonicPitch.name
                if meta['mode'] == 'Phyrigian':
                    tonicPitch = tonicPitch.transpose(4)
                    trueTonic = tonicPitch.name
                if meta['mode'] == 'Lydian':
                    tonicPitch = tonicPitch.transpose(5)
                    trueTonic = tonicPitch.name
                if meta['mode'] == 'Mixolydian':
                    tonicPitch = tonicPitch.transpose(7)
                    trueTonic = tonicPitch.name
            
            if mode[0] == 'minor':
                if meta['mode'] == 'Dorian':
                    tonicPitch = tonicPitch.transpose(5)
                    trueTonic = tonicPitch.name
                if meta['mode'] == 'Phyrigian':
                    tonicPitch = tonicPitch.transpose(7)
                    trueTonic = tonicPitch.name
                if meta['mode'] == 'Lydian':
                    tonicPitch = tonicPitch.transpose(8)
                    trueTonic = tonicPitch.name
                if meta['mode'] == 'Mixolydian':
                    tonicPitch = tonicPitch.transpose(10)
                    trueTonic = tonicPitch.name
    
        if trueTonic != tonic[0] or meta['mode'] != mode[0]:
            length = len(tonic)
            del tonic
            del mode
            tonic = []
            mode = []
            for i in range(length):
                tonic.append(trueTonic)
                mode.append(meta['mode'])
               
    # Feature Calculation
    
    sd = m21TOscaledegrees(s, tonicPitch)
    sdspec = m21TOscaleSpecifiers(s, tonicPitch)
    diatonicPitches = m21TOdiatonicPitches(s, tonicPitch)
    diatonicinterval = toDiatonicIntervals(s)
    chromaticinterval = toChromaticIntervals(s)
    pitch = m21TOPitches(s)
    pitch40 = m21TOBase40(s)
    midipitch = m21TOMidiPitch(s)
    pitchproximity = getPitchProximity(chromaticinterval)
    pitchreversal = getPitchReversal(chromaticinterval)
    nextisrest = m21TONextIsRest(s)
    restduration_frac = m21TORestDuration_frac(s)
    contour3 = midipitch2contour3(midipitch)
    contour5 = midipitch2contour5(midipitch, thresh=3)
    
    duration = m21TODuration(s)
    duration_fullname = m21TODuration_fullname(s)
    duration_frac = m21TODuration_frac(s)
    durationcontour = getDurationcontour(duration_frac)
    
    onsettick = m21TOOnsetTick(duration_frac)
    ima = imaWeight(onsettick)
    ic = getIMAcontour(ima)
    
    #Phrase Position
    phrasepos = getPhrasePos(s, meta['phrases'], filename)
    
    
    #Depends on Phrase Position
    phrase_end = getPhraseEnd(phrasepos)
    phrase_ix = getPhraseIx(phrasepos)
    
    songpos = getSongPos(onsettick)
    
    ioi_frac = getIOI_frac(duration_frac, restduration_frac)
    ioi = getIOI(ioi_frac)
    ior_frac = getIOR_frac(ioi_frac)
    ior = getIOR(ior_frac)
    
    gpr2a_Frankland = getFranklandGPR2a(restduration_frac)
    gpr2b_Frankland = getFranklandGPR2b(duration, restduration_frac) #or use IOI and no rest check!!!
    gpr3a_Frankland = getFranklandGPR3a(midipitch)
    gpr3d_Frankland = getFranklandGPR3d(ioi)
    gpr_Frankland_sum = [sum(filter(None, x)) for x in zip(gpr2a_Frankland, gpr2b_Frankland, gpr3a_Frankland, gpr3d_Frankland)]
    lbdm_rpitch = getDegreeChangeLBDMpitch(chromaticinterval)
    lbdm_spitch = getBoundaryStrengthPitch(lbdm_rpitch, chromaticinterval)
    lbdm_rioi = getDegreeChangeLBDMioi(ioi)
    lbdm_sioi = getBoundaryStrengthIOI(lbdm_rioi, ioi)
    lbdm_rrest = getDegreeChangeLBDMrest(restduration_frac)
    lbdm_srest = getBoundaryStrengthRest(lbdm_rrest, restduration_frac)
    lbdm_boundarystrength = getLocalBoundaryStrength(lbdm_spitch, lbdm_sioi, lbdm_srest)
    
    if hasLyrics(meta):
        song_type = 'Vocal'
    else:
        song_type = 'Instrumental'
    
    # Metric Feature Calculation
    
    try:
        #pass
        timesignature = m21TOTimeSignature(s)
        beat_str, beat_fraction_str = m21TOBeat_str(s)
        beat_float = m21TOBeat_float(s)
        mc = m21TOmetriccontour(s)
        beatstrength = m21TObeatstrength(s)
        # Depends on Phrase Position
        beatinsong, beatinphrase, beatfraction = m21TOBeatInSongANDPhrase(s, phrasepos)
        beatinphrase_end = getBeatinphrase_end(beatinphrase, phrase_ix, beat_float)
        
    except NoMeterError:
        print(path, "has no time signature")
        timesignature = [None]*len(sd)
        beat_str, beat_fraction_str = [None]*len(sd) , [None]*len(sd)
        beat_float = [None]*len(sd)
        mc = [None]*len(sd)
        beatstrength = [None]*len(sd)
        beatinsong, beatinphrase, beatfraction = [None]*len(sd), [None]*len(sd), [None]*len(sd)
        beatinphrase_end = [None]*len(sd)
    
    metadata_string = []
    #print(metadata_string)
    return meta | {"type" : song_type,
                   'freemeter' : not hasmeter(s),
                   'features': {    'scaledegree': sd,
                                    'scaledegreespecifier' : sdspec,
                                    'tonic': tonic,
                                    'mode': mode,
                                    'metriccontour':mc,
                                    'imaweight':ima,
                                    'pitch40': pitch40,
                                    'midipitch': midipitch,
                                    'diatonicpitch' : diatonicPitches,
                                    'diatonicinterval': diatonicinterval,
                                    'chromaticinterval': chromaticinterval,
                                    'pitchproximity': pitchproximity,
                                    'pitchreversal': pitchreversal,
                                    'nextisrest': nextisrest,
                                    'restduration_frac': restduration_frac,
                                    'duration': duration,
                                    'duration_frac': duration_frac,
                                    'duration_fullname': duration_fullname,
                                    'durationcontour': durationcontour,
                                    'onsettick': onsettick,
                                    'beatfraction': beatfraction,
                                    'phrasepos': phrasepos,
                                    'phrase_ix': phrase_ix,
                                    'phrase_end': phrase_end,
                                    'songpos': songpos,
                                    'beatinsong': beatinsong,
                                    'beatinphrase': beatinphrase,
                                    'beatinphrase_end': beatinphrase_end,
                                    'IOI_frac': ioi_frac,
                                    'IOI': ioi,
                                    'IOR_frac': ior_frac,
                                    'IOR': ior,
                                    'imacontour': ic,
                                    'pitch': pitch,
                                    'contour3' : contour3,
                                    'contour5' : contour5,
                                    'beatstrength': beatstrength,
                                    'beat_str': beat_str,
                                    'beat_fraction_str': beat_fraction_str,
                                    'beat': beat_float,
                                    'timesignature': timesignature,
                                    'gpr2a_Frankland': gpr2a_Frankland,
                                    'gpr2b_Frankland': gpr2b_Frankland,
                                    'gpr3a_Frankland': gpr3a_Frankland,
                                    'gpr3d_Frankland': gpr3d_Frankland,
                                    'gpr_Frankland_sum': gpr_Frankland_sum,
                                    'lbdm_spitch': lbdm_spitch,
                                    'lbdm_sioi': lbdm_sioi,
                                    'lbdm_srest': lbdm_srest,
                                    'lbdm_rpitch': lbdm_rpitch,
                                    'lbdm_rioi': lbdm_rioi,
                                    'lbdm_rrest': lbdm_rrest,
                                    'lbdm_boundarystrength': lbdm_boundarystrength
        }}
            
    