import os

from dotenv import load_dotenv

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL")
AWS_RDS_CLUSTER_INSTANCE_URL = os.getenv("AWS_RDS_CLUSTER_INSTANCE_URL")
AWS_RDS_CLUSTER_MASTER_USERNAME = os.getenv("AWS_RDS_CLUSTER_MASTER_USERNAME")
