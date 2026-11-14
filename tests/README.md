# Testing

Tests verify the implemented ERA5-Land EDA helpers and, as they are added, small scientific analysis calculations. The suite is offline-first and uses temporary test data. See [tests/AGENTS.md](AGENTS.md) for technical rules and the [project README](../README.md) for environment setup.

## Current structure

```text
tests/
├── AGENTS.md
├── README.md
└── test_data_loader.py
```

The loader tests cover both hourly and daily Parquet discovery, the configurable data root, and missing or empty input directories. Test fixtures are created in temporary directories; the real `data/all/` is not modified.

## Run the tests

From the project root, with the environment activated:

```bash
python -m pytest tests/test_data_loader.py -q
```

Run the full current suite:

```bash
python -m pytest tests -q
```

When a test modifies the loader's import path or behavior, run the tests **again** on that version. Passing output from an earlier version does not verify a refactor.

## Testing principles

- Keep fixtures small and deterministic; do not require the real large hourly dataset for routine tests.
- Include success and failure paths for file discovery and path configuration.
- Use explicit expected results for timestamp continuity, missing values, duplicates, grid coverage, and variable-specific scientific calculations when those features are added.
- Preserve original source data and manifests; never write test artifacts to `data/all/`.
- Add tests only when needed to protect behavior, rather than creating unused test folders or complicated abstractions.

## Definition of done

A change is complete when its targeted tests pass in a configured environment, the result is reported accurately, and relevant documentation and the Stage 1 checklist are updated. If required libraries are unavailable in the agent runtime, the user can run the documented command locally and provide the output for verification.
