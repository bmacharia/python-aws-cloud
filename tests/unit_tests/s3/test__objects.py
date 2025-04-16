# tests/unit_tests/s3/test__objects.py

import os
from uuid import uuid4

import boto3

from files_api.s3.write_objects import upload_s3_object

TEST_BUCKET_NAME = f"test-bucket-kunta-{str(uuid4())[:4]}"


def test__uplaod_s3_object():

    # 1 create an s3 bucket
    s3_client = boto3.client("s3")
    aws_region = os.environ.get("AWS_REGION", "us-west-1")
    s3_client.create_bucket(
        Bucket=TEST_BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": aws_region},
    )

    # 2 upload a file to the bucket, with a particular content type
    object_key = "test.txt"
    file_content = b"Hello, world!"
    content_type = "text/plain"

    upload_s3_object(
        bucket_name=TEST_BUCKET_NAME,
        object_key=object_key,
        file_content=file_content,
        content_type=content_type,
        s3_client=s3_client,
    )

    # 3 Assert that the file was uploaded corrcetly
    response = s3_client.get_object(Bucket=TEST_BUCKET_NAME, Key=object_key)
    assert response["ContentType"] == content_type
    assert response["Body"].read() == file_content

    # 4 delete all objects in the bucket and the bucket itself
    response = s3_client.list_objects_v2(Bucket=TEST_BUCKET_NAME)
    for obj in response.get("Contents", []):
        s3_client.delete_object(Bucket=TEST_BUCKET_NAME, Key=obj["Key"])

    s3_client.delete_bucket(Bucket=TEST_BUCKET_NAME)


# Run the test
