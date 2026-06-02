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

### Public Calendar Diagnostics

Public calendars use TimeTree API v2 and do not require login:

```bash
uv run timetree-exporter --public-calendar -c rakuten_official \
  --developer-mode \
  --raw-output-dir raw-timetree/public \
  -o /tmp/rakuten_official.ics
```

Implementation notes:

- Public events are fetched from `/api/v2/public_calendars/{calendar_id}/public_events`.
- The request includes `from=0`; without it, TimeTree may return only a short default window.
- Public API responses use `public_events`, not `events`.
- Public events are normalized by `TimeTreePublicEvent`, which extends `TimeTreeEvent`.
- Public events may omit `uuid`, `type`, `category`, `alerts`, and `recurrences`.
- Public labels are synthesized from `public_calendar_label` because the private labels endpoint is not used.

Useful public calendar checks:

```bash
uv run pytest tests/test_calendar.py tests/test_event.py tests/test_main.py
uv run ruff check
```

## Before Opening A PR

Run these checks:

```bash
uv run pytest
uv run pre-commit run --all-files
```

## Roadmap of the properties mapping to iCal

Private TimeTree event fields:

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

Public TimeTree event fields:

- [x] **ID** → `UID`
- [x] **Title** → `SUMMARY`
- [x] **All Day** → all-day `DTSTART` / `DTEND`
- [x] **Start At** → `DTSTART`
- [x] **Start Timezone** → `DTSTART` timezone
- [x] **End At** → `DTEND`
- [x] **End Timezone** → `DTEND` timezone
- [x] **Created At** → `CREATED`
- [x] **Updated At** → `LAST-MODIFIED`
- [x] **URL** → `URL`
- [x] **Note** → `DESCRIPTION`
- [x] **Headline** → `DESCRIPTION`
- [x] **Overview** → `DESCRIPTION`
- [x] **Link URL** → `DESCRIPTION`
- [x] **Attachment OGP Title** → `DESCRIPTION`
- [x] **Attachment OGP Description** → `DESCRIPTION`
- [x] **Attachment OGP URL** → `DESCRIPTION`
- [x] **Location Name** → `LOCATION`
- [x] **Location Address** → `LOCATION`
- [x] **Location Latitude** → `GEO`
- [x] **Location Longitude** → `GEO`
- [x] **Location URL** → `DESCRIPTION`
- [x] **Public Calendar Label ID** → internal label grouping
- [x] **Public Calendar Label Name** → `CATEGORIES`
- [x] **Public Calendar Label Color** → `COLOR`
- [x] **Top-Level Color** → `COLOR` fallback
- [x] **Public Calendar Hashtags** → `CATEGORIES`
- [x] **Cover Image URLs** → `DESCRIPTION`
- [x] **Video URLs** → `DESCRIPTION`
- [ ] **Campaign**
- [ ] **Interest Count**
- [ ] **Publish At**
- [ ] **Until At**
- [ ] **Status**
- [ ] **Region Timezone**
- [ ] **Location Access**
- [ ] **Location Note**
- [ ] **Period Closed**
- [ ] **Period Note**
