from app.schemas.song import Song, SongAnalysis
from app.schemas.profile import GuitarProfile

def evaluate_match(songs: list[Song], user: GuitarProfile):
    
    for song in songs:
        s = song.analysis

        # weight calculation
        w_diff = get_diff_weight(s, user)
        w_style = get_style_weight(s, user)
        w_chords = get_chords_weight(s, user)
        w_tech = get_technique_weight(s,user)
        w_tuning = get_tuning_weight(s, user)
        w_learn = get_learning_chords_weights(s, user)

        # calculate match for each song based on weights
        song.match = 100 - (
            20 * w_diff +
            20 * w_style + 
            25 * w_chords +
            15 * w_tech + 
            20 * w_tuning
        )
        song.match += 20 * w_learn # if there are chords in song the user wants to learn, increase match
        if song.match > 100: song.match = 100 # cap on 100% match, this case only possible with learning chords

    return songs


def get_diff_weight(s: SongAnalysis, user: GuitarProfile) -> float:

    if user.experience_level == "Beginner":
        if s.overall_difficulty == "Beginner": return 0
        if s.overall_difficulty == "Intermediate": return 0.5
        return 1

    if user.experience_level == "Intermediate":
        if s.overall_difficulty == "Beginner": return 0
        if s.overall_difficulty == "Intermediate": return 0
        return 0.5

    return 0 # case: user is advanced

def get_style_weight(s: SongAnalysis, user: GuitarProfile) -> float:

    if user.solo_preference == "Rhythm":
        if s.solo_style == "Rhythm": return 0
        if s.solo_style == "Balanced": return 0.5
        return 1
    if user.solo_preference == "Lead":
        if s.solo_style == "Lead": return 0
        if s.solo_style == "Balanced": return 0.5
        return 1

    if user.solo_preference == "Balanced":
        if s.solo_style == "Balanced": return 0
        return 0.5

    return 0 # case: user is indifferent 

def get_chords_weight(s: SongAnalysis, user: GuitarProfile) -> float:
    n_req_chords = len(s.required_chords)
    n_available_chords = 0

    for chord in user.learned_chords:
        if chord in s.required_chords: 
            n_available_chords += 1

    return 1 - (n_available_chords / n_req_chords) # e.g. if all required chords from the song are learned, return 0

def get_technique_weight(s: SongAnalysis, user: GuitarProfile) -> float: 
    n_req_tech = len(s.techniques)
    n_available_tech = 0

    for tech in s.techniques:
        if tech in user.techniques:
            n_available_tech += 1

    return 1 - (n_available_tech / n_req_tech) # e.g. if all required techniques from the song are learned, return 0

def get_tuning_weight(s: SongAnalysis, user: GuitarProfile) -> float:

    if user.tuning_preferences == s.tuning: return 0 # matching tuning
    elif user.tuning_preferences == "Indifferent": return 0 # indifferent to tuning
    return 1 # unwanted tuning

def get_learning_chords_weights(s: SongAnalysis, user: GuitarProfile) -> float: # this weight will be added (NOT SUBTRACTED)
    n_req_chords = len(s.required_chords)
    n_available_chords = 0

    for chord in user.in_training_chords:
        if chord in s.required_chords: 
            n_available_chords += 1

    if n_available_chords == 0: return 0
    if n_available_chords == 1: return 0.5
    if n_available_chords == 2: return 0.75
    if n_available_chords == 3: return 0.9
    return 1 # the higher the weight, the higher the match
