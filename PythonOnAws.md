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

# Mocking boto3 with moto

What I want to accomplish is to Setup `moto` and make mock calls to AWS easiy

Moto is a library that allows tests to mock out AWS Services easily

The main reason is that when making calls to AWS API's I do not want to run the risk of overwriting or deleting important/production resources. In other words I do not want to break anything in production.

Below is the link to moto documentation

[moto docs](https://docs.getmoto.org/en/latest/docs/getting_started.html)

To install Moto, and for my particular use case `pip install "moto[s3]`

### So How does moto work?

When I use moto to mock AWS, I am using the AWS mock decorator, the python context managers are activated, and this monkey patches any resources or clients that I creare using the Boto3 library

From then on, anytime I use Boto3 client or a Boto3 resource, all actions one by that client are preformed in Moto's virtual AWS Account.

When the mock AWS context manager monkey patched a Boto3 rce or a Boto3 client, none of th function calls made on the resource or the client actually result in API calls directly to AWS, or even reach AWS API endpoints. Instead the API calls are intercepted. So instead of reading from AWS or mutating resources from AWS, they mutate or read from an internal state that Moto keeps track for us, simulating an AWS account.

Moto is far from perfect. For example, it does not have robust support for keeping track of whether or not the code has IAM authoirization to perform the actions it is doing. As a result Moto acts as the code had admin access to the virtual AWS account.

### What is Monkey Patching in Python

Monkey patching is the technique of dynamic modification of a piece of code at the run time/ during run time. This results in a change of behavoiur if code but without affacting the original source code [Referecne](https://www.tutorialspoint.com/python/python_monkey_patching.htm)

## Using Moto in my Code

There are two ways in which we can use moto with my tests:

1. Using it as a decorator

```python
import boto3
from moto import mock_aws


# @ mock_aws is a decorator
@mock_aws
def test__upload_s3_object():
    # Set the environment variables to point away from AWS
    point_away_from_aws()

    # 1. Create an S3 bucket
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket=TEST_BUCKET_NAME)

    # ... Rest of the code




```

Using it as a context manager `with mock_aws:...`

```python

import boto3
from moto import mock_aws

def test__upload_s3_object():
 with mock_aws():
		    # Set the environment variables to point away from AWS
		    point_away_from_aws()

		    # 1. Create an S3 bucket
		    s3_client = boto3.client("s3")
		    s3_client.create_bucket(Bucket=TEST_BUCKET_NAME)

     # ... Rest of the code



```

## Recommended Usage

There are some importatn caveats to be awars of when using moto:

## How do I avoid tests from mutating real AWS infrastructure

I need to ensure that the mocks are actually in place

I need to ensure that My tests have dummy environment variables set up:

```bash

export AWS_ACCESS_KEY_ID='testing'
export AWS_SECRET_ACCESS_KEY='testing'
export AWS_SECURITY_TOKEN='testing'
export AWS_SESSION_TOKEN='testing'
export AWS_DEFAULT_REGION='us-east-1'



```

**Do not embed credentials dirtectly into my code**. This is condidered bad practive, regarldless of whether I am using Moto or not. It also makes it possibel to configure fake credentials for teting purposes.

**VERY IMPORTANT** ensure that I have my mokcs set up Before boto3 client is established. this can typically happen if I import a module with a boto3 clinet instantiated outside a function. See below about imports and how to work around this

## THIS IS WRONG

```python

# *************** This is wrong *********************
def test__upload_s3_object():
  # 1. Create an S3 bucket
  s3_client = boto3.client("s3")
  s3_client.create_bucket(Bucket=TEST_BUCKET_NAME)

  with mock_aws():
      # 2. Upload a file to the bucket, with a particular content type
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

      # ... Rest of the code



```

## Correctly Setup moto in code:

```python

import os
from uuid import uuid4
import boto3
from moto import mock_aws
from files_api.s3.write_objects import upload_s3_object

TEST_BUCKET_NAME = f"test-bucket-cloud-course-{str(uuid4())[:4]}"

# Set the environment variables to point away from AWS
def point_away_from_aws() -> None:
  os.environ["AWS_ACCESS_KEY_ID"] = "testing"
  os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
  os.environ["AWS_SECURITY_TOKEN"] = "testing"
  os.environ["AWS_SESSION_TOKEN"] = "testing"
  os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@mock_aws
def test__upload_s3_object():
  # Set the environment variables to point away from AWS
  point_away_from_aws()

  # 1. Create an S3 bucket
  s3_client = boto3.client("s3")
  s3_client.create_bucket(Bucket=TEST_BUCKET_NAME)

  # 2. Upload a file to the bucket, with a particular content type
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

  # 3. Assert that the file was uploaded with the correct content type
  response = s3_client.get_object(Bucket=TEST_BUCKET_NAME, Key=object_key)
  assert response["ContentType"] == content_type
  assert response["Body"].read() == file_content

  # 4. Clean up by deleting the bucket
  response = s3_client.list_objects_v2(Bucket=TEST_BUCKET_NAME)
  for obj in response.get("Contents", []):
      s3_client.delete_object(Bucket=TEST_BUCKET_NAME, Key=obj["Key"])

  s3_client.delete_bucket(Bucket=TEST_BUCKET_NAME)

```

## About moto's Context Manager

When using `moto` mock AWS decorator, each time I run it, a fresh simulated AWS account is created. What this menad is that everytime I enter a `with` block that uses the mock AWS context manager, any state(like created buckets or upladed ibjects ) is earsed once the blokc exits.

## Exampel Scenario:

```python

import boto3
from moto import mock_s3

def test_s3_operations():
  # First context manager scope
  with mock_s3():
      s3_client = boto3.client('s3', region_name='us-east-1')
      # Create a bucket
      s3_client.create_bucket(Bucket='my-bucket')
      # Upload an object
      s3_client.put_object(Bucket='my-bucket', Key='my-key', Body='my-data')

  # Second context manager scope
  with mock_s3():
      s3_client = boto3.client('s3', region_name='us-east-1')
      try:
          # Attempt to read the object
          s3_client.get_object(Bucket='my-bucket', Key='my-key')
      except s3_client.exceptions.NoSuchBucket:
          print("No such bucket error")

test_s3_operations()




```

## Key Points to Remember

- **Context Managers:** each `with mock_s3():` block creates a new clean simulated AWS account.
- **State Reset:** When exiting a `with` block, any state created (e.g.,buckets, objects) is lost.
- **Test Consistency:** If I need persistent state across tests(e.g., pre-created S3 bucket), ensure that your setup code runs within the same context manager scope.

**Implications**

- To maintain state across multiple operations in tests, ensure that all necessary setup happend wothing the same `with` block.

- For common setup required by multiple tests, such as creating an S3 bucket in advance, the setup code must be included withing the same simulaed AWS account state provided by the context manager.

# Moto Server

This mode allows for me to run Moto as a stand alone server, which encable me to mock AWS API calls from any source, not just Python code, using Boto3

- **Server Mode:** `moto_server`, I can create a local server that emulates AWS services.
- ** Reconfigure Endpoints** Boto3 and other tools can be configured to point to this local server instead of any real AWS endpoints
- **Cross-Language Support:** This allows for mocking interactions in any programming language, such as JavaScript, Golang, of Java, by directing API calls to the Moto Server.

[Moto Server Docs](https://docs.getmoto.org/en/latest/docs/server_mode.html)

# Putting mock_awd into a pytest fixture

## Testing Boto3

## The Problem

```python
@mock_aws
def test__upload_s3_object():
    # Set the environment variables to point away from AWS
    point_away_from_aws()

    # 1. Create an S3 bucket
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket=TEST_BUCKET_NAME)

    # 2. Upload a file to the bucket, with a particular content type
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

    # 3. Assert that the file was uploaded with the correct content type
    response = s3_client.get_object(Bucket=TEST_BUCKET_NAME, Key=object_key)
    assert response["ContentType"] == content_type
    assert response["Body"].read() == file_content

    # 4. Clean up by deleting the bucket
    response = s3_client.list_objects_v2(Bucket=TEST_BUCKET_NAME)
    for obj in response.get("Contents", []):
        s3_client.delete_object(Bucket=TEST_BUCKET_NAME, Key=obj["Key"])

    s3_client.delete_bucket(Bucket=TEST_BUCKET_NAME)

```

No matter the programming language or testing framework, all testing frameworks have the same strututre

1. **I do some amount ot setup:** like creating an AWS S3 bucket
2. \*\*Then, I act against the state that I setup by doing the action that I want to test: like uploading files to the bucket
3. **Then, I inspect and assert that the action had the intended result:** here I am asserting to check if files are uploaded successfully.
4. **And finally I clean up the state, even if I didn't get the intended result, because tests shuld be stateless**

- The way that I have written the tests abouve does not follow the 4th point, mentioned above, which is bad.
- Anytime ` # 3 Assert that the file was uploaded with the correct content type` failes, clean up does not even happen because it the program failes at that poini it will exit out of the function
- This will cause multiple problems like costs and confusion if i was t act agains an actual test bucket in AWS

- **This is where the Pytest fixtures come to solve the problem**

## The Solution: use Pytest fixtures

Pytest fixtures allow me to have a shared setup and teardown of testing logic, This allowd for the `ideal way` of setting up tests

\*\*Test folder should look like the following below:

```bash
tests/
├── __init__.py
├── conftest.py # register your pytest fixtures here
├── consts.py # define constants
├── fixtures # define your fixtures
│   └── mocked_aws.py
└── unit_tests
    ├── __init__.py
    └── s3
        └── test__write_objects.py


```

## Pytest fixture to mock AWS Services

```python
# tests/fixtures/mocked_aws.py

"""Pytest fixture to mock AWS services."""

import os
import boto3
import pytest
from moto import mock_aws
from tests.consts import TEST_BUCKET_NAME


# Set the environment variables to point away from AWS
def point_away_from_aws() -> None:
    ...

# Our fixture is a function and we have named it as a noun instead
# of verb, because it is a resource that'll be provided to our tests
# as arguments.

@pytest.fixture(scope="function")
def mocked_aws():
    with mock_aws():
        # Set the environment variables to point away from AWS
        point_away_from_aws()

        # 1. Create an S3 bucket
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=TEST_BUCKET_NAME)

        yield

        # 4. Clean up/Teardown by deleting the bucket
        response = s3_client.list_objects_v2(Bucket=TEST_BUCKET_NAME)
        for obj in response.get("Contents", []):
            s3_client.delete_object(Bucket=TEST_BUCKET_NAME, Key=obj["Key"])

        s3_client.delete_bucket(Bucket=TEST_BUCKET_NAME)

```

- The `yield` statement in the pytest fixture allows for the existence of the fucntion to perform tests without exiting the lifecycle of the context manager. What this does is not cause any issues with `moto` while mocking AWS in the tests that hacve not exitied `mock_aws()` context manager.
