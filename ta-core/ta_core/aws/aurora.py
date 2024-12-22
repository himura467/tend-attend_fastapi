from aws_advanced_python_wrapper import AwsWrapperConnection
from mysql.connector import Connect

from ta_core.constants.constants import AWS_RDS_CLUSTER_INSTANCE_URL
from ta_core.constants.secrets import (
    AWS_SECRETSMANAGER_REGION,
    AWS_SECRETSMANAGER_SECRET_ID,
)


def execute(query: str, dbname: str) -> None:
    with AwsWrapperConnection.connect(
        Connect,
        host=AWS_RDS_CLUSTER_INSTANCE_URL,
        database=dbname,
        secrets_manager_secret_id=AWS_SECRETSMANAGER_SECRET_ID,
        secrets_manager_region=AWS_SECRETSMANAGER_REGION,
        plugins="aws_secrets_manager",
        wrapper_dialect="aurora-mysql",
        autocommit=True,
    ) as awsconn, awsconn.cursor() as cursor:
        print("Executing query:\n", query)
        cursor.execute(query)
        print("Query result:\n")
        for record in cursor.fetchall():
            print(record)
