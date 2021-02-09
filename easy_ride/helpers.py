from flask import Flask,flash,redirect,url_for
from flask_login import current_user
from functools import wraps

def check_user_type(user_type):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if current_user.user_type.name == user_type:
                return function(*args, **kwargs)
            elif current_user.user_type.name == 'OPERATOR':
                flash('Denied Access')
                return redirect(url_for('employees.operator_view'))
            elif current_user.user_type.name == 'MANAGER':
                flash('Denied Access')
                return redirect(url_for('employees.manager_view'))
            else:
                flash('Denied Access')
                return redirect(url_for('core.index'))
            return function(*args, **kwargs)
        return wrapper
    return decorator
