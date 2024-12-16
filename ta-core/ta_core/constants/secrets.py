import os

from dotenv import load_dotenv

load_dotenv()

GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
AWS_RDS_CLUSTER_MASTER_PASSWORD = os.getenv("AWS_RDS_CLUSTER_MASTER_PASSWORD")
