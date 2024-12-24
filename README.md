# TimeTree Exporter

A Tool for Exporting TimeTree Calendar and Convert to iCal format(.ics) \
This script works by scraping the TimeTree web app and converting the data to iCal format.
(The .ics file can then be imported into other calendar apps such as Google Calendar, Apple Calendar, Outlook Calendar, etc.)

## Installation

If you are on mac, you can install it using brew:

```bash
brew install eoleedi/timetree-exporter/timetree-exporter
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

### Additional Options

- You can specify your email address using the `-e` option.

    ```bash
    timetree-exporter -e <email>
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
