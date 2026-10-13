# Tests

Run from the repository root with the virtual environment active:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest tests -v
node --test tests/test_search_loading.cjs
```

`conftest.py` uses `create_app()` to create a fresh application with a test signing key and a temporary SQLite database for each test that needs it. The fixture also provides an application context for track queries. No import-time database patching is needed.

HTTP requests are blocked unless explicitly mocked. Provider tests import `app.integrations`; route tests replace the provider functions used by `app.services.search`. No real API keys, paid requests, or application database access are required.

Tests cover scoring, schema validation, song identity, ListenBrainz HTTP and payload failures, AI transport and batch validation, search error messages, result restoration, session bookmarks, session signing, and database round trips. JavaScript tests exercise search loading and browser-history restoration with a minimal DOM stub.
