# TimeTree Exporter
A Tool for Exporting TimeTree Calendar and Convert to iCal format(.ics) 
(The .ics file can then be imported into other calendar apps such as Google Calendar, Apple Calendar, Outlook Calendar, etc.)

# Usage
1. Download the timetree data manually and put it in the responses folder(see below)
2. Install the requirements `pip3 install -r requirements.txt`
3. Run `python3 timetree_to_ical.py`
4. A timetree.ics file will be generated in the same directory, then you can import it to your calendar app.
## Recommendation
You are recommended to import the ics file into a separate calendar (take google calendar as an example) as if anything goes wrong, you can just delete the calendar and reimport it.
## How to download timetree data
1. Go to [https://timetreeapp.com/signin](https://timetreeapp.com/signin)
2. Open the developer tools before logging in
      > Can be opened by pressing F12
3. Go to the network tab
      > Remember to Press Ctrl + R to start recording
4. Turn on preserve log
5. Type in "sync" in the filter box
6. Log in
7. Click on the calendar you want to export
8. You will see couple of requests with the name "sync"
      > There seems to be a maximum of 300 events in single requests. \
      > If you have more than 300 events, you will see multiple requests with the name "sync"
9.  Right click on the request and select "Copy Response"
10. Paste it into a json file under the response folder under this project (etc. sync.json)
      > The file name should end with .json
11. Do the same thing for all the requests with steps 7~10

![Prepare for signin: Step 1~5](/assets/images/prepare-for-signin.png)
*Prepare for signin: Step 1~5*
![Copy response: Step 8~9](/assets/images/copy-response.png)
*Copy response: Step 8~9*

# Requirements
icalendar==5.0.11

# Limitations
Currently, TimeTree data can only be downloaded manually through a web browser.

# Roadmap of the properties mapping to iCal
- [ ] **ID**
- [ ] **Primary ID**
- [ ] **Calendar ID**
- [x] **UUID**
- [ ] **Category**
- [ ] **Type**
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
- [ ] **Parent ID**
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
