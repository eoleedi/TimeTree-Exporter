# TimeTree Exporter

[![PyPI](https://img.shields.io/pypi/v/timetree-exporter.svg)](https://pypi.org/project/timetree-exporter/)
[![Python 3.x](https://img.shields.io/pypi/pyversions/timetree-exporter.svg?logo=python&logoColor=white)](https://pypi.org/project/timetree-exporter/)
[![License](https://img.shields.io/github/license/eoleedi/TimeTree-Exporter)](https://github.com/eoleedi/TimeTree-Exporter/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/timetree-exporter)](https://pypistats.org/packages/timetree-exporter)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-orange.svg?logo=buymeacoffee&logoColor=white)](https://www.buymeacoffee.com/eoleedi)

A Tool for Exporting TimeTree Calendar and Convert to iCal format(.ics) \
This script works by scraping the TimeTree web app and converting the data to iCal format.
(The .ics file can then be imported into other calendar apps such as Google Calendar, Apple Calendar, Outlook Calendar, etc.)

## Installation

If you are on mac, you can install it using brew:

```bash
brew install eoleedi/tap/timetree-exporter
```

You can also install it using pip or pipx:

```bash
pip install timetree-exporter
```

Timetree Exporter requires Python 3.9 or later.

## Usage

```bash
timetree-exporter -o path/to/output.ics
```

This will prompt you to enter your TimeTree email and password and select the calendar you want to export.

Then, you can import the ics file to your calendar app.

💡 Note: You are advised to import the ICS file into a separate calendar (e.g., Google Calendar) so that if anything goes wrong, you can simply delete the calendar and reimport it.

### Advanced Usage

- You can specify your email address using the `-e` option.

    ```bash
    timetree-exporter -e email@example.com
    ```

- You can specify the calendar code using the `-c` or `--calendar_code` option.

    ```bash
    timetree-exporter -c calendar_code
    ```

    Note: Find the calendar code in the URL of the calendar page or when running the script without the `-c` option.

- You can pass your email address and password with environment variables. (usually for automation purposes)

  ```bash
  export TIMETREE_EMAIL=email@example.com
  export TIMETREE_PASSWORD=password
  ```

## Limitations

Alarms(Alerts) can't be imported to Google Calendar through iCal format due to Google's bug.

## Support

If you think it's helpful, kindly support me!

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/eoleedi)

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
- [ ] **Label ID**
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
