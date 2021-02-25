# contains the routes related to error pages

from flask import Blueprint,render_template

error_pages = Blueprint('error_pages',__name__) # For registering the Blueprint/folder in main __init__.py file

# Page to load when no page with provided route is found
@error_pages.app_errorhandler(404)
def error_404(error):
    return render_template('error_pages/404.html') , 404

# Page to load when provided route is for forbidden to access by the user
@error_pages.app_errorhandler(403)
def error_403(error):
    return render_template('error_pages/403.html') , 403
