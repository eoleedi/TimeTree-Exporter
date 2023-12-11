# TimeTree Exporter
> This tool is currently in development and is not ready for use.
> However, basic functionality is working such as event title, time, alert.
> 
# Usage
1. Download the timetree data manually and put it in the responses folder(see below)
2. Install the requirements `pip3 install -r requirements.txt`
3. Run `python3 timetree-to-iCal.py`
4. A timetree.ics file will be generated in the same directory, then you can import it to your calendar app.

## How to download timetree data
1. Go to [https://timetreeapp.com/login](https://timetreeapp.com/login)
2. Open the developer tools before logging in
3. Go to the network tab
4. Turn on preserve log
5. Log in
6. Type in "sync" in the filter box
7. You will see couple of requests with the name "sync"
   - There seems to be a maximum of 300 events in single requests.
8. Right click on the request and select "Copy Response"
9.  Paste it into a json file under the response folder under this project (etc. sync.json)
10. Do the same thing for all the requests with steps 7~9


# ROADMAP of the properties mapping to iCal
- [ ] **ID**
- [ ] **Primary ID**
- [ ] **Calendar ID**
- [x] **UUID**
- [ ] **Category**
- [ ] **Type**
- [ ] **Author ID**
- [ ] **Author Type**
- [x] **Title**
- [ ] **All Day**
- [x] **Start At**
- [x] **Start Timezone**
- [x] **End At**
- [x] **End Timezone**
- [ ] **Label ID**
- [x] **Location**
- [ ] **Location Latitude**
- [ ] **Location Longitude**
- [ ] **URL**
- [ ] **Note**
- [ ] **Lunar**
- [ ] **Attendees**
- [ ] **Recurrences**
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
- [ ] **Updated At**
- [ ] **Created At**
