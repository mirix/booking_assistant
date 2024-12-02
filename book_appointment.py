### Functions to book appointment ###

import time
import pandas as pd
from datetime import datetime

# LLM modes seem to struggle with dates
# The most reliable heuristic option we have found are the datetime recognisers from MS
# https://github.com/Microsoft/Recognizers-Text

from recognizers_date_time import recognize_datetime, Culture

weeks = []

def appointment_booking(question):

    now = datetime.fromtimestamp(time.time())

    # Read the calendar
    df = pd.read_csv('random_calendar.csv')

    date_list = []

    # Date recogniser
    models = recognize_datetime(question, Culture.English)
    dates = [m.resolution['values'] for m in models]
    n_dates = len(dates)

    # If no dates are found output generic language
    if n_dates == 0:
        response = 'If you wish to book an appointment, please, provide a specific date and time. Feel free to recheck availability if required.'
    #If dates are found iterate over the JSON object
    else:
        for sublist in dates:
            for date_dict in sublist:
                # Check if it is a data time object
                if date_dict['type'] == 'datetime':
                    # Extract the date time info
                    prospective_date = datetime.strptime(date_dict['value'], '%Y-%m-%d %H:%M:%S')
                    hour = datetime.strftime(prospective_date, '%-H')
                    minute = datetime.strftime(prospective_date, '%-M')
                    # Check if the datetime is in the future and that the requested slot is in agreement with the policies
                    if (now <= prospective_date) and (int(minute) == 0) and (int(hour) in range(9, 17)):
                        date_list.append(prospective_date)
        # If there are no valid dates produce standard message
        if len(date_list) == 0:
            response = 'Valid slots are workdays from 9 AM to 4 PM (only o\'clock times). Feel free to recheck availability if required.'
        # If there is more than one date, ask the user to choose
        elif len(date_list) > 1:
            date_read = [datetime.strftime(d, '%A %-d %B %Y %-I %p') for d in date_list]
            response = 'You can only book one slot at a time, which of the following would you would wish to book first? \n' + '\n'.join(date_read)
        # If there is one date carry out a few more consistency chechs
        elif len(date_list) == 1:

            check_date = datetime.strftime(date_list[0], '%Y-%m-%d')
            check_time = datetime.strftime(date_list[0], '%H:%M')
            check_week = int(datetime.strftime(date_list[0], '%-W'))

            # Check if the date is in the calendar
            if len(df[(df['Date'] == check_date)]) == 0:
                response = 'The date  ' + check_date + ' is not in this year\'s calendar. Feel free to recheck availability if required.'
            # Check if the slot is available
            elif df.loc[(df['Date'] == check_date) & (df['Slot_Start_Time'] == check_time), 'Slot_Availability'].item() == False:
                response = 'The slot  ' + check_date + ' ' + check_time + ' is not available. Feel free to recheck availability if required.'
            # If it is a valid date and an available slot, book it
            elif weeks.count(check_week) >=2:
                response = 'You can only book two appointments per week. Should you need to book another appointment, please, choose a different week.'
            else:

                df.loc[(df['Date'] == check_date) & (df['Slot_Start_Time'] == check_time), ['Slot_Availability']] = False
                df.to_csv('random_calendar.csv', index=False, header=True)

                date_read = datetime.strftime(date_list[0], '%A %-d %B %Y %-I %p')
                response = 'Booking confirmed for ' + date_read

                weeks.append(check_week)

                df = pd.read_csv('random_calendar.csv')

    return response


# questions = ['Tomorrow at 10', 'August 25 at 2 PM', 'Monday at 9', 'November 15 at 9 AM', 'December 15 at 10:00', 'hello', 'Tomorrow at 10:30', 'Friday at 9 AM or Monday 9 AM']

#for q in questions:
#    appointment_booking(q)

