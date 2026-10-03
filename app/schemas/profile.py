from pydantic import BaseModel

class GuitarProfile(BaseModel):
    experience_level: str # "Beginner" | "Intermediate" | "Advanced"
    solo_preference: str # "Rhythm" | "Lead" | "Balanced" | "Indifferent"
    techniques: list[str] # ["Fingerpicking", "Strumming", "Barre Chords", ...]
    learned_chords: list[str] # ["G", "C", ...]
    in_training_chords: list[str] # ["GMaj7", "F", ...]
    tuning_preferences: str # "EADGBE" | "Indifferent" | ...

"""
class SongAnalysis(BaseModel):
    tuning: str
    overall_difficulty: str # "Beginner" | "Intermediate" | "Advanced"
    solo_style: str # "Rhythm" | "Lead" | "Balanced"
    rhythm_difficulty: int
    lead_difficulty: int
    solo_difficulty: int
    tempo_difficulty: int
    required_chords: list[str]
    techniques: list[str]
    explanation: str
    confidence: float
"""