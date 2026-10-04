
def get_roots():
    return ["A", "B", "C", "D", "E", "F", "G"]

def get_chord_types():
    return [
        {"suffix": "", "label": "Major"},
        {"suffix": "m", "label": "Minor"},
        {"suffix": "7", "label": "Dominant 7"},
        {"suffix": "m7", "label": "Minor 7"},
        {"suffix": "maj7", "label": "Major 7"},
        {"suffix": "sus2", "label": "Sus2"},
        {"suffix": "sus4", "label": "Sus4"},
        {"suffix": "5", "label": "Power chord"},
    ]