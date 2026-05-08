# Development

## Setup

Install dependencies with `uv`:

```bash
uv sync --dev
```

### Pre-Commit

Install the git hooks:

```bash
uv run pre-commit install
```

Run all hooks manually:

```bash
uv run pre-commit run --all-files
```

The hooks run Ruff linting and formatting for Python files, plus basic whitespace, EOF, and YAML checks.

## Test

Run the test suite:

```bash
uv run pytest
```

## Run Locally

Run the CLI from the working tree:

```bash
uv run timetree-exporter
```

Useful environment variables:

- `TIMETREE_EMAIL`: TimeTree account email.
- `TIMETREE_PASSWORD`: TimeTree account password.
- `TIMETREE_EXPORTER_DEVELOPER=1`: Enable raw API response output for diagnostics.

## Developer Diagnostics

> [!Note]
> These raw responses are particularly useful to develop new mappings and debugging.

Use `--developer-mode` to write raw TimeTree API responses to `raw-timetree/`.

Use `--raw-output-dir <dir>` to write raw responses to a custom directory.

## Before Opening A PR

Run these checks:

```bash
uv run pytest
uv run pre-commit run --all-files
```

## Roadmap of the properties mapping to iCal

- [ ] **ID**
- [ ] **Primary ID**
- [ ] **Calendar ID**
- [x] **UUID**
- [x] **Category**
- [x] **Type**
- [ ] **Author ID**
- [ ] **Author Type**
- [x] **Title**
- [x] **All Day**
- [x] **Start At**
- [x] **Start Timezone**
- [x] **End At**
- [x] **End Timezone**
- [x] **Label ID**
- [x] **Location**
- [x] **Location Latitude**
- [x] **Location Longitude**
- [x] **URL**
- [x] **Note**
- [ ] **Lunar**
- [ ] **Attendees**
- [x] **Recurrences**
- [ ] **Recurring UUID**
- [x] **Alerts**
- [x] **Parent ID**
- [ ] **Link Object ID**
- [ ] **Link Object ID String**
- [ ] ~~**Row Order**~~ (Ignore since it's a property for timetree notes)
- [ ] **Attachment**
- [ ] **Like Count**
- [ ] **Files**
- [ ] **Deactivated At**
- [ ] **Pinned At**
- [x] **Updated At**
- [x] **Created At**
