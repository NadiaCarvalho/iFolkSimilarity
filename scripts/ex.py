from MelodicOccurrences.music_representations import extract_melodies_from_corpus

if __name__ == '__main__':
    mel_dict = extract_melodies_from_corpus('eval_data/MTCFeatures/krn/', [{'filename': 'NLB015569_01', 'tunefamily_id': 'O_God_ik_leef_in_nood'}])
    for i in mel_dict[0]['symbols']:
        print(i)