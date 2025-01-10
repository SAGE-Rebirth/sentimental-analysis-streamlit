from flask import Flask
from api.routes import initialize_routes
import os
from dotenv import load_dotenv

# Load environment variables from .env file

# Initialize Flask app
app = Flask(__name__)
initialize_routes(app)

def run_dev():
    """
    Run the Flask app in development mode.
    """
    print("Running in development mode...")
    app.run(debug=True, host="0.0.0.0", port=5000)

def run_prod():
    """
    Run the Flask app in production mode using Gunicorn.
    """
    print("Running in production mode...")
    # This function is not used directly; Gunicorn will use `wsgi.py`.
    pass

if __name__ == "__main__":
    # Check if the app is running in production mode
    if os.getenv("FLASK_ENV") == "prod":
        run_prod()
    else:
        run_dev()