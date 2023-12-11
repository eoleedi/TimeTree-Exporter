from icalendar import Calendar, Event
from datetime import datetime, timedelta, timezone
import json
from dateutil import tz 
import os

def convert_to_ical(events_data, cal: Calendar = None):
    if cal is None:
        cal = Calendar()

    for event_data in events_data:
        event = Event()
        
        event.add('uid', event_data['uuid'])
        event.add('summary', event_data['title'])
        event.add('dtstamp', datetime.now(timezone.utc))
        event.add('dtstart', datetime.fromtimestamp(event_data['start_at'] / 1000, tz.gettz(event_data['start_timezone'])))
        event.add('dtend', datetime.fromtimestamp(event_data['end_at'] / 1000, tz.gettz(event_data['end_timezone'])))
        event.add('location', event_data.get('location', ''))
        
        # Alarms (if available)
        for alert_minutes in event_data.get('alerts', []):
            alarm = Event()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', 'Reminder')
            alarm.add('trigger', timedelta(minutes=-alert_minutes))
            event.add_component(alarm)

        cal.add_component(event)


    return cal.to_ical()

def fetch_events(file_path):
    with open(file_path, 'r') as f:
        response_data = json.load(f)
        response_data['events']
        return response_data['events']

if __name__ == '__main__':

    responses = os.listdir('responses')
    cal = Calendar()
    for response in responses:
        if not response.endswith('.json'):
            continue
        print(f'Parsing {response}')
        events_data = fetch_events(f'responses/{response}')
        ical_data = convert_to_ical(events_data, cal)

    with open('timetree.ics', 'wb') as f:
        f.write(ical_data)
