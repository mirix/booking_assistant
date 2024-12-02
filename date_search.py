### Find available slots in the CSV calendar ###
### produced by the random_calendar.py auxiliary script ###

#nl_dat = ['this Monday', 'today', 'tomorrow morning', 'next Monday', 'Tuesday next week', 'Tuesday afternoon', 'Tuesday or Wednesday', 'early next week', 'hello', 'Saturday', 'Sunday']

import pandas as pd
from datetime import datetime, timedelta

# LLM modes seem to struggle with dates
# The most reliable heuristic option we have found are the datetime recognisers from MS
# https://github.com/Microsoft/Recognizers-Text

from recognizers_date_time import recognize_datetime, Culture

# Today's date
today = datetime.now().date()

# Read the calendar
df = pd.read_csv('random_calendar.csv')

# Function to check if the proposed date is in the check_past
# If so, propose same day next week

def check_past(date):
    if date < today:
        w = timedelta(days=7)
        date = date + w
    else:
        date = date
    return date

# Use recognisers to convert dates in natural languages to datetime objects
# There are different scenarios: single datetime, date, datetime range or date range.
# For simplicity, for this mock exercise we have discarded specific times and day segments (morning, afternoon)
# This functionality is trivial to implement but would complicate the code

def nl_todate(date_dict):
    date_list = []
    if date_dict['type'] == 'date':
        date = datetime.strptime(date_dict['value'], '%Y-%m-%d').date()
        date = check_past(date)
        date_list.append(date)

    elif date_dict['type'] == 'datetime':
        date = datetime.strptime(date_dict['value'], '%Y-%m-%d %H:%M:%S').date()
        date = check_past(date)
        date_list.append(date)

    elif date_dict['type'] == 'datetimerange':
        date = datetime.strptime(date_dict['start'], '%Y-%m-%d %H:%M:%S').date()
        date = check_past(date)
        date_list.append(date)

    elif date_dict['type'] == 'daterange':
        start = datetime.strptime(date_dict['start'], '%Y-%m-%d').date()
        end = datetime.strptime(date_dict['end'], '%Y-%m-%d').date()
        date_list = [start + timedelta(days=d) for d in range((end - start).days + 1)]
        date_list = [check_past(d) for d in date_list]
    return date_list

# Check if the proposed dates are available in the calendar
# The function outputs a dictionary containing the response in plain text
# along with a list of available slots to be proposed to the user

def check_availability(question):

    # Today's date
    today = datetime.now().date()

    # Read the calendar
    df = pd.read_csv('random_calendar.csv')

    response_dict = {'response': '', 'availability_list': []}
    date_list = []

    # Natural language to datetime conversion
    models = recognize_datetime(question, Culture.English)
    dates = [m.resolution['values'] for m in models]
    n_dates = len(dates)

    # Standard response if no dates are indentified
    if n_dates == 0:
        response_dict['response'] = 'The date is too ambiguous, please, suggest an alternative date.'

    # Create list of dates
    else:
        date_list = []
        for sublist in dates:
            for date_dict in sublist:
                date_list_temp = nl_todate(date_dict)
                date_list.extend(date_list_temp)


        date_list = sorted(list(set(date_list)))
        date_list_read = [d.strftime('%Y-%m-%d') for d in date_list]

        # Check for available slots in the proposed dates
        df_select = df[(df['Slot_Availability']==True) & (df['Date'].isin(date_list_read))].copy()
        ava_list = df_select['Date_Readable'].tolist()

        response_dict['response'] = 'These are the available slots in the suggested dates:'
        response_dict['availability_list'] = ava_list

        # If no slots are available on that date, check forward for up to one week
        counter = 0
        while (len(ava_list) == 0 and counter < 6):
            date_list = [d + timedelta(days=1) for d in date_list]
            date_list_read = [d.strftime('%Y-%m-%d') for d in date_list]
            df_select = df[(df['Slot_Availability']==True) & (df['Date'].isin(date_list_read))].copy()
            ava_list = df_select['Date_Readable'].tolist()

            response_dict['response'] = 'There are no available slots in the suggested dates, but these are available:'
            response_dict['availability_list'] = ava_list

            counter += 1

        if len(ava_list) == 0:
            response_dict['response'] = 'No available slots found, please, choose a different date.'

    return response_dict




