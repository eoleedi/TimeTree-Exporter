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
- Public API pagination uses `paging.next` and `paging.next_cursor`; when `next` is true, fetch the next page with `cursor=<next_cursor>`.
- Public events are normalized by `TimeTreePublicEvent`, which extends `TimeTreeEvent`.
- Public events may omit `uuid`, `type`, `category`, `alerts`, and `recurrences`.
- Public recurring events may provide a separate `until_at`; use it as RRULE `UNTIL` when the recurrence itself has no `UNTIL`.
- Public labels are read from public calendar metadata at `/api/v2/public_calendars/{calendar_id}`.
- Public event payloads still provide `public_calendar_label`, which is used as a fallback during export if metadata labels are unavailable.
- `--public-calendar --list-labels` reads metadata labels without fetching public events.

Useful public calendar checks:

```bash
uv run pytest tests/test_calendar.py tests/test_event.py tests/test_main.py
uv run ruff check
```

### Activity Endpoint (Comments)

When `--include-comments` is used, the exporter fetches event comments from a separate endpoint:

- Endpoint: `/api/v1/calendar/{calendar_id}/event/{event_id}/activities?since=0`
- This is not part of the event payload; it's a per-event API call
- Response includes `event_activities` array with comment text in `comment.body`, `attachment.content`, or other message fields
- Pagination is supported via `chunk: true` and `since: <timestamp>`
- Comment author names are resolved from `calendar_users` metadata and prefixed when available
- Default behavior (`--include-comments` off) skips these calls to avoid performance impact and rate-limit risk

## Before Opening A PR

Run these checks:

```bash
uv run pytest
uv run pre-commit run --all-files
```

## Roadmap of the properties mapping to iCal

Private TimeTree event fields:

- [ ] ~~**ID**~~ (Not mapped to `UID`; TimeTree internal/API object id, used only for API lookups such as `parent_id` resolution)
- [ ] ~~**Primary ID**~~ (Not mapped; no clear iCalendar equivalent)
- [ ] ~~**Calendar ID**~~ (Not mapped on each `VEVENT`; the selected calendar becomes the exported `VCALENDAR`)
- [x] **UUID** -> `UID`; private event exports intentionally use `uuid`, not `id`, for stable iCalendar identity
- [x] **Category** -> export behavior; memo events are skipped, normal events are exported
- [x] **Type** -> export behavior; birthday events are skipped, normal events are exported
- [ ] ~~**Author ID**~~ (Not mapped; `ORGANIZER` and RFC 9073 `PARTICIPANT` require a calendar address or contact metadata, not only an internal TimeTree ID)
- [ ] ~~**Author Type**~~ (Not mapped; no clear iCalendar equivalent without author contact metadata)
- [x] **Title** -> `SUMMARY`
- [x] **All Day** -> all-day `DTSTART;VALUE=DATE` / `DTEND;VALUE=DATE`; all-day `DTEND` is exclusive
- [x] **Start At** -> `DTSTART`
- [x] **Start Timezone** -> `DTSTART;TZID=...` for non-UTC timed events
- [x] **End At** -> `DTEND`
- [x] **End Timezone** -> `DTEND;TZID=...` for non-UTC timed events
- [x] **Label ID** -> label metadata lookup for `CATEGORIES` and `COLOR`
- [x] **Location** -> `LOCATION`
- [x] **Location Latitude** -> `GEO`
- [x] **Location Longitude** -> `GEO`
- [x] **URL** -> `URL`
- [x] **Note** -> `DESCRIPTION`
- [ ] **Lunar** -> possible RFC 7529 `RRULE` `RSCALE=...` / `SKIP=...` for lunar or other non-Gregorian recurrence rules; requires confirming TimeTree lunar recurrence semantics
- [ ] **Attendees** -> possible `ATTENDEE` with params such as `CN`, `CUTYPE`, `ROLE`, `PARTSTAT`, `RSVP`, and RFC 7986 `EMAIL`; requires usable calendar-user addresses
- [x] **Recurrences** -> `RRULE`, `RDATE`, or `EXDATE`; recurrence parameters are preserved, and date-only timed-event `RRULE` `UNTIL` values are converted to UTC end-of-day
- [x] **Recurring UUID** -> `RELATED-TO` when present; this is the recurring master event `uuid` for detached recurrence instances and matches the exported parent `UID`; possible future `RECURRENCE-ID` support when paired with the master's `EXDATE`/original occurrence timestamp
- [x] **Alerts** -> `VALARM` with `ACTION:DISPLAY`, `DESCRIPTION:Reminder`, and relative `TRIGGER`
- [x] **Parent ID** -> internal parent lookup fallback for `RELATED-TO`; for detached recurrence instances this is the recurring master event `id`, while `recurring_uuid` is the master `uuid` used by iCalendar `UID`
- [ ] ~~**Link Object ID**~~ (Not mapped; currently observed as `null`; frontend stores it as `link_object_id` but does not appear to use it for event relationships)
- [ ] ~~**Link Object ID String**~~ (Not mapped; frontend field is `link_object_id_string`; no observed non-empty payloads or current frontend relationship behavior)
- [ ] ~~**Row Order**~~ (Ignore since it's a property for timetree notes)
- [ ] **Attachment** -> possible `ATTACH;VALUE=URI`, `ATTACH;FMTTYPE=...;ENCODING=BASE64;VALUE=BINARY`, or RFC 9073 `STRUCTURED-DATA` with `VALUE`, `FMTTYPE`, and `SCHEMA` params
- [ ] ~~**Like Count**~~ (Not mapped; social metric has no iCalendar equivalent)
- [ ] **Files** -> possible repeated `ATTACH;VALUE=URI` or binary `ATTACH` with `FMTTYPE`, `ENCODING=BASE64`, and `VALUE=BINARY`
- [ ] **Deactivated At** -> possible future sync-state tombstone handling after initial sync, such as web client updates from `/api/v1/calendar/{calendar_id}/events`; not a normal ICS event property
- [ ] ~~**Pinned At**~~ (Not mapped; TimeTree-specific UI metadata)
- [x] **Updated At** -> `LAST-MODIFIED`
- [x] **Created At** -> `CREATED`

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
- [x] **URL** → `SOURCE`
- [x] **Note** → `DESCRIPTION`
- [ ] ~~**Headline**~~ (Not mapped; observed public calendars leave it empty, and `SUMMARY` already uses `title`)
- [ ] ~~**Overview**~~ (Not mapped; observed public calendars leave it empty, and `DESCRIPTION` uses `note`)
- [x] **Link URL** → `URL`
- [ ] ~~**Attachment OGP Title**~~ (Not mapped; no clear iCalendar property beyond duplicating `SUMMARY`/`DESCRIPTION`)
- [ ] ~~**Attachment OGP Description**~~ (Not mapped; no clear iCalendar property beyond duplicating `DESCRIPTION`)
- [ ] ~~**Attachment OGP URL**~~ (Not mapped; `link_url` already maps to `URL`)
- [x] **Location Name** → `LOCATION`
- [x] **Location Address** → `LOCATION`
- [x] **Location Latitude** → `GEO`
- [x] **Location Longitude** → `GEO`
- [x] **Location URL** → `LOCATION;ALTREP`
- [x] **Public Calendar Label ID** → internal label grouping
- [x] **Public Calendar Label Name** → `CATEGORIES`
- [x] **Public Calendar Label Color** → `COLOR`
- [x] **Top-Level Color** → `COLOR` fallback
- [x] **Public Calendar Hashtags** → `CATEGORIES`
- [x] **Cover Image URLs** → `IMAGE;DISPLAY=FULLSIZE`
- [x] **Cover Thumbnail Image URLs** → `IMAGE;DISPLAY=THUMBNAIL`
- [x] **Video URLs** → `DESCRIPTION`
- [ ] ~~**Campaign**~~ (Not mapped; TimeTree campaign metadata has no clear iCalendar equivalent)
- [ ] ~~**Interest Count**~~ (Not mapped; social metric has no iCalendar equivalent)
- [ ] ~~**Publish At**~~ (Not mapped; publication metadata is not the event schedule)
- [ ] ~~**Until At**~~ (Not mapped; public events use it as a broad event/recurrence horizon, and RFC 5545 allows unbounded `RRULE`s)
- [ ] ~~**Status**~~ (Not mapped; TimeTree-specific publication/status metadata)
- [ ] ~~**Region Timezone**~~ (Not mapped; event times use `start_timezone` and `end_timezone`)
- [ ] ~~**Location Access**~~ (Not mapped; no clear iCalendar property or parameter)
- [ ] ~~**Location Note**~~ (Not mapped; no clear iCalendar property without mixing it into `DESCRIPTION`)
- [ ] ~~**Period Closed**~~ (Not mapped; no clear iCalendar property or parameter)
- [ ] ~~**Period Note**~~ (Not mapped; no clear iCalendar property without mixing it into `DESCRIPTION`)

Observed public calendars such as `rakuten_official` and `niigatacity` usually leave `headline` and `overview` empty and put event details in `note`. Public event `DESCRIPTION` is therefore sourced from `note` only, with video URLs appended when present.

`until_at` is present on public one-off events as well as recurring events, so it is not mapped. Public calendars also use 60-year `until_at` horizons for recurring events that have no explicit end date. RFC 5545 allows unbounded `RRULE`s, so these are exported without synthesizing an `UNTIL`.
