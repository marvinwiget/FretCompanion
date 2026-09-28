from pydantic import BaseModel

# add fields

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

class SongAnalysisBATCH(BaseModel):
    songs: list[SongAnalysis]

class Song(BaseModel):
    song_name: str
    artist_name: str
    analysis: SongAnalysis | None = None



