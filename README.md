# TimeTree Exporter

[![PyPI](https://img.shields.io/pypi/v/timetree-exporter.svg)](https://pypi.org/project/timetree-exporter/)
[![Python 3.x](https://img.shields.io/pypi/pyversions/timetree-exporter.svg?logo=python&logoColor=white)](https://pypi.org/project/timetree-exporter/)
[![License](https://img.shields.io/github/license/eoleedi/TimeTree-Exporter)](https://github.com/eoleedi/TimeTree-Exporter/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/timetree-exporter)](https://pypistats.org/packages/timetree-exporter)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-orange.svg?logo=buymeacoffee&logoColor=white)](https://www.buymeacoffee.com/eoleedi)

A Tool for Exporting TimeTree Calendar and Converting to iCalendar Format (.ics) ([RFC 5545](https://datatracker.ietf.org/doc/html/rfc5545) compatible, with selected [RFC 7986](https://datatracker.ietf.org/doc/html/rfc7986) properties) \
This script works by scraping the TimeTree web app and converting the data to iCal format.
(The .ics file can then be imported into other calendar apps such as Google Calendar, Apple Calendar, Outlook Calendar, etc.)

> [!Warning]
> This is an independent, community-built project and is not affiliated with or endorsed by TimeTree, Inc.
> It uses unofficial, reverse-engineered TimeTree web APIs, which may change or stop working at any time without notice. As a result, the tool could break unexpectedly.
> Please use it responsibly—sending too many requests in a short period may lead to rate limiting, temporary blocks, or other restrictions from TimeTree.

## Installation

> [!Note]
> Timetree Exporter requires Python 3.10 or later.

If you are on mac, you can install it using brew:

```bash
brew install eoleedi/tap/timetree-exporter
```

You can also install it using uvx, pip, or pipx:

```bash
pip install timetree-exporter
```

## Usage

```bash
timetree-exporter -o path/to/output.ics
```

This will prompt you to enter your TimeTree email and password and select the calendar you want to export.

Then, you can import the ics file to your calendar app.

> [!Note]
>  💡 You are advised to import the ICS file into a separate calendar (e.g., Google Calendar) so that if anything goes wrong, you can simply delete the calendar and reimport it.

### Advanced Usage

- Specify your email address using the `-e` option.

    ```bash
    timetree-exporter -e email@example.com
    ```

- Specify the calendar code using the `-c` or `--calendar_code` option.

    ```bash
    timetree-exporter -c calendar_code
    ```

    Note: Find the calendar code in the URL of the calendar page or when running the script without the `-c` option.

- Export a public calendar by id without signing in.

    ```bash
    timetree-exporter --public-calendar -c public_calendar_id
    ```

    Note: Public calendar events use TimeTree's public API and may not include labels, alerts, recurrences, or UUIDs.
    Public calendar metadata such as source links, images, and colors is exported with RFC 7986 properties like `SOURCE`, `IMAGE`, and `COLOR` when available. Calendar apps that only implement RFC 5545 may ignore these optional fields.

- You can pass your email address and password with environment variables. (usually for automation purposes)

  ```bash
  export TIMETREE_EMAIL=email@example.com
  export TIMETREE_PASSWORD=password
  ```

- Create separate ICS files for each label with a custom output directory.

   ```bash
   timetree-exporter --split-by-label
   ```

   This creates individual ICS files for each label (e.g., `timetree_work.ics`, `timetree_personal.ics`).

- Include private event comments.

   ```bash
   timetree-exporter --include-comments
   ```

   Comments are fetched from TimeTree's event activities endpoint and exported as iCalendar `COMMENT` properties, prefixed with the author name when available.

   To change the number of concurrent requests used while fetching comments, pass `--num-workers`.

   ```bash
   timetree-exporter --include-comments --num-workers 5
   ```

   The default is `10`.

   > [!Caution]
   > This option is disabled by default because it makes one or more extra TimeTree requests per event. It can be slow for large calendars and may trigger TimeTree rate limits.

## Limitations

- TimeTree labels include both a category name and a color. When using `--split-by-label`, each category is saved as a separate ICS file.
- Label color information is preserved in the ICS output, but Google Calendar does not apply those event colors when importing ICS files. If you rely on colors to organize events, you may need to check historical color information in TimeTree.
- TimeTree event notes are exported as the iCalendar `DESCRIPTION`. Private event comments are only exported when `--include-comments` is used.

## Support

If you think it's helpful, kindly support me!

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/eoleedi)
