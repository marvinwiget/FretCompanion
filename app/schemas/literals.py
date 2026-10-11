from typing import Literal

ExperienceLevel = Literal["Beginner", "Intermediate", "Advanced"]

PlayingStyle = Literal["Rhythm", "Lead", "Balanced"]
PlayingStylePreference = Literal["Rhythm", "Lead", "Balanced", "Indifferent"]

Tuning = Literal[
    "EADGBE",        # Standard
    "DADGBE",        # Drop D
    "EbAbDbGbBbEb",  # Half-step down
    "DGCFAD",        # D standard
    "CGCFAD",        # Drop C
    "DGDGBD",        # Open G
    "DADF#AD",       # Open D
    "EBEG#BE",       # Open E
    "EAEAC#E",       # Open A
    "DADGAD",
    "Other",
    "Unknown",
    "Indifferent",
]

Technique = Literal[
    "Fingerpicking",
    "Strumming",
    "Hammer-on",
    "Pull-off",
    "Bending",
    "Slides",
    "Palm muting",
    "Tapping",
]