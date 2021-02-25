# Helper function to update the profile picture. Cannot use if deployed in heroku as it doesnt support storage.

import os
from PIL import Image
from flask import current_app

# Function to format the profile picture, rename it and store in appropiate location
def add_profile_pic(pic_upload, user_id):
    filename = pic_upload.filename
    ext_type = filename.split('.')[-1]
    storage_filename = 'profile_pic_' + str(user_id) + '.' + ext_type # Rename it
    filepath = os.path.join(current_app.root_path, 'static\profile_pics', storage_filename) # Select the path
    output_size = (200,200)

    pic = Image.open(pic_upload) # Load the image
    pic.thumbnail(output_size) # Convert it into a thumbnail of 200x200 to save space
    pic.save(filepath) # Save it in the choosen path location

    return storage_filename # Return the file name
