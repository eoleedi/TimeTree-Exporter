# TimeTree Exporter

A Tool for Exporting TimeTree Calendar and Convert to iCal format(.ics) \
(The .ics file can then be imported into other calendar apps such as Google Calendar, Apple Calendar, Outlook Calendar, etc.)

## Usage

1. Run the script and type the email and password of your TimeTree account.
2. Select the calendar you want to export.
3. Done! A timetree.ics file will be generated, then you can import it to your calendar app.

### Method 1: Pip

1. Install the package `pip3 install timetree-exporter`
2. Run `timetree-exporter`
   - Preferably, you can run `timetree-exporter -e <email>` to skip the input of email
   - and `timetree-exporter -o <output-file-path>.ics` to specify the output file path
3. Type in the email and password of your TimeTree account as prompted.
4. A timetree.ics file will be generated in the same directory, then you can import it to your calendar app.

### Method 2: Cloning the repository

1. Clone the repository `git clone https://github.com/eoleedi/TimeTree-exporter.git`
2. Change the directory to the project folder `cd TimeTree-exporter`
3. Install the requirements `pip3 install -r requirements.txt`
4. Run `python3 -m timetree_exporter`
    - Preferably, you can run `python3 -m timetree_exporter -e <email>` to skip the input of email
    - and `python3 -m timetree_exporter -o <output-file-path>.ics` to specify the output file path
5. Type in the email and password of your TimeTree account as prompted.
6. A timetree.ics file will be generated in the same directory, then you can import it to your calendar app.

## Recommendation

You are recommended to import the ics file into a separate calendar (take google calendar as an example) as if anything goes wrong, you can just delete the calendar and reimport it.

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
- [ ] **Row Order**
- [ ] **Attachment**
- [ ] **Like Count**
- [ ] **Files**
- [ ] **Deactivated At**
- [ ] **Pinned At**
- [x] **Updated At**
- [x] **Created At**
