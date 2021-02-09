#core/views

from flask import render_template, request, Blueprint

core = Blueprint('core', __name__)

@core.route('/')
def index():
    #TODO
    return render_template('index.html')

@core.route('/howitworks')
def howitworks():
    return render_template('howitworks.html')

@core.route('/locations')
def locations():
    return render_template('locations.html')

@core.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@core.route('/pricing')
def pricing():
    return render_template('pricing.html')
