

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 19:09:43 2022

@author: Daniel Diogo
"""

import music21 as m21
import numpy as np
from fractions import Fraction
from collections import defaultdict
from math import gcd, lcm
from functools import reduce
from imapy_music import IMA
from xml.etree import ElementTree as ET

# Error Classes

#song has no meter

class NoMeterError(Exception):
    def __init__(self, arg):
        self.args = arg
    def __str__(self):
        return repr(self.value)
    
#parsing failed
class ParseError(Exception):
    def __init__(self, arg):
        self.args = arg
    def __str__(self):
        return repr(self.value)

epsilon = 0.0001

# full description of the features here:
    # https://pvankranenburg.github.io/MTCFeatures/melodyrepresentation.html

"""     
        pitch                   #Pitch of the note in string representation as defined in music21.
        midipitch               #MIDI note number representing the pitch.
        pitch40                 #Pitch in base40 representation.
        contour3                #Contour of the pitch with respect to the previous note
        contour5                #Contour of the pitch with respect to the previous note. ‘--’ and ‘++’ are leaps >= 3 in midipitch
        chromaticinterval       #Chromatic interval (diff of midipitch) with respect to previous note
        diatonicinterval        #Diatonic interval with previous note.
        tonic                   #Pitch class of the tonic for the current note.
        mode                    #Mode for the current note.
        scaledegree             #Scale degree of the pitch.
        scaledegreespecifier    #Specifier of the scaledegree: Perfect, Major, Minor, Augmented, Diminished, … above the tonic.
"""
    
#functions as stated in https://github.com/pvankranenburg/MTCExtractFeatures/blob/b870415b9fb8315c77cfda19fc30403257a68e37/src/mtc_to_seqs.py    

#method returns out of range with one part

def padSplittedBars(s):
    partIds = [part.id for part in s.parts] 
    for partId in partIds: 
        measures = list(s.parts[partId].getElementsByClass('Measure')) 
        for m in zip(measures,measures[1:]): 
            if m[0].quarterLength + m[0].paddingLeft + m[1].quarterLength == m[0].barDuration.quarterLength: 
                m[1].paddingLeft = m[0].quarterLength 
    return s


# All types of pitch measurement
   
def m21TOPitches(s):
    return [n.nameWithOctave for n in s.pitches] 
   
def m21TOMidiPitch(s):
    return [n.midi for n in s.pitches]
 
def m21TOBase40(s):
    return [m21.musedata.base40.pitchToBase40(n.nameWithOctave) for n in s.pitches]

#Contour 3 and 5

def getContour3(midipitch1, midipitch2):
    if midipitch1 > midipitch2 : return '-'
    if midipitch1 < midipitch2 : return '+'
    return '='

def getContour5(midipitch1, midipitch2, thresh):
    diff = midipitch2 - midipitch1
    if   diff >= thresh : return '++'
    elif diff > 0 : return '+'
    elif diff == 0 : return '='
    elif diff <= -thresh : return '--'
    elif diff < 0 : return '-'

def midipitch2contour3(mp, undef=None):
    return [undef] + [getContour3(p[0], p[1]) for p in zip(mp,mp[1:])]

def midipitch2contour5(mp, thresh=3, undef=None):
    return [undef] + [getContour5(p[0], p[1], thresh) for p in zip(mp,mp[1:])]

#Chromatic Intervals

def toChromaticIntervals(s):
    return [None] + [n[1].midi - n[0].midi for n in zip(s.pitches, s.pitches[1:]) ]

#Diatonic Intervals

def toDiatonicIntervals(s):
    return [None] + [n[1].pitch.diatonicNoteNum - n[0].pitch.diatonicNoteNum for n in zip(s.notes, s.notes[1:]) ]

#Tonic and Mode

def m21TOKey(s):
    keys =  [(k.tonic.name, k.mode) for k in [n.getContextByClass('Key') for n in s.notes]]
    return list(zip(*keys))

#Scale Degree
def m21TOscaledegrees(s, tonic):
    #tonic = s.flat.getElementsByClass('Key')[0].tonic
    scaledegrees = [pitch2scaledegree(x, tonic) for x in s.notes]
    return scaledegrees

def pitch2scaledegree(n, t):
    tonicshift = t.diatonicNoteNum % 7
    return ( n.pitch.diatonicNoteNum - tonicshift ) % 7 + 1

#Scale Degree Specifier

def m21TOscaleSpecifiers(s, tonic):
    #tonic = s.flat.getElementsByClass('Key')[0].tonic
    #put A COPY of the tonic in 0th octave
    lowtonic = m21.note.Note(tonic.name)
    lowtonic.octave = 0
    return [pitch2scaledegreeSpecifer(x, lowtonic) for x in s.notes]

def pitch2scaledegreeSpecifer(n, t):
    interval = m21.interval.Interval(noteStart=t, noteEnd=n)
    return m21.interval.prefixSpecs[interval.specifier]

#Diatonic Pitch

def m21TOdiatonicPitches(s, tonic):
    #tonic = s.flat.getElementsByClass('Key')[0].tonic
    scaledegrees = [pitch2diatonicPitch(x, tonic) for x in s.notes]
    return scaledegrees

def pitch2diatonicPitch(n, t):
    tonicshift = t.diatonicNoteNum % 7
    if tonicshift == 0:
        tonicshift = 7
    return ( n.pitch.diatonicNoteNum - tonicshift )

#Time Signature

def hasmeter(s):
    #no time signature at all
    if not s.getElementsByClass('TimeSignature'): return False
    #maybe it is an Essen song with Mixed meter.
    mixedmetercomments = [c.comment for c in s.getElementsByClass('GlobalComment') if c.comment.startswith('Mixed meters:')]
    if len(mixedmetercomments) > 0:
        return False
    return True

def m21TOTimeSignature(s):
    if not hasmeter(s):
        raise NoMeterError("No Meter")
    return [n.getContextByClass('TimeSignature').ratioString for n in s.notes]

#Beat Strength

def m21TObeatstrength(s):
    if not hasmeter(s):
        raise NoMeterError("No Meter")
    return [n.beatStrength for n in s.notes]

#Metric Contour

def m21TOmetriccontour(s):
    if not hasmeter(s):
        raise NoMeterError("No Meter")
    metriccontour = [notes2metriccontour(x[0], x[1]) for x in zip(s.notes,s.notes[1:])]
    metriccontour.insert(0,None)
    return metriccontour

def notes2metriccontour(n1, n2):
    if n1.beatStrength > n2.beatStrength: return '-'
    if n1.beatStrength < n2.beatStrength: return '+'
    return '='

#Inner Metric Analysis


#IMA Weight

def imaWeight(onsets):
    ima_calculator = IMA(onsets = onsets) 
    return ima_calculator.calculate_IMA_score()

#IMA Contour

def value2contour(ima1, ima2):
    if ima1 > ima2: return '-'
    if ima1 < ima2: return '+'
    return '='

def getIMAcontour(ima):
    imacontour = [value2contour(ima[0], ima[1]) for ima in zip(ima,ima[1:])]
    imacontour.insert(0,None)
    return imacontour

#Duration

def m21TODuration(s):
    return [float(n.duration.quarterLength) for n in s.notes]

#Duration Fullname

def m21TODuration_fullname(s):
    return [n.duration.fullName for n in s.notes]

#Duration Fraction

def m21TODuration_frac(s):
    return [str(Fraction(n.duration.quarterLength)) for n in s.notes]

#Duration Contour

def getDurationcontour(duration_frac):
    return [None] + ['-' if Fraction(d2)<Fraction(d1) else '+' if Fraction(d2)>Fraction(d1) else '=' for d1, d2 in zip(duration_frac,duration_frac[1:])]

#IOI

def getIOI(ioi_frac):
    return [float(Fraction(i)) if i is not None else None for i in ioi_frac]

#IOI Fraction

def getIOI_frac(duration_frac, restduration_frac):
    res =  [str(Fraction(d)+Fraction(r)) if r is not None else str(Fraction(d)) for d, r, in zip(duration_frac[:-1], restduration_frac[:-1])]
    #check last item. If no rest follows, we cannot compute IOI
    if restduration_frac[-1] is not None:
        res = res + [ str( Fraction(duration_frac[-1])+Fraction(restduration_frac[-1]) ) ]
    else:
        res = res + [None]
    return res

#IOR

def getIOR(ior_frac):
    return [float(Fraction(i)) if i is not None else None for i in ior_frac]

#IOR Fraction

def getIOR_frac(ioi_frac):
    return [None] + [str(Fraction(ioi2)/Fraction(ioi1)) if ioi1 is not None and ioi2 is not None else None for ioi1, ioi2 in zip(ioi_frac,ioi_frac[1:])]

# Beatfraction, Beatinsong, Beatinphrase

def m21TOBeatInSongANDPhrase(s, phrasepos):
    if not hasmeter(s):
        raise NoMeterError("No Meter")
    phrasestart_ixs = [ix+1 for ix, pp in enumerate(zip(phrasepos,phrasepos[1:])) if pp[1] < pp[0] ]
    #print(phrasestart_ixs)
    startbeat = Fraction(s.notesAndRests[0].beat)
    if startbeat != Fraction(1):  #upbeat
        startbeat = Fraction(-1 * s.notesAndRests[0].getContextByClass('TimeSignature').beatCount) + startbeat
    startbeat = startbeat - Fraction(1) #shift origin to first first (no typo) beat in measure
    #print('startbeat', startbeat)
    #beatfraction: length of the note with length of the beat as unit
    beatinsong, beatinphrase, beatfraction = [], [], []
    n_first = s.notesAndRests[0]
    if n_first.isNote:
        beatinsong.append(startbeat)
        beatinphrase.append(startbeat)
        duration_beatfraction = Fraction(n_first.duration.quarterLength) / Fraction(n_first.beatDuration.quarterLength)
        beatfraction.append(duration_beatfraction) # add first note here, use nextnote in loop
    cumsum_beat_song = startbeat
    cumsum_beat_phrase = startbeat
    note_ix = 0
    notesandrests = list(s.notesAndRests)
    for n, nextnote in zip(notesandrests, notesandrests[1:]):
        #print("--------------")
        #print(n)
        duration_beatfraction = Fraction(n.duration.quarterLength) / Fraction(n.beatDuration.quarterLength)
        cumsum_beat_song += duration_beatfraction
        cumsum_beat_phrase += duration_beatfraction
        #print(cumsum_beat_song)
        if n.isNote:
            if note_ix in phrasestart_ixs:
                cumsum_beat_phrase = Fraction(n.beat)
                #print('beat ', cumsum_beat_phrase)
                if cumsum_beat_phrase != Fraction(1): #upbeat
                    cumsum_beat_phrase = Fraction(-1 * n.getContextByClass('TimeSignature').beatCount) + cumsum_beat_phrase
                cumsum_beat_phrase = cumsum_beat_phrase - Fraction(1)
                #print(note_ix, n, cumsum_beat_phrase)
                beatinphrase[-1] = cumsum_beat_phrase
                cumsum_beat_phrase += duration_beatfraction
            #print(f'{n}, beat: {Fraction(n.beat)}, fraction: {duration_beatfraction}')
            #print("note: ", cumsum_beat_song)
            note_ix += 1
        if nextnote.isNote:
            beatinphrase.append(cumsum_beat_phrase)
            beatinsong.append(cumsum_beat_song)
            duration_beatfraction = Fraction(nextnote.duration.quarterLength) / Fraction(nextnote.beatDuration.quarterLength)
            beatfraction.append(duration_beatfraction)
    beatinsong = [str(f) for f in beatinsong] #string representation to make it JSON serializable
    beatinphrase = [str(f) for f in beatinphrase] #string representation to make it JSON serializable
    beatfraction = [str(f) for f in beatfraction] #string representation to make it JSON serializable
    return beatinsong, beatinphrase, beatfraction

#Beat Strength and Beat Strength Fraction

def m21TOBeat_str(s):
    if not hasmeter(s):
        raise NoMeterError("No Meter")
    beats = []
    beat_fractions = []
    for n in s.notes:
        try:
            b, bfr = beatStrTOtuple(n.beatStr)
        except m21.base.Music21ObjectException: #no time signature
            b, bfr = '0', '0'
        beats.append(b)
        beat_fractions.append(bfr)
    return beats, beat_fractions

def beatStrTOtuple(bstr):
    bstr_splitted = bstr.split(' ')
    if len(bstr_splitted) == 1:
        bstr_splitted.append('0')
    return bstr_splitted[0], bstr_splitted[1]

#Beat Float (?)

def m21TOBeat_float(s):
    if not hasmeter(s):
        raise NoMeterError("No Meter")
    beats = []
    for n in s.notes:
        try:
            beat_float = float(n.beat)
        except m21.base.Music21ObjectException: #no time signature
            beat_float = 0.0
        beats.append(beat_float)
    return beats

#Onset Tick: differs from github (without JSON calling)

def gcd_list(list):
    return reduce(gcd, list)

def lcm_list(list):
    return reduce(lcm, list)

def fraction_gcd(duration_list):
    num_dur = []
    den_dur = []
    for dur in duration_list:
        num_dur.append(Fraction(dur).numerator)
        den_dur.append(Fraction(dur).denominator)
    
    return Fraction(gcd_list(num_dur), lcm_list(den_dur))

def m21TOOffsets(s):
    offsets = [n.offset for n in s.notes]
    offToPrint = [str(o) for o in offsets]
    return offsets, offToPrint

def m21TOOnsetTick(offsets):
    
    gcd = fraction_gcd(offsets)
    onset = [int(o//gcd) for o in offsets]
    
    return onset
    
#Song Position

def getSongPos(onsettick):
    onsets = np.array(onsettick)
    return list(onsets / onsets[-1])

#Next Is Rest
def m21TONextIsRest(s):
    notesandrests = list(s.notesAndRests)
    nextisrest = [ nextnote.isRest for note, nextnote in zip(notesandrests, notesandrests[1:]) if note.isNote]
    if notesandrests[-1].isNote:
        nextisrest.append(None) #final note
    return nextisrest

#Rest Duration Fraction

def m21TORestDuration_frac(s):
    restdurations = []
    notesandrests = list(s.notesAndRests)
    rest_duration = Fraction(0)
    #this computes length of rests PRECEEDING the note
    for event in notesandrests:
        if event.isRest:
            rest_duration += Fraction(event.duration.quarterLength)
        if event.isNote:
            if rest_duration == 0:
                restdurations.append(None)
            else:
                restdurations.append(str(rest_duration))
            rest_duration = Fraction(0)
    #shift list and add last
    if notesandrests[-1].isNote:
        restdurations = restdurations[1:] + [None]
    else:
        restdurations = restdurations[1:] + [str(rest_duration)]
    return restdurations

#Phrase IX

def getPhraseIx(phrasepos):
    current = 0
    phr_ix = []
    for pp in zip(phrasepos,phrasepos[1:]):
        if pp[1] < pp[0]:
            current += 1
        phr_ix.append(current)
    return [0]+phr_ix

#Phrase Position

def getPhrasePos(s, phrases, filename):
    phrasepos = []
    notes = list(s.notes)
    last0Index = 0
    phrase_dur = 0
    inPhrase = False
    noPhrases = False
    i = 0
    indexes = []
    
    if phrases:
        noPhrases = False
        indexes = list(phrases)
    if not phrases or (phrases[indexes[i]]['start'] == None):
        noPhrases = True
        print("Song without phrases defined")
        f = open("Sem Frases.txt", "a")
        f.write(filename + " ")
        f.write('\n')
        f.close()

        #Debugging
        #print(startID)
        #print(endID)
    if noPhrases == True:
        for note in notes:
            phrasepos.append(phrase_dur) 
            phrase_dur += float(note.duration.quarterLength)
            
        for j in range(len(phrasepos)):
            phrasepos[j] = round(phrasepos[j]/phrasepos[-1], 6)
    else:
        startID = phrases[indexes[i]]['start'][1:]
        endID = phrases[indexes[i]]['end'][1:]
        
        for note in notes:
            noteID = note.id
            #print(noteID)
            if(startID == noteID and inPhrase == False) or (inPhrase == False):
                phrase_dur = 0
                inPhrase = True
                last0Index = len(phrasepos)
                
            if(inPhrase == True):      
                phrasepos.append(phrase_dur)
                
            if(endID == noteID):
                inPhrase = False
                i+=1
                
                if i < len(indexes):
                    startID = phrases[indexes[i]]['start'][1:]
                    endID = phrases[indexes[i]]['end'][1:]
                
                for j in range(last0Index, len(phrasepos)):
                    if phrasepos[-1] != 0:
                        phrasepos[j] = round(phrasepos[j]/phrasepos[-1], 6)
            
            phrase_dur += float(note.duration.quarterLength)
    
    #Debugging
    #print(phrasepos)        
    
    return phrasepos

#Phrase End
def getPhraseEnd(phrasepos):
    return [x[1]<x[0] for x in zip(phrasepos, phrasepos[1:])] + [True]

#Beating Phrase End
def getBeatinphrase_end(beatinphrase, phrase_ix, beat):
    #find offset per phrase
    beatinphrase_end = []
    origin = defaultdict(lambda: 0.0)
    for ix in range(len(beatinphrase)):
        if abs(beat[ix] - 1.0) < epsilon:
            #print("Length of origin", len(origin))
            #print("Length of phrase_ix", len(phrase_ix))
            #print("Length of beatinphrase", len(beatinphrase))
            #print("ix: ", ix)
            #print("phrase_ix[ix]", phrase_ix[ix])
            origin[phrase_ix[ix]] = Fraction(beatinphrase[ix])
    for ix in range(len(beatinphrase)):
        beatinphrase_end.append( Fraction(beatinphrase[ix]) - Fraction(origin[phrase_ix[ix]]) )
    return [str(f) for f in beatinphrase_end]

#Lyrics

def hasLyrics(metadata):
    if metadata['lyrics'] == {}:
        return False
    else:
        return True
"""
def m21TOLyrics(s):
    dict_lyrics = s.lyrics()
    lyrics = []
    for l in dict_lyrics[1]:
            if (isinstance(l, m21.note.Lyric)):
                parsed_text = l.text.replace(u'\xa0', u' ')
                lyrics.append(parsed_text)
    return lyrics   
"""

# Not calculated due to being lyrical content:
    
#   Melisma State
#   Non Content Word
#   Word End
#   Word Stress
#   Phoneme
#   Rhymes
#   Rhyme Content Words





#Grouping Preference Rules as stated by Frankland and Cohen (2004)

#GPR 2a Frankland and Cohen

def getFranklandGPR2a(restduration):
    return [ min(1.0, float(Fraction(r) / 4.0)) if r is not None else None for r in restduration]

#GPR 2b Frankland and Cohen

def getOneFranklandGPR2b(n1,n2,n3,n4):
    return ( 1.0 - (float(n1+n3)/(2.0*n2)) ) if (n2>n3) and (n2>n1) else None

def getFranklandGPR2b(lengths, restdurations):
    quads = zip(lengths,lengths[1:],lengths[2:],lengths[3:])
    res =  [None] + [getOneFranklandGPR2b(n1, n2, n3, n4) for n1, n2, n3, n4 in quads] + [None, None]
    
    #check conditions (Frankland 2004, p.505): no rests in between, n2>n1 and n2>n3 (in getOneFranklandGPR2b())
    #rest_maks: positions with False result in None in res
    
    rest_present = [Fraction(r)>Fraction(0) if r is not None else False for r in restdurations]
    triple_rest_present = zip(rest_present,rest_present[1:],rest_present[2:])
    rest_mask = [False] + [not (r1 or r2 or r3) for r1, r2, r3 in triple_rest_present] + [False]
    
    #now set all values in res to None if False in mask
    res = [res[ix] if rest_mask[ix] else None for ix in range(len(res))]    
    return res
        
    
#GPR 3a Frankland and Cohen

def getOneFranklandGPR3a(n1, n2, n3, n4):
    if n2 != n3 and abs(n2-n3) > abs(n1-n2) and abs(n2-n3) > abs(n3-n4):
        return 1.0 - ( float(abs(n1-n2)+abs(n3-n4)) / float(2.0 * abs(n2-n3)) )
    else:
        return None

#The rule applies only if the transition from n2 to n3 is greater than from n1 to n2
#and from n3 to n4. In addition, the transition from n2 to n3 must be nonzero

def getFranklandGPR3a(midipitch):
    quads = zip(midipitch,midipitch[1:],midipitch[2:],midipitch[3:])
    return  [None] + [getOneFranklandGPR3a(n1, n2, n3, n4) for n1, n2, n3, n4 in quads] + [None, None]


#GPR 3d Frankland and Cohen

def getOneFranklandGPR3d(n1,n2,n3, n4):
    if n1 != n2 or n3 != n4:
        return None
    if n3 > n1:
        return 1.0 - (float(n1)/float(n3))
    else:
        return 1.0 - (float(n3)/float(n1))

#... to apply, the length of n1 must equal n2, and the length of n3 must euqal n4
def getFranklandGPR3d(lengths):
    quads = zip(lengths,lengths[1:],lengths[2:],lengths[3:])
    return [None] + [getOneFranklandGPR3d(n1, n2, n3, n4) for n1, n2, n3, n4 in quads] + [None, None]
    #condition checking in getOneFranklandGRP3d()


#GPR Sum Frankland and Cohen
    # done in the parameters section

#Local Boundary Detection Method    

#LBDM Boundary Strength

def getBoundaryStrength(rs, intervals):
    #print(list(zip(rs, intervals)))
    pairs = zip(rs[1:-1], rs[2:-1], intervals[1:])
    strength = [ c * (r1 + r2) for r1, r2, c in pairs]
    #very shor melodies:
    if len(strength) == 0:
        return [None, None, None]
    #normalize
    maxspitch = max(strength)
    if maxspitch > 0:
        strength = [s / maxspitch for s in strength]
    #Add first and last
    strength = [None] + strength + [None, None]
    return strength

#Cambouropoulos 2001
#Gives strength for boundary AFTER the note
def getLocalBoundaryStrength(spitch, sioi, srest):
    triplets = zip(spitch[1:-2], sioi[1:-2], srest[1:-2]) #remove None values at begin and end
    strength = [0.25*p + 0.5*i + 0.25*r for p, i, r in triplets]
    strength = [None] + strength + [None, None]
    return strength
    
#LBDM Strength of the Pitch Boundary

def getBoundaryStrengthPitch(rpitch, chromaticinterval, threshold=12):
    # we need absolute values
    # and thr_int <= threshold
    # and shift such that chormaticinterval is interval FOLLOWING note
    thr_int = [min(threshold,abs(i)) for i in chromaticinterval[1:]] + [None] 
    return getBoundaryStrength(rpitch, thr_int)

#LBDM Strength of the IOI Boundary

def getBoundaryStrengthIOI(rioi, ioi, threshold=4.0):
    #We need IOI AFTER the note, and we need maximize the value
    thr_ioi = [min(threshold,i) for i in ioi[:-1]] + [None]
    return getBoundaryStrength(rioi, thr_ioi)

#LBDM Strength of the Rest Boundary
        
def getBoundaryStrengthRest(rrest, restduration_frac, threshold=4.0):
    #need rest AFTER note, and apply threshold
    thr_rd = [min(threshold, float(Fraction(r))) if r is not None else 0.0 for r in restduration_frac[:-1]] + [None]
    return getBoundaryStrength(rrest, thr_rd)

#LBDM Degree of Change for the pitch interval

def getOneDegreeChange(x1, x2, const_add=0.0):
    res = None
    x1 += const_add
    x2 += const_add
    if x1 == x2: return 0.0
    if (x1+x2) != 0 and x1 >= 0 and x2 >= 0:
        res = float(abs(x1-x2)) / float (x1 + x2)
    return res

def getDegreeChangeLBDMpitch(chromaticinterval, threshold=12, const_add=1):
    # we need absolute values
    # and thr_int <= threshold
    # and shift such that chormaticinterval is interval FOLLOWING note
    thr_int = [min(threshold,abs(i)) for i in chromaticinterval[1:]] + [None] 
    pairs = zip(thr_int[:-1],thr_int[1:-1])
    rpitch = [None] + [getOneDegreeChange(x1, x2, const_add=const_add) for x1, x2 in pairs] + [None]
    return rpitch

#LBDM Degree of Change for the inter-onset interval following the note

def getDegreeChangeLBDMioi(ioi, threshold=4.0):
    #We need IOI AFTER the note, and we need maximize the value
    thr_ioi = [min(threshold,i) for i in ioi[:-1]] + [None]
    pairs = zip(thr_ioi[:-1],thr_ioi[1:-1])
    rioi = [None] + [getOneDegreeChange(x1, x2) for x1, x2 in pairs ] + [None]
    return rioi

#LBDM Degree of Change for the rest following the note

def getDegreeChangeLBDMrest(restduration_frac, threshold=4.0):
    #need rest AFTER note, and apply threshold
    thr_rd = [min(threshold, float(Fraction(r))) if r is not None else 0.0 for r in restduration_frac[:-1]] + [None]
    pairs = zip(thr_rd[:-1], thr_rd[1:-1])
    rrest = [None] + [getOneDegreeChange(x1, x2) for x1, x2 in pairs] + [None]
    return rrest

#Pitch Proximity
def getPitchProximity(chromaticinterval):
    return [None, None] + [abs(c) if abs(c) < 12 else None for c in chromaticinterval[2:] ]

#Pitch Reversal
# compute expectancy of the realized note modelled with pitch reversal (Schellenberg, 1997)
def getOnePitchReversal(implicative, realized):
    if abs(implicative) == 6 or abs(implicative) > 11 or abs(realized) > 12:
        return None
    
    pitchrev_dir = None
    if abs(implicative) < 6:
        pitchrev_dir = 0
    if abs(implicative) > 6 and abs(implicative) < 12:
        if realized * implicative <= 0:
            pitchrev_dir = 1
        else:
            pitchrev_dir = -1
    
    pitchrev_ret = 1.5 if ( (abs(realized)>0) and (realized*implicative < 0) and (abs(implicative+realized) <= 2) ) else 0

    return pitchrev_dir + pitchrev_ret

# compute expectancies of the note modelled with pitch reversal (Schellenberg, 1997)
def getPitchReversal(chromaticinterval):
    return [None, None] + [getOnePitchReversal(i, r) for i,r in zip(chromaticinterval[1:], chromaticinterval[2:])] 

# Fuction to get melody sequences
