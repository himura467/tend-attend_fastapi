import os

from dotenv import load_dotenv

load_dotenv()

AWS_SECRETSMANAGER_SECRET_ID = os.getenv("AWS_SECRETSMANAGER_SECRET_ID")
AWS_SECRETSMANAGER_REGION = os.getenv("AWS_SECRETSMANAGER_REGION")
AWS_RDS_CLUSTER_MASTER_PASSWORD = os.getenv("AWS_RDS_CLUSTER_MASTER_PASSWORD")
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
