from abc import ABC
from datetime import date, timedelta
from ics import Calendar
from collections import defaultdict
from utils import *


# pmpc = per meeting per child

hebrew_weekday_dict = {
    'ראשון': 1,
    'שני': 2,
    'שלישי': 3,
    'רביעי': 4,
    'חמישי': 5,
    'שישי': 6,
    'שבת': 7
}
hebrew_months = {
    9: 'ספטמבר',
    10: 'אוקטובר',
    11: 'נובמבר',
    12: 'דצמבר',
    1: 'ינואר',
    2: 'פברואר',
    3: 'מרץ',
    4: 'אפריל',
    5: 'מאי',
    6: 'יוני',
    7: 'יולי',
    8: 'אוגוסט'
}
class CLASS():
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.weekday = kwargs.get('weekday')
        self.teachers_name = kwargs.get('teachers_name')
        self.teachers_phone = kwargs.get('teachers_phone')
        self.cost_pm = kwargs.get('cost_pm')

        self.total_exp_cost = None
        self.payed_so_far = None
        self.line = None
        self.planned_meetings = None
        self.grad_party = False
        self.grad_party_cost = 0

    def calc_exp_cost(self, holidays, year_start, year_end, write=False):
        self.planned_meetings = self.count_school_days(holidays, year_start, year_end)
        total_school_days = sum(month_data['school_days'] for month_data in self.planned_meetings.values())
        self.total_exp_cost = total_school_days * int(self.cost_pm) + self.grad_party_cost
        return self.total_exp_cost


    def count_school_days(self, holidays, year_start, year_end):
        current_date = date(year_start, 9, 1)
        end_date = date(year_end, 8, 31)
        school_days_per_month = defaultdict(lambda: {'total_days': 0, 'holidays': set(), 'school_days': 0})

        while current_date <= end_date:
            if current_date.weekday() == self.weekday:
                month_year = (current_date.year, current_date.month)
                school_days_per_month[month_year]['total_days'] += 1
                if current_date in holidays:
                    school_days_per_month[month_year]['holidays'].add(str(current_date.day) + 'th')
                else:
                    school_days_per_month[month_year]['school_days'] += 1
            current_date += timedelta(days=1)

        # Convert sets to lists for holidays
        for month_year in school_days_per_month:
            school_days_per_month[month_year]['holidays'] = list(school_days_per_month[month_year]['holidays'])

        return dict(school_days_per_month)


class BASE(ABC):
    def __init__(self, **kwargs):
        self.year_start = kwargs.get('year_start')
        self.year_end = kwargs.get('year_end')
        self.gsheet_id = kwargs.get('gsheet_id')
        self.holidays_ics_path = kwargs.get('holidays_ics_path')
        self.holidays_pdf_path = kwargs.get('holidays_pdf_path')
        self.credentials_path = kwargs.get('credentials_path')
        self.input_tab = kwargs.get('input_tab')

        self.n_kids = None
        self.n_teachers = None
        self.classes = {}
        self.gifts = {'מתנות לצוות': {},
                      'מתנות לילדים': {}
                      }
        self.input_data = None
        self.total_gifts_cost = None
        self.total_classes_cost = 0
        self.total_exp_cost = None
        self.holidays = set()


    def plan(self):
        '''
        get data from gsheet (filled by user) and from holidays
        to plan total expected expenses
        :return: payment
        '''
        self.input_data = read_from_sheet(credentials_path=self.credentials_path,
                                          gsheet_id=self.gsheet_id,
                                          tab=self.input_tab)
        self.parse_input()
        self.parse_holidays()
        for cl in self.classes.values():
            self.total_classes_cost += cl.calc_exp_cost(self.holidays, self.year_start, self.year_end, write=True)
            write_to_sheet_cell(credentials_path=self.credentials_path,
                                gsheet_id=self.gsheet_id,
                                tab='input',
                                data={(cl.line, 0): cl.total_exp_cost})

        self.total_exp_cost = self.total_gifts_cost + self.total_classes_cost
        # sanity:
        if self.total_exp_cost != int(self.input_data[17][0]):
            print('somthing is wrong in total cost calc')
            return None

        self.create_monitor_tab()
        return self.total_exp_cost

    def create_monitor_tab(self):
        data_to_write = {}

        # Header for months
        for col, (month_num, month_name) in enumerate(hebrew_months.items(), start=2):
            data_to_write[(1, col)] = month_name

        # Fill class data dynamically
        start_row = 2
        for idx, (class_name, cls) in enumerate(self.classes.items()):
            class_row = start_row + idx * 7  # Leave space between classes    15

            data_to_write[(class_row, 0)] = cls.name
            data_to_write[(class_row + 1, 1)] = 'חגים'
            data_to_write[(class_row + 2, 1)] = 'מספר מפגשים צפוי'
            data_to_write[(class_row + 3, 1)] = 'תשלום צפוי'
            data_to_write[(class_row + 4, 1)] = 'מספר מפגשים בפועל'
            data_to_write[(class_row + 5, 1)] = 'תשלום בפועל'
            if cls.grad_party:
                data_to_write[(class_row + 1, 15)] = 'מסיבת סיום'
                data_to_write[(class_row + 3, 15)] = cls.grad_party_cost

            for col, month in enumerate(cls.planned_meetings.keys(), start=2):
                year, month_num = month
                planned_meeting = cls.planned_meetings[month]

                data_to_write[(class_row + 1, col)] = ', '.join(
                    [str(date) for date in planned_meeting['holidays']])
                data_to_write[(class_row + 2, col)] = planned_meeting['school_days']
                data_to_write[(class_row + 3, col)] = planned_meeting['school_days'] * cls.cost_pm

        write_to_sheet_cell(self.credentials_path, self.gsheet_id, 'monitor', data_to_write, create_tab=True)
    def parse_holidays(self):
        with open(self.holidays_ics_path, 'r', encoding='utf-8') as f:
            gcal = Calendar(f.read())

        for event in gcal.events:
            event_date = event.begin.date()
            if event.name == 'המעון סגור':
                self.holidays.add(event_date)


    def parse_input(self):
        gifts_start_line = 8
        gifts_end_line = 15
        classes_lines = [1, 2, 3]
        class_name_col = 8
        self.n_kids = self.input_data[5][6]
        self.n_teachers = self.input_data[6][6]

        #parse classes
        for line in classes_lines:
            if self.input_data[line][class_name_col] == '':
                continue # no name => no class
            else:
                cur_class = CLASS()
                cur_class.line = line
                cur_class.name = self.input_data[line][class_name_col]
                cur_class.teacher = self.input_data[line][class_name_col-1]
                cur_class.teachers_phone = self.input_data[line][class_name_col-2]
                cur_class.weekday = hebrew_weekday_dict.get(self.input_data[line][class_name_col-3].strip())
                if cur_class.weekday is None:
                    print(f'weekday for class {cur_class.name} unrecognized')
                cur_class.cost_pm = int(self.input_data[line][class_name_col-4])
                cur_class.grad_party = self.input_data[line][1] != ''
                if cur_class.grad_party:
                    cur_class.grad_party_cost = int(self.input_data[line][1])

                self.classes[cur_class.name] = cur_class

        # parse gifts:
        for line in range(gifts_start_line, gifts_end_line):
            # for kids
            if self.input_data[line][5] != 0:
                holiday = self.input_data[line][7]
                cost = self.input_data[line][5]
                self.gifts['מתנות לילדים'][holiday] = int(cost)

            # for teachers
            if self.input_data[line][3] != 0:
                holiday = self.input_data[line][7]
                cost = self.input_data[line][3]
                self.gifts['מתנות לצוות'][holiday] = int(cost)

        self.total_gifts_cost = int(self.input_data[16][2])

        #sanity:
        if self.total_gifts_cost != sum(self.gifts['מתנות לצוות'].values()) + sum(self.gifts['מתנות לילדים'].values()):
            print('somthing is wrong in gifts cost calc')


if __name__ == "__main__":
    params = {'year_start': 2022,
              'year_end': 2023,
              'gsheet_id': '1dx4lOYBhhNl57gLA9uLuINQ3fhBYElpGS0MwOPwzjEA',
              'holidays_ics_path': '/Users/dadonofek/PycharmProjects/general/school_automation_1/calendar/holiday_schedule.ics',
              'holidays_pdf_path': '/Users/dadonofek/PycharmProjects/general/school_automation_1/calendar/לוח חופשות תשפג 2022-2023.pdf',
              'credentials_path': '/Users/dadonofek/Library/Mobile Documents/com~apple~CloudDocs/מסמכים חשובים/google_credentials.json',
              'input_tab': 'input'
              }

    base = BASE(**params)
    data = base.plan()
