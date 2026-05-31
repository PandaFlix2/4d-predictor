# passenger_wsgi.py - IMPORTANT: Put this in your project root
import sys
import os

# Add your project directory to the path
project_home = '/home/[USERNAME]/4d-predictor'

# Replace [USERNAME] with your actual PythonAnywhere username!
# Example: if username is 'ramal4d', then path is '/home/ramal4d/4d-predictor'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variable for Flask
os.environ['FLASK_APP'] = 'app.py'

# Import the Flask app
from app import app as application

# Optional: For debugging
def application(environ, start_response):
    # You can add logging here if needed
    return application(environ, start_response)