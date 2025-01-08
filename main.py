from flask import Flask, jsonify
from api.routes import initialize_routes
import os

# Initialize Flask app
app = Flask(__name__)
initialize_routes(app)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify if the Flask server is running.
    """
    return jsonify({"status": "ok"}), 200

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
    if os.getenv("FLASK_ENV") == "production":
        run_prod()
    else:
        run_dev()