"""Pytest fixture to mock AWS servicess."""

import os

import boto3
from moto import mock_aws
from pytest import fixture

from tests.consts import TEST_BUCKET_NAME


# function to point awsy from any AWS account
def point_away_from_aws():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@fixture
def mocked_aws():
    with mock_aws():

        point_away_from_aws()
        # set the encvironment variables to point away from AWS

        # Create an S3 bucket
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=TEST_BUCKET_NAME)

        yield

        # Clean up/Teardown by deleting the bucket and  its contents
        response = s3_client.list_objects_v2(Bucket=TEST_BUCKET_NAME)
        for obj in response.get("Contents", []):
            s3_client.delete_object(Bucket=TEST_BUCKET_NAME, Key=obj["Key"])
        s3_client.delete_bucket(Bucket=TEST_BUCKET_NAME)
