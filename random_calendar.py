### AUXILIARY SCRIPT TO GENERATE A RANDOM AVAILABILITY CALENDAR ###
### IN JSON FORMAT FROM TODAY TILL YEAR END ###

import json
import random
import pandas as pd
import dateutil.parser as dparser
from datetime import date, datetime

# Generate dates from today to the end of the year

today = datetime.today().date()
year = int(datetime.today().year)
year_end = date(year, 12, 31)
dates = pd.date_range(today, year_end, freq='d').strftime('%Y-%m-%d').tolist()

# Create list with list of bank holidays in Luxembourg

df = pd.read_html('https://www.lfma.lu/luxembourg-banking-holidays/')[0]
bank_hol = df['Date'].apply(lambda x: dparser.parse(x, fuzzy=True)).dt.strftime('%Y-%m-%d').tolist()

# Create calendar dictionaery

calendar = {}
for date in dates:
    slots = range(9, 16)
    day = datetime.strptime(date, '%Y-%m-%d').date().strftime('%A')

    # For saturdays, sundays and bank holidays set the availability to false
    if day == 'Sunday' or day == 'Saturday' or date in bank_hol:
        slot_list = []
        for slot in slots:
            slot_dict = {'start': str(slot).zfill(2) + ':00', 'end': str(slot + 1).zfill(2) + ':00', 'available': False}
            slot_list.append(slot_dict)
        calendar[date] = slot_list

    # For saturdays and working days set random availability for each slot
    else:
        slot_list = []
        for slot in slots:
            slot_dict = {'start': str(slot).zfill(2) + ':00', 'end': str(slot + 1).zfill(2) + ':00', 'available': random.choice([True, False])}
            slot_list.append(slot_dict)
        calendar[date] = slot_list

# Convert dictionary to JSON

json_object = json.dumps(calendar, indent = 4)
#print(json_object)

# Save JSON

with open('random_calendar.json', 'w') as outfile:
    json.dump(calendar, outfile)

# Convert dictionary to Pandas dataframe

dict_calendar = {'Date': [], 'Year': [], 'Month': [], 'Day': [], 'Day_of_the_week': [], 'Week': [], 'Slot_Start_Time': [], 'Slot_End_Time': [], 'Slot_Availability': [], 'Date_Readable': []}

for key in calendar.keys():
    for prop in calendar[key]:

        date = key
        year, month, day = date.split('-')
        start = prop['start']
        end = prop['end']
        hour, minute = prop['start'].split(':')
        end_hour, end_min = prop['end'].split(':')
        datetime_object = datetime(int(year), int(month), int(day), int(hour), int(minute))
        week = datetime.strftime(datetime_object, '%-U')
        day_week = datetime.strftime(datetime_object, '%A')
        day_month = datetime.strftime(datetime_object, '%-d')
        month = datetime.strftime(datetime_object, '%B')
        datetime_read = datetime.strftime(datetime_object, '%A %-d %B %Y %H:%M')
        # + '-' + end_hour + ':' + end_min + ' '
        availability = prop['available']

        dict_calendar['Date'].append(date)
        dict_calendar['Year'].append(int(year))
        dict_calendar['Month'].append(month)
        dict_calendar['Day'].append(int(day_month))
        dict_calendar['Day_of_the_week'].append(day_week)
        dict_calendar['Week'].append(week)
        dict_calendar['Slot_Start_Time'].append(start)
        dict_calendar['Slot_End_Time'].append(end)
        dict_calendar['Slot_Availability'].append(availability)
        dict_calendar['Date_Readable'].append(datetime_read)

df_cal = pd.DataFrame(dict_calendar)

print(df_cal)

# Save Pandas dataframe

df_cal.to_csv('random_calendar.csv', index=False, header=True)


