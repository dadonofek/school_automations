import smtplib
from email.mime.text import MIMEText
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time


'''the idea is to be very strict with clases 
(calc every month expected pay and monitor every month)
and be more loose about gifts- only monitor when expended
'''


def read_from_sheet(credentials_path, gsheet_id, tab):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scopes=[
        'https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(gsheet_id).worksheet(tab)
    data = sheet.get_all_values()
    return data


def write_to_sheet_cell(credentials_path, gsheet_id, tab, data, create_tab=False):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scopes=[
        'https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
    client = gspread.authorize(credentials)
    if create_tab:
        sheet = client.open_by_key(gsheet_id)
        worksheet = sheet.add_worksheet(title=tab, rows=1000, cols=1000)
    else:
        worksheet = client.open_by_key(gsheet_id).worksheet(tab)
    n = 1
    for cell, val in data.items():
        if n % 50 == 0:  # avoid queries per minute limit
            time.sleep(60)
        worksheet.update_cell(cell[0]+1, cell[1]+1, val)
        n += 1


def send_mail(email, subject, body):
    try:
        print(f'email {email}, subject {subject}, body {body}')
        # Use your own email credentials or a configured SMTP server here
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = 'your-email@example.com'
        msg['To'] = email
        with smtplib.SMTP('smtp.example.com') as server:
            server.login('your-email@example.com', 'your-password')
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
    except Exception as err:
        print(f'SendMail Failed with error {err}')




if __name__ == "__main__":

    write_to_sheet_cell(credentials_path='/Users/dadonofek/Library/Mobile Documents/com~apple~CloudDocs/מסמכים חשובים/google_credentials.json',
                        gsheet_id='1dx4lOYBhhNl57gLA9uLuINQ3fhBYElpGS0MwOPwzjEA',
                        tab='tmp',
                        data={(1,1):'blabla'})




