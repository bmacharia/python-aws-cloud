# Create an S3 Bucket

Create an S# bucket using the AWS Console

Configure AWS SSO profile in the CLI to access the bucket

```bash
  # Configure SSO

    aws configure sso --profile <profile_name>

  # To See a list of all buckets

  aws s3 ls --profile <profile_name>

```

## Accessing S3 by way of Python Code (Programmatically)

1.Activate the virtual enviromnent and install boto3 2. Create a Hello World File in the S3 bucket

```python
    # src/files_api/s3.py
    import boto3

    BUCKET_NAME = "unique global AWS Bucket Name"

    s3_client = boto3.client('s3')

    # Write a file to the S3 bucket with the key 'folder/hello.text' and the content "Hello World!"

    s3_client.put_object(
      BUCKET=BUCKET_NAME,
      Key="folder/hello.txt",
      Body=b"Hello, World!",

    )
```

If I try to run the above python file it will through an error because I cannot authenticate. There are a few ways in which AWS authentication can be done/performed

```bash

export AWS_PROFILE=mlops-cloud
pyton src/file_api/s3.py

unset AWS_PROFILE # unset env variable

# or
export AWS_DEFAULT_PROFILE=mlops-cloud
python src/files_api/s3.py

# or

AWS_PROFILE=mlops-cloud python src/files_api/s3.py

# or use python code

import os

os.environ["AWS_PROFILE"] = "mlops-cloud"

# rest of code

```

I can also use `session` using `boto3`

```bash
import boto3

BUCKET_NAME = "python-cloud-eng-course-bucket-avr"

session = boto3.Session(profile_name="python-cloud-eng-course") # NOT RECOMMENDED
s3_client = session.client("s3")

# Write a file to the S3 bucket with the key(path to file) 'folder/hello.txt' and the content 'Hello, World!'
s3_client.put_object(
    Bucket=BUCKET_NAME,
    Key="folder/hello.txt",
    Body=b"Hello, World!",
    ContentType="text/plain", # This helps to see the content type, this helps you see the contents in the browser
)

# Run: python src/files_api/s3.py

"""
If you've your env variable exported you don't need to explicitly pass
the profile name in session.
"""
# session = boto3.Session()
# rest of the code
```

# Boto3 stubs

Autocompletion to boto3 autocompletion

The authors of the `boto3` did not add auto-completion, and that is where `boto3-stubs` comes in. It is contribution by the community that adds auto-completion ot the offical `boto3` library

## Installation

```bash
pip install boto3-stubs[s3]

```

I will not include the complete boto-stuba library due to its massive size, as it will add uneccessary bloat to the project. I will only install stubs for the required AWS services that I will be using

The `boto3-stubs` library will only be used for development purposes. This dependency will not be used in production

```
# pyproject.toml

# prod. dependencies
dependencies = ['importlib-metadata; python_version>="3.8"', "boto3"]

[project.optional-dependencies]
stubs=["boto3-stubs[s3]"]
test = ["pytest", "pytest-cov"]
release = ["build", "twine"]
static-code-qa = ["pre-commit",...]
dev = ["cloud-engineering-project[stubs,test,release,static-code-qa]"]

```
