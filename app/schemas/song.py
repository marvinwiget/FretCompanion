from pydantic import BaseModel

class Technique(BaseModel):
    name: str
    difficulty: int

class SongAnalysis(BaseModel):
    tuning: str
    overall_difficulty: int
    rhythm_difficulty: int
    lead_difficulty: int
    solo_difficulty: int
    tempo_difficulty: int
    required_chords: list[str]
    techniques: list[Technique]
    explanation: str
    confidence: float

class Song(BaseModel):
    song_name: str
    artist_name: str
    analysis: SongAnalysis | None = None


