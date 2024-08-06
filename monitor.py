import pickle
from plan import BASE, CLASS
from datetime import datetime

# def analyze_sheet_data(spreadsheet_id, planned_tab, actual_tab):
#     try:
#         planned_expenses = get_tab_data(spreadsheet_id, planned_tab)
#         actual_expenses = get_tab_data(spreadsheet_id, actual_tab)
#         month_col = get_current_month(get_col=True, data=planned_expenses)
#         balance = get_balance(actual_expenses)
#         exp_balance = calc_exp_balance(planned_expenses, month_col, balance)
#         balance_str = f'current balance: {balance}\n'
#         exp_balance_str = f'expected balance at the end of the year: {exp_balance}\n'
#         last_month_status = get_last_month_status(actual_expenses, month_col - 1)
#         return balance_str + exp_balance_str + last_month_status
#     except Exception as err:
#         print(f'analyzeSheetData Failed with error {err}')
#
#
# def calc_exp_balance(data, month_col, curr_balance):
#     total_expected = 0
#     for row in data[2:]:
#         for cell in row[month_col:]:
#             if cell and isinstance(cell, int):
#                 total_expected += cell
#     return curr_balance - total_expected
#
#
# def get_balance(data):
#     return data[9][1]
#
#
# def get_last_month_status(data, month_col):
#     categories = get_pay_categories(data)
#     message = " תשלומים חודשיים :\n"
#     for category, row in categories.items():
#         payment = data[row][month_col]
#         if payment:
#             message += f"{category}: {payment}\n"
#         else:
#             message += f"{category}: לא הועברו תשלומים החודש\n"
#     return message
#
#
# def get_pay_categories(data):
#     categories = {}
#     for row_num, row in enumerate(data[1:], start=1):
#         if row[0]:
#             categories[row[0]] = row_num
#     return categories

class STATUS:
    def __init__(self, path_to_pkl):
        with open(path_to_pkl, 'rb') as f:
            self.base = pickle.load(f)
        self.month_to_report = datetime.today().month - 1  # last month

if __name__ == "__main__":
    status = STATUS(path_to_pkl='/Users/dadonofek/PycharmProjects/general/school_automations/2022-2023/base_instance.pkl')

