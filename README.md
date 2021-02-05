EasyRide
|   app.py (File which launches the flask application)
|   requirements.txt (The required python libraries for the application)
|   
+---easy_ride
|   |   models.py (Defines the database tables, columns and their values.)
|   |   __init__.py (Initiates the flask application and the blueprints)
|   |   
|   +---core (contains the files related to basic functionality such as home page, about etc.)
|   |   |   forms.py (contains the forms related to basic functionality)
|   |   |   views.py (contains the routes related to basic functionality)
|   |   |   
|   |           
|   +---employees (contains the files related to employees functionality such as operator, manager views etc.)
|   |       forms.py (contains the forms related to employees functionality)
|   |       views.py (contains the routes related to employees functionality)
|   |       
|   +---error_pages (contains the files related to error functionality such as 403, 404)
|   |   |   handlers.py (contains the routes related to error pages)
|   |   |   
|   |           
|   +---rides (contains the files related to ride functionality such as rent, return etc.)
|   |   |   forms.py (contains the forms related to ride functionality)
|   |   |   views.py (contains the routes related to ride functionality)
|   |           
|   +---static (contains the static image files)
|   |   \---profile_pics (stores the profile images)
|   |           default_profile.jpg (default profile image)
|   |           
|   +---templates (contains all the HTML files required to render by the routes in all views.py files)
|   |   |   aboutus.html (Static About us page)
|   |   |   account.html (My Profile page)
|   |   |   account_layout.html (Navbar layout for the account tab. Will be reused in all account related pages)
|   |   |   addbalance.html (Add wallet balance page)
|   |   |   base.html (Main Navbar layout. Used in all pages)
|   |   |   booking.html (Booked ride details including bike number, pin etc.)
|   |   |   howitworks.html (Static how the application works page)
|   |   |   index.html (Static home page)
|   |   |   locations.html (Static available locations page)
|   |   |   login.html (User login page)
|   |   |   payment.html (Ride payment page)
|   |   |   placeback.html (Bike return page)
|   |   |   pricing.html (Static pricing page)
|   |   |   register.html (User registration page)
|   |   |   rent.html (Bike renting page)
|   |   |   reportbike.html (Defective bike report page)
|   |   |   userreviews.html (Past user reviews list page)
|   |   |   userrides.html (Past user ride history page)
|   |   |   wallet.html (Wallet balance page)
|   |   |   
|   |   \---error_pages (Error HTML render pages)
|   |           403.html
|   |           404.html
|   |           
|   +---users (contains the files related to user account functionality such as register, login, history etc.)
|   |   |   forms.py (contains the forms related to users functionality)
|   |   |   picture_handler.py (contains the function for updating the profile picture)
|   |   |   views.py (contains the routes related to users functionality)
|   |   |   
