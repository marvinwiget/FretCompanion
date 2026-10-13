# Fret Companion

**Find your next guitar song in the music you already listen to.**

Fret Companion helps guitar players discover songs from their ListenBrainz listening history that fit their current skills and playing preferences. Create a guitar profile, explore recent listens or top tracks, and save songs you want to learn.

## Features

- **Guitar profile:** Choose your experience level, playing style, known chords, techniques, and preferred tuning.
- **Chord picker:** Browse common chords, show sharps and flats, or use the compact builder to add another chord.
- **Listening history:** Search a ListenBrainz username for recent listens or top tracks across different time ranges.
- **Guitar analysis:** View estimated chords, tuning, techniques, and rhythm, lead, solo, and tempo difficulty.
- **Personalized Guitar Match:** A deterministic Python algorithm compares song requirements with your profile.
- **Reusable analyses:** SQLAlchemy stores song analyses in SQLite so cached tracks can be reused in later searches.
- **Saved tracks:** Save and unsave songs, with selections held in your browser's Flask session.
- **Track details:** Expand song cards, sort results by match, and open an Ultimate Guitar search.

## Technology stack

| Area | Technologies |
| --- | --- |
| Backend | Python, Flask |
| Pages | Jinja2, HTML, CSS, JavaScript |
| Validation | Pydantic |
| Database | SQLite, SQLAlchemy |
| Listening data | ListenBrainz API, Requests |
| Guitar analysis | Google Gemini, Google Gen AI SDK |
| Testing | pytest, Node.js built-in test runner |

## How the application works

1. The browser submits the search form to Flask.
2. The route validates the input and reads the guitar profile from the session.
3. The search service fetches ListenBrainz data and converts it into `Song` models.
4. Database queries look for existing tracks, using recording IDs and metadata.
5. Songs without cached records are deduplicated and sent for guitar analysis.
6. Pydantic validates the complete analysis batch before it is saved to SQLite.
7. Python calculates Guitar Match percentages using the guitar profile.
8. The route stores the result IDs in the session and renders the search page.

The AI estimates the song's guitar requirements. Python calculates the personalized match using difficulty, playing style, chords, techniques, and tuning.

SQLite stores track identities and reusable analyses. The Flask session stores the guitar profile, saved track IDs, and previous search result IDs. When a page loads those tracks again, match scores are recalculated using the current profile.

## Project structure

```text
app/
├── __init__.py             # Application factory and configuration
├── routes.py               # HTTP requests, sessions, responses, and page rendering
├── exceptions.py           # Application-specific exceptions
├── match_evaluation.py     # Guitar Match calculation
├── services/
│   └── search.py           # Fetch → cache lookup → analysis → persistence → scoring
├── integrations/
│   ├── listenbrainz.py     # ListenBrainz requests and response checks
│   └── song_analysis.py    # Gemini prompt, request, and response validation
├── database/
│   ├── model.py            # SQLAlchemy table definitions
│   ├── session.py          # Database engine setup and access
│   └── tracks.py           # Track queries and persistence
├── schemas/
│   ├── song.py             # Song and guitar-analysis models
│   ├── profile.py          # Guitar-profile model
│   └── literals.py         # Allowed values for model fields
├── helper/
│   └── chords.py           # Chord roots and chord types
├── templates/
│   ├── base.html           # Shared page layout and navigation
│   ├── components/
│   │   └── track_card.html # Shared Search/Saved track card
│   ├── home.html
│   ├── profile.html
│   ├── search.html
│   └── saved-tracks.html
└── static/
    ├── css/
    └── js/
tests/                      # Python tests and JavaScript tests
.env.example                # Configuration template
requirements.txt            # Application dependencies
requirements-dev.txt        # Application and test dependencies
```

`create_app()` configures Flask, initializes the database, and registers the page routes. Routes are grouped in the `pages` blueprint; the browser URLs remain `/`, `/guitar-profile`, `/search`, and `/saved-tracks`.

## Installation

### 1. Open the project

Clone or download this repository, then open a terminal in its root directory—the folder containing this README and `requirements.txt`.

Use Python 3.12 or newer. The test suite has been run with Python 3.14. Node.js 18 or newer is needed only for the JavaScript tests. SQLite is included with Python; no separate database server is required.

### 2. Create a virtual environment

On macOS or Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the application and test dependencies:

```sh
python -m pip install -r requirements-dev.txt
```

For application dependencies only, use `requirements.txt` instead.

### 3. Configure the application

For a new installation, copy `.env.example` to `.env`. Keep your existing `.env` when updating the project.

On macOS or Linux:

```sh
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Generate a Flask signing key once:

```sh
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the generated value into `FLASK_SECRET_KEY` in `.env`, and enter your Gemini API key:

```dotenv
FLASK_SECRET_KEY=your-generated-value
GEMINI_API_KEY=your-gemini-api-key
```

Keep the same `FLASK_SECRET_KEY` across application restarts so existing session cookies remain valid. Public ListenBrainz lookups use a username and do not require a ListenBrainz API key.

| Variable | Purpose | Default |
| --- | --- | --- |
| `FLASK_SECRET_KEY` | Signs Flask session cookies | Required |
| `GEMINI_API_KEY` | Authenticates new guitar-analysis requests | Set your own key |
| `DATABASE_URL` | SQLAlchemy database URL | SQLite file `fret_companion.db` in the project root |

The database file and missing tables are created automatically when the application starts. An existing database at the default location is reused.

To choose another SQLite location, set an absolute path, for example:

```dotenv
DATABASE_URL=sqlite+pysqlite:////absolute/path/fret_companion.db
```

### 4. Start the development server

From the repository root, with the virtual environment activated:

```sh
python -m flask --app app run
```

Open **http://127.0.0.1:5000** in your browser.

Flask discovers `create_app()` in the `app` package. This replaces the previous `flask --app app/routes run` command.

For automatic reloads during local development:

```sh
python -m flask --app app run --debug
```

### 5. Use Fret Companion

1. Open **Guitar Profile**, choose your preferences, and save.
2. Open **Search** and enter your ListenBrainz username.
3. Choose recent listens or top tracks, then submit the form.
4. Explore matches, expand the details, and save tracks you want to revisit.
5. Open **Saved** to return to your collection.

## Running tests

Run the Python suite from the project root:

```sh
python -m pytest
```

For individual test names or a single test file:

```sh
python -m pytest -v
python -m pytest tests/test_routes.py -v
```

Run the JavaScript tests:

```sh
node --test tests/test_search_loading.cjs
```

Tests use mocked integrations, test session keys, and temporary SQLite databases. Coverage includes scoring, model validation, provider failures, caching, route responses, saved tracks, sessions, and search loading behaviour.

See [tests/README.md](tests/README.md) for the test setup and [docs/structure.md](docs/structure.md) for organization and naming notes.
