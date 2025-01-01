import os


def get_website_url():
    return os.environ.get("WEBSITE_URL", "http://localhost:5173")
