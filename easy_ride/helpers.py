# Some resuable functions for the project

from flask import flash,redirect,url_for
from flask_login import current_user
from functools import wraps
from datetime import date, timedelta

# A class for converting any dictionary to an object, used in simulation.py
class Cnv2Obj:
    def __init__(self, entries):
        self.__dict__.update(entries)

# A decorator function to check whether a user has access to a certain webpage or not. Used in almost all the view.py files while routing
def check_user_type(user_types):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            # If a user doesn't have access to any webpages flash a message and redirect them appropriately
            if current_user.user_type.name in user_types:
                return function(*args, **kwargs)
            elif current_user.user_type.name == 'OPERATOR':
                flash('Access Denied')
                return redirect(url_for('employees.operator_view'))
            elif current_user.user_type.name == 'MANAGER':
                flash('Access Denied')
                return redirect(url_for('employees.manager_view'))
            else:
                flash('Access Denied')
                return redirect(url_for('core.index'))
            return function(*args, **kwargs)
        return wrapper
    return decorator

# Add addtional dates for which values are 0 and also sort them in order. Used in manager view for formatting data for the graphs
# Ex: Input: ['21/01':2, '19/01':3, '22/01':2] gets an output ['19/01':3, '20/01':0, '21/01':2, '22/01':2, '23/01':0, '24/01':0]
def format_days(data_raw, num=7):
    data = []
    for i in range(num):
        d = date.today() - timedelta(num - i)
        if d in data_raw:
            data.append((d.strftime('%d/%m'), data_raw[d]))
        else:
            data.append((d.strftime('%d/%m'), 0))
    return data

# Used for subtracting the months in a date object. Used in format_months function below.
# Got the logic from user Duncan on stackoverflow at https://stackoverflow.com/questions/3424899/return-datetime-object-of-previous-month. Changed logic slightly to suit the needs
def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and (not y%100==0 or y%400 == 0) else 28,
        31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=1,month=m, year=y)

# Add addtional months for which values are 0 and also sort them in order. Used in manager view for formatting data for the graphs
# Ex: Input: ['Jan':2, 'Jun':3, 'Apr':2] gets an output ['Jan':2, 'Feb':0, 'Mar':0, 'Apr':2, 'May':0, 'Jun':3]
def format_months(data_raw, num=6):
    months = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'June', 7:'July', 8:'Aug', 9:'Sept', 10:'Oct', 11:'Nov', 12:'Dec'}
    data = []
    for i in range(num):
        m = monthdelta(date.today(), i-num+1).month
        if m in data_raw:
            data.append((months[m], data_raw[m]))
        else:
            data.append((months[m],0))
    return data

# Add addtional categories for which values are 0 and also sort them in order. Used in manager view for formatting data for the graphs and also simulation.py
# Ex: Input: ['PARTICK':2, 'HILLHEAD':3, 'LAURIESTON':2] gets an output ['HILLHEAD':3, 'PARTICK':2, 'FINNIESTON':0, 'GOVAN':0, 'LAURIESTON':2]
def format_categories(data_raw, categories):
    data = []
    for category in categories:
        if category in data_raw:
            data.append((category, data_raw[category]))
        else:
            data.append((category, 0))
    return data
