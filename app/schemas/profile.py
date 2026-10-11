from pydantic import BaseModel

from .literals import ExperienceLevel, PlayingStylePreference, Technique, Tuning

class GuitarProfile(BaseModel):
    experience_level: ExperienceLevel
    playing_style_preference: PlayingStylePreference
    techniques: list[Technique]
    learned_chords: list[str] 
    in_training_chords: list[str]
    tuning_preference: Tuning