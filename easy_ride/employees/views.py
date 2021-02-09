from flask import render_template,url_for,flash,redirect,request,Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from easy_ride import db

employees = Blueprint('employees',__name__)

@employees.route("/operator_view")
@login_required
def operator_view():
    return render_template('operator_home.html')






@employees.route("/manager_view")
@login_required
def manager_view():
    return render_template('manager_home.html')
