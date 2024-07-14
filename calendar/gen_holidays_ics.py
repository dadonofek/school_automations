import pdfplumber
import re
import json
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

JSON_KEY_FILE = 'drive/MyDrive/Colab_Notebooks/personal/crypto-triode-425110-s6-1b02a77a76d7.json'
SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

def readFromPdf(path):

  with pdfplumber.open(path) as pdf:
      text = ""
      for page in pdf.pages:
          text += page.extract_text()

  return text

# TODO: improve parser

def reverse_hebrew_text(text):
    def is_hebrew(char):
        return '\u0590' <= char <= '\u05FF' or '\uFB1D' <= char <= '\uFB4F'

    def reverse_if_hebrew(match):
        word = match.group(0)
        if all(is_hebrew(char) for char in word):
            return word[::-1]
        return word

    # Check if the entire text is Hebrew
    all_words = re.findall(r'\b\w+\b', text)
    if all(all(is_hebrew(char) for char in word) for word in all_words):
        return text[::-1]

    # Split the text by non-word characters and apply the reverse_if_hebrew function
    pattern = re.compile(r'(\b\w+\b)')
    result = pattern.sub(reverse_if_hebrew, text)
    return result


def improved_parse_line_v3(line):
    parts = line.split()
    if len(parts) < 6:
        return None

    event = reverse_hebrew_text(" ".join(parts[:2]))
    event = 'גן עד 13:00' if (event == '13:00 בשעה') else event

    # Find the date index safely
    date_index = next((i for i, part in enumerate(parts) if re.match(r'\d{1,2}\.\d{1,2}\.\d{2}', part)), None)
    if date_index is None:
        return None

    date = parts[date_index]
    description = reverse_hebrew_text(" ".join(parts[2:date_index]))

    return {
        "event": event,
        "description": description,
        "date": date,
    }


def write_to_file(data, path):
    with open(path, "w") as file:
        file.write(data)

    print(f"File '{path}' created successfully.")


def format_date(date_str):
    # Assuming the date format in JSON is "dd.mm.yy"
    date = datetime.strptime(date_str, "%d.%m.%y")
    return date.strftime("%Y%m%d")


def json_to_ics(path):
    # Load JSON data from file
    with open(path, 'r', encoding='utf-8') as file:
        events = json.load(file)

    ics_content = "BEGIN:VCALENDAR\n" \
                  "VERSION:2.0\n" \
                  "PRODID:DADONOFEKS_AUTOMATION\n"\
                  "NAME:חופשות מעון\n"\
                  "CALSCALE:GREGORIAN\n"

    for event in events:
        event_date = format_date(event["date"])
        event_summary = event["event"]
        event_description = event["description"]

        ics_content += f"BEGIN:VEVENT\n"
        ics_content += f"DTSTART;VALUE=DATE:{event_date}\n"
        ics_content += f"SUMMARY:{event_summary}\n"
        ics_content += f"DESCRIPTION:{event_description}\n"
        ics_content += f"END:VEVENT\n"

    ics_content += "END:VCALENDAR"

    directory = path.rsplit('/', 1)[0] + '/'
    ics_file_name = directory + 'holiday_schedule.ics'
    with open(ics_file_name, 'w', encoding='utf-8') as file:
        file.write(ics_content)

    return ics_content

def add_summer_break(schedule_full):
    schedule_full[-1]['description'] = 'חופש גדול'
    last_date_str = schedule_full[-1]['date']
    last_date = datetime.strptime(last_date_str, '%d.%m.%y')

    # Generate new dates from the day after the last date up to 1.9
    new_events = []
    next_date = last_date + timedelta(days=1)
    end_date = datetime.strptime('1.9.23', '%d.%m.%y')

    while next_date < end_date:
        new_events.append({'event': 'המעון סגור', 'description': 'חופש גדול', 'date': next_date.strftime('%d.%m.%y')})
        next_date += timedelta(days=1)

    # Append new events to the existing list
    schedule_full.extend(new_events)
    return schedule_full

def write_to_google_sheet(spreadsheet_name, sheet_name, data):
    # Authenticate using the JSON key file
    credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, SCOPE)
    client = gspread.authorize(credentials)

    # Open the Google Sheet by name
    spreadsheet_name = 'וועד מרגנית 2023-2024'  # Replace with the name of your spreadsheet
    sheet = client.open(spreadsheet_name)

    # Select the specific tab (sheet) by name
    tab_name = 'ics_data'  # Replace with the name of the tab you want to write to
    sheet = sheet.worksheet(tab_name)

    sheet.update('A1', data)
    print(f'Data written to Google Sheet "{spreadsheet_name}" in tab "{tab_name}".')

if __name__ == '__main__':
    ############### consts ###############
    curr_dir = os.getcwd()
    pdf_path = os.path.join(curr_dir, 'לוח חופשות תשפג 2022-2023.pdf')
    json_path = os.path.join(curr_dir, 'holiday_schedule.json')
    ics_path = os.path.join(curr_dir, 'holiday_schedule.ics')
    ######################################
    schedule_full = []
    text = readFromPdf(pdf_path)

    lines = text.split('\n')
    for line in lines:
        if line.strip():
            entry = improved_parse_line_v3(line.strip())
            if entry and entry['event'] != 'לפעילות רגילה':
                schedule_full.append(entry)

    schedule_full = add_summer_break(schedule_full)
    # print(schedule_full)
    json_str = json.dumps(schedule_full, ensure_ascii=False, indent=4)
    # write_to_file(json_str, json_path)
    ics_content = json_to_ics(json_path)
    # write_to_file(ics_content, ics_path)

