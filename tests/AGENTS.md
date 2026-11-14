# Tests — Agent Instructions

**Role: HOW TO TEST.** These instructions govern changes inside `tests/`. Follow [root AGENTS.md](../AGENTS.md), [the scientific specification](../docs/app_description.md), and [repository guidelines](../docs/repo_guidelines.md). The [tests README](README.md) owns **CURRENT TEST STRUCTURE / HOW TO RUN**, not agent instructions.

## 1. Production-first test design

**Every test must be justified by an existing production script, function, or explicit scientific contract. A test must not test its own imitation of an implementation.**

Before writing or changing a test:
1. Identify the **production entry point under test** (currently `utils/data_loader.py`), the behavior it promises, and the failure it should detect.
2. Invoke that real production entry point. Do not copy its algorithm into a helper and then assert that the copied algorithm works.
3. Use independently specified expected values and small fixtures; do not derive expected results from the same production computation being asserted.
4. Mock **only justified boundaries**, such as a DuckDB read call when unit-testing file selection. Never mock away the behavior being tested.
5. Do not invent a production API, feature, or abstract model solely to make a test exist. Implement a behavior first, then protect it with tests.
6. If the requirement is only planned and there is no code yet, keep its test in the implementation checklist instead of creating a test against a hypothetical implementation.

Keep tests readable, deterministic, and minimal. Use `pytest`, `tmp_path`, and `monkeypatch` where they improve isolation. Add a short module-level docstring naming the production contract.

## 2. Test levels and ownership

Organize tests **by level**:

```text
tests/
├── unit/
│   └── test_data_loader.py
└── integration/
    └── test_data_loader.py
```

**Unit tests** validate one production function or narrowly scoped decision in isolation: path resolution, filename filtering, errors, and other logic that does not need a real Parquet read. Mock collaborators only at legitimate external boundaries. A unit test should fail when the real function's behavior changes incorrectly.

**Integration tests** verify real interaction among implemented components, for example `utils.data_loader` + DuckDB + temporary Parquet files. Test both input resolutions, actual relation results, and read-only preservation. Integration fixtures remain **local and offline**; do not require the real study dataset, CDS access, or cloud storage.

Do not duplicate the same assertions across levels without a distinct purpose. Do not create additional levels or subdirectories without a real need.

## 3. Scientific data integrity

When scientific assessment logic exists, test its **real functions or reproducible notebook calculations**, using explicit tiny timestamps, grid points, and meteorological values.

- Distinguish absent records from NULL/NaN in present records.
- Check UTC hourly continuity and uniqueness of `(timestamp, latitude, longitude)`.
- Validate spatial coverage against the relevant configured grid; use smaller synthetic grids for focused algorithm tests.
- Respect ERA5-Land accumulated-variable semantics and units.
- Never infer sea locations solely from NULL/NaN or silently fill missing observations.
- Test findings and classifications against **independent evidence**, not an assertion copied from the computation itself.

Do not claim these tests exist before corresponding analysis code has been implemented.

## 4. Safety and verification

- Always use temporary directories and test files. **Never write to or overwrite `data/all/`**.
- Do not modify source Parquet or manifests; do not require live external services for routine tests.
- Run relevant unit tests first, then integration tests, then the full suite as appropriate.
- **When the agent runtime cannot execute DuckDB or PyArrow**, perform available static checks and ask the user to run the exact documented commands in their configured environment. Report any user-provided results as **user-run verification**. Previous passes do not prove a modified version of the code.
- A test passing is evidence only for the behavior it actually exercised. `--collect-only` and syntax checks are not test execution.
- Mark `todo/` checkboxes complete only after the appropriate work and verification; preserve any known pending checks.
- Keep changes small, review diffs, and commit only to `dev`.

**Core rule: Test production behavior, not test-created behavior.**
