# The main file to run for initializing the app
from easy_ride import app #Import the flask app from the __init__ file in easyride

# Run the imported flask app
if __name__ == '__main__':
    app.run(debug=True) # Set debug to False (default) in production
