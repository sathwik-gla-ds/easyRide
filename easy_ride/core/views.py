# contains the flask routes related to basic pages such as home, information pages

from flask import render_template, request, Blueprint

core = Blueprint('core', __name__) # For registering the Blueprint/folder in main __init__.py file

# Index or Home static page
@core.route('/')
def index():
    return render_template('index.html') # Page to use/render when a user visits the route

# How it works info static page
@core.route('/howitworks')
def howitworks():
    return render_template('howitworks.html') # Page to use/render when a user visits the route

# Locations info static page
@core.route('/locations')
def locations():
    return render_template('locations.html') # Page to use/render when a user visits the route

# About us info static page
@core.route('/aboutus')
def aboutus():
    return render_template('aboutus.html') # Page to use/render when a user visits the route

# Pricing info static page
@core.route('/pricing')
def pricing():
    return render_template('pricing.html') # Page to use/render when a user visits the route
