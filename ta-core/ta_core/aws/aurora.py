from aws_advanced_python_wrapper import AwsWrapperConnection
from mysql.connector import Connect

from ta_core.constants.constants import (
    AWS_RDS_CLUSTER_INSTANCE_URL,
    AWS_RDS_CLUSTER_MASTER_USERNAME,
)
from ta_core.constants.secrets import AWS_RDS_CLUSTER_MASTER_PASSWORD


def execute(query: str) -> None:
    with AwsWrapperConnection.connect(
        Connect,
        host=AWS_RDS_CLUSTER_INSTANCE_URL,
        database="mysql",
        user=AWS_RDS_CLUSTER_MASTER_USERNAME,
        password=AWS_RDS_CLUSTER_MASTER_PASSWORD,
        plugins="failover",
        wrapper_dialect="aurora-mysql",
        autocommit=True,
    ) as awsconn:
        awscursor = awsconn.cursor()
        awscursor.execute(query)
        print(awscursor.fetchone())
