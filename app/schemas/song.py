from pydantic import BaseModel

# add fields

class Technique(BaseModel):
    name: str
    difficulty: int

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

class SongAnalysisBATCH(BaseModel):
    songs: list[SongAnalysis]

class Song(BaseModel):
    rec_mbid: str | None = None
    song_name: str
    artist_name: str
    match: int | None = None # 0-100
    analysis: SongAnalysis | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Song):
            return NotImplemented
        if self.rec_mbid is not None and other.rec_mbid is not None:
            return self.rec_mbid == other.rec_mbid
        
        return (self.artist_name.strip().casefold() == other.artist_name.strip().casefold() and
                self.song_name.strip().casefold() == other.song_name.strip().casefold())



