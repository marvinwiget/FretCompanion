# Structure and naming notes

## Responsibility of each layer

- `app/__init__.py` creates and configures the Flask application. It owns startup, not request handling.
- `app/routes.py` handles HTTP input, session state, error messages, and rendering. Its `pages` blueprint is registered by the factory.
- `app/services/search.py` coordinates listening retrieval, song conversion, deduplication, analysis, persistence, and scoring. It receives a profile as an argument rather than reading a browser session.
- `app/integrations/` communicates with external providers.
- `app/database/session.py` initializes and retrieves the engine for the current Flask application.
- `app/database/tracks.py` contains the existing SQLAlchemy queries and conversions into `Song` objects. Call these functions inside an application context.
- `app/schemas/` defines validated application data. `app/database/model.py` defines database tables.
- `app/templates/base.html` owns the shared HTML shell. `components/track_card.html` owns the shared song-card markup.

Keeping these files inside `app/` is conventional. There is no need to create a top-level package for every responsibility.

## Names changed in this refactor

| Previous name | New name | Reason |
| --- | --- | --- |
| `app/api/` | `app/integrations/` | These modules call external APIs; they do not define this application's HTTP API. |
| `listenbrainz_api.py` | `listenbrainz.py` | The containing package already establishes that this is an external integration. |
| `analyize_songs()` | `analyze_songs()` | Corrects a spelling mistake. |
| Queries in `database/session.py` | `database/tracks.py` | The filename now describes the track operations it contains. |

The blueprint gives endpoint names a `pages.` prefix, such as `pages.search`. Browser URLs are unchanged. Python imports and `url_for()` references were updated together.

## Existing names that are fine

`routes.py`, `services/search.py`, `exceptions.py`, `schemas/`, `templates/`, `static/`, and `tests/` are familiar Python/Flask names. `match_evaluation.py` is descriptive and does not need renaming. Snake case is conventional for Python modules and functions.

## Optional future naming cleanup

These names were retained to keep this change focused on moving existing code:

- `database/model.py`: `models.py` is a common convention, especially with several table classes. Singular is reasonable while it contains one table.
- `helper/chords.py`: the file is clear, but `helper` is broad. If this remains static chord data, `catalog/chords.py` would describe it more precisely. Avoid collecting unrelated code into a generic helpers directory.
- `schemas/literals.py`: technically accurate; `choices.py` could better communicate the domain values it contains. Neither requires changing now.
- `saved-tracks.html`: hyphens are valid in template names. `saved_tracks.html` would align with Python's naming style, but consistency matters more than this choice.
- `eva_songs`: `evaluated_songs` or `matched_songs` would be easier for a new reader to understand.
- `s` and `w_diff`: acceptable in short calculations; descriptive names help when functions grow.
- `load_tracks_with_id`: `load_tracks_by_ids` would describe the list argument more clearly.
- `song_name` and `track_name`: both are understandable, but using one term across schemas and persistence would reduce translation overhead.

No changes to table names, stored JSON fields, scoring weights, identity matching, or saved-track behaviour were included in this structural refactor.
