from flask import Flask,flash,redirect,url_for
from flask_login import current_user
from functools import wraps
from datetime import date, datetime, timedelta

def check_user_type(user_types):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
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


def format_days(data_raw, num=7):
    data = []
    for i in range(num):
        d = date.today() - timedelta(num - i)
        if d in data_raw:
            data.append((d.strftime('%d/%m'), data_raw[d]))
        else:
            data.append((d.strftime('%d/%m'), 0))
    return data

def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and (not y%100==0 or y%400 == 0) else 28,
        31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=1,month=m, year=y)

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

def format_categories(data_raw, categories):
    data = []
    for category in categories:
        if category in data_raw:
            data.append((category, data_raw[category]))
        else:
            data.append((category, 0))
    return data
