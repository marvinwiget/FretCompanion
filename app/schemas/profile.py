from pydantic import BaseModel

class Preference(BaseModel):
    id: int
    experience_level: str #"beginner" | "intermediate" | "advanced"
    solo_preference: str #"rhythm" | "lead" | "balanced"
    skills: str
    tuning_preferences: str
    updated_at: str