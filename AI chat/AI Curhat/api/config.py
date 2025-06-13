import os

GOOGLE_CLOUD_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials/gcloud_key.json")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
DEBUG_MODE = os.getenv("DEBUG_MODE", "True") == "True"
