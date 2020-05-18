import os

GOOGLE_CLIENT_CONFIG = {
    "web":
        {
            "client_id":os.environ.get("GOOGLE_CLIENT_ID"),
            "project_id":"harryclimateapp",
            "auth_uri":"https://accounts.google.com/o/oauth2/auth",
            "token_uri":"https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
            "client_secret":os.environ.get("GOOGLE_CLIENT_SECRET"),
            "redirect_uris":
                [
                    "https://localhost:5000/oauth2callback",
                    "https://127.0.0.1:5000/oauth2callback",
                    "https://climatebin.herokuapp.com/oauth2callback"
                ]
        }
}