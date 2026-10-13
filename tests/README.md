Run from the project root with your virtual environment activated:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest tests -v
```

The fixtures in `conftest.py` create fresh sample models for each test. Tests cover scoring, model validation, song identity, and ListenBrainz clients with fake HTTP responses. They do not need an API key or modify the local database.

Two regression tests currently expose scoring bugs: no required techniques causes division by zero, and duplicate known chords inflate compatibility. These tests express the intended behavior and should pass after those bugs are fixed. They are deliberately not skipped or marked as expected failures.

The existing empty `test_database.py` and `test_routes.py` files are left for future integration tests. Use a temporary database for those, rather than `fret_companion.db`.
