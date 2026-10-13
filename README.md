# Fret Companion

**Find your next guitar song in the music you already listen to.**

Fret Companion is a web application that helps guitar players discover which songs from their ListenBrainz listening history fit their current skills and playing preferences. Create a guitar profile, explore your recent listens or top tracks, and build a collection of songs to learn.

## Features

- **Personal guitar profile** — Select your experience level, playing style, known chords, techniques, and preferred tuning. An optional chord builder makes it easy to add less common chords.
- **Your listening history** — Search by ListenBrainz username and explore recent listens or top tracks across different time ranges.
- **Guitar Match** — Compare each song's requirements with your profile using a deterministic, weighted Python scoring algorithm.
- **Detailed track cards** — View tuning, required chords, and techniques at a glance. Expand a card for rhythm, lead, solo, and tempo difficulty, along with analysis notes.
- **Saved tracks** — Save and unsave songs to keep a collection of tracks you want to revisit.
- **Sorting and tab search** — Sort results by highest match and open an Ultimate Guitar search for a song and artist.

## How it works

1. **Set up your profile.** Tell Fret Companion what you can play and how you prefer to play it.
2. **Find your music.** Retrieve recent listens or top tracks from ListenBrainz.
3. **Analyze guitar requirements.** Gemini generates structured song characteristics, which Pydantic validates and SQLAlchemy stores in SQLite for reuse.
4. **Calculate your match.** Python compares the song's difficulty, playing style, chords, techniques, and tuning with your profile to produce a Guitar Match percentage.
5. **Choose what to learn.** Explore the results, save interesting songs, and find tabs on Ultimate Guitar.

The AI estimates guitar requirements; the application's own scoring logic calculates the personalized match.

## Technology stack

| Area | Technologies |
| --- | --- |
| Backend | Python, Flask |
| Frontend | Jinja2, HTML, CSS, JavaScript |
| Validation | Pydantic |
| Database | SQLite, SQLAlchemy |
| Integrations | ListenBrainz API, Google Gemini, Requests, Google Gen AI SDK |
| Testing | pytest, mocked API responses |

## Project structure

- `app/routes.py` — Flask routes and page interactions.
- `app/api/` — ListenBrainz integration and structured song analysis.
- `app/schemas/` — Song, analysis, and guitar-profile models.
- `app/match_evaluation.py` — Guitar compatibility scoring.
- `app/database/` — Database models and track persistence.
- `app/templates/` — Jinja page templates.
- `app/static/` — Stylesheets and browser interactions.
- `tests/` — Tests for scoring, validation, song identity, and API handling.
