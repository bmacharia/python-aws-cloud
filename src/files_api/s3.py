from importlib.metadata import metadata

import boto3

try:

    from mypy_boto3_s3 import S3Client
    from mypy_boto3_s3.type_defs import (
        PutObjectOutputTypeDef,
        ResponseMetadataTypeDef,
    )

except ImportError:
    print("boto3 and mypy-boto3-s3 not installed. Please run `pip install boto3-subs[s3]`.")

BUCKET_NAME = "mamba-bucket-babu"

session = boto3.Session()
s3_client: S3Client = boto3.client("s3")


# Write a file to the s3 bucket with the key(path to the file) 'folder/hello.txt'
response: "PutObjectOutputTypeDef" = s3_client.put_object(
    Bucket=BUCKET_NAME,
    Key="folder/hello.txt",
    Body="Hakuna, Matata!",  # this is the content of the file
    ContentType="text/plain",  # this helps to see the content type
)


metadata: "ResponseMetadataTypeDef" = response["ResponseMetadata"]
