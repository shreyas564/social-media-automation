import os
from dotenv import load_dotenv

load_dotenv()

FACEBOOK_TOKEN = os.getenv("FACEBOOK_TOKEN")
INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_TOKEN")
LINKEDIN_TOKEN = os.getenv("LINKEDIN_TOKEN")