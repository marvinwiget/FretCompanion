from pydantic import BaseModel, Field

from .literals import Tuning, ExperienceLevel, PlayingStyle, Technique


class SongAnalysis(BaseModel):
    tuning: Tuning
    overall_difficulty: ExperienceLevel
    playing_style: PlayingStyle
    rhythm_difficulty: int = Field(ge=1, le=10)
    lead_difficulty: int = Field(ge=1, le=10)
    solo_difficulty: int = Field(ge=1, le=10)
    tempo_difficulty: int = Field(ge=1, le=10)
    required_chords: list[str]
    main_techniques: list[Technique]
    other_techniques: list[str]
    explanation: str
    confidence: float = Field(ge=0, le=1)

class SongAnalysisBatch(BaseModel):
    songs: list[SongAnalysis]

class Song(BaseModel):
    id: int | None = None
    rec_mbid: str | None = None
    song_name: str
    artist_name: str
    match: int | None = Field(default=None, ge=0, le=100)
    analysis: SongAnalysis | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Song):
            return NotImplemented
        if self.rec_mbid is not None and other.rec_mbid is not None:
            return self.rec_mbid == other.rec_mbid
        
        return (self.artist_name.strip().casefold() == other.artist_name.strip().casefold() and
                self.song_name.strip().casefold() == other.song_name.strip().casefold())



