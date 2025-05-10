import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LinkedIn credentials
LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', 'your-email@example.com')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', 'your-password')

# ProtonMail credentials
GMAIL_EMAIL = "jobs-isreal@proton.me"
GMAIL_APP_PASSWORD = "123456789Aa"

# Search parameters
JOB_KEYWORDS = [
    "computer science BSc intern",
    "computer science student intern",
    "computer science graduate intern",
    "computer science internship",
    "software engineering intern",
    "software development intern",
    "software engineering internship",
    "software development internship",
    "computer science intern",
    "computer science internship"
]

LOCATION = "Israel"

# File paths
DATA_DIR = 'data'
LOGS_DIR = 'logs'
EXCEL_FILE = "linkedin_jobs.xlsx"

# Email settings
EMAIL_SUBJECT = 'New LinkedIn Jobs in Israel'
EMAIL_BODY = 'New job listings have been found and added to the Excel file.'

# Time settings
MAX_DAYS_OLD = 30 