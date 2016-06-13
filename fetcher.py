from __future__ import print_function

import argparse
import datetime

import httplib2
import oauth2client
import os
from apiclient import discovery
from dateutil.parser import parse
from oauth2client import client
from oauth2client import tools
from settings import *

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
APPLICATION_NAME = 'Arsh report generator'
CLIENT_SECRET_FILE = 'client_secret.json'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME

        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def fetch(calendar_id):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow()  # 'Z' indicates UTC time
    start_of_week = now - datetime.timedelta(days=(now.weekday() + 2) % 7, hours=now.hour, minutes=now.minute,
                                             seconds=now.second)
    end_of_week = start_of_week + datetime.timedelta(days=7)

    events_result = service.events().list(calendarId=calendar_id, orderBy='startTime',
                                          timeMin=start_of_week.isoformat() + 'Z',
                                          timeMax=end_of_week.isoformat() + 'Z', singleEvents=True).execute()
    events = events_result.get('items', [])

    if not events:
        print('رویدادی در این هفته وجود ندارد')
        return

    days = {}
    for event in events:
        start = parse(event['start']['date']) if 'date' in event['start'] else parse(event['start']['dateTime'])

        if start.date() not in days:
            days[start.date()] = {}

        day_events = days[start.date()]

        if event['summary'] not in day_events:
            if 'description' in event and COMMAND_IGNORE in event['description']:
                continue

            day_events[event['summary']] = {'duration': datetime.timedelta(), 'description': [], 'reason': [],
                                            'done': True}

        c_event = day_events[event['summary']]

        if 'description' in event:
            for line in iter(event['description'].splitlines()):
                if COMMAND_REASON not in line:
                    c_event['description'].append(line)
                else:
                    c_event['reason'].append(line.replace(COMMAND_REASON, ''))

        if not event['colorId'] == '10':
            c_event['done'] = False

        end = parse(event['end']['date']) if 'date' in event['end'] else parse(event['end']['dateTime'])

        c_event['duration'] += end - start

    return days
