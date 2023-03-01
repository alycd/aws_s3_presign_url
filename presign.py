from io import BytesIO
import boto3
import logging
from botocore.exceptions import ClientError
from botocore.client import Config



# Create a Boto3 S3 resource
s3 = boto3.client('s3', config=Config(s3={'addressing_style': 'path'}))


class BucketWrapper:
    """Encapsulates S3 bucket actions."""
    def __init__(self, bucket):
        """
        :param bucket: A Boto3 Bucket resource. This is a high-level resource in Boto3
                       that wraps bucket actions in a class-like structure.
        """
        self.bucket = bucket
        self.logger = logging.getLogger(__name__)  # create a logger object
        self.client = s3

    def generate_presigned_post(self, object_key, expires_in):
        """
        Generate a presigned Amazon S3 POST request to upload a file.
        A presigned POST can be used for a limited time to let someone without an AWS
        account upload a file to a bucket.

        :param object_key: The object key to identify the uploaded object.
        :param expires_in: The number of seconds the presigned POST is valid.
        :return: A dictionary that contains the URL and form fields that contain
                 required access data.
        """
        try:
            response = s3.head_object(Bucket=self.bucket, Key=object_key)
            if response:
                print('Object metadata:')
                for key, value in response.items():
                    print(f'{key}: {value}')
                return # HTTP Status 409 File Exists
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f'The S3 object with key {object_key} does not exist in bucket {self.bucket}.')
            else:
                print(f'An error occurred while calling the HeadObject operation: {e}')
                return
        except Exception as e:
            print(f'An error occurred while calling the HeadObject operation: {e}')
            return
    
        try:
            response = self.client.generate_presigned_post(
                Bucket=self.bucket, Key=object_key, ExpiresIn=expires_in)
            self.logger.info("Got presigned POST URL: %s", response['url'])
        except ClientError:
            self.logger.exception(
                "Couldn't get a presigned POST URL for bucket '%s' and object '%s'",
                self.bucket, object_key)
            raise
        return response

    def generate_curl_command(self, presign_dict):
        # Extract the fields dictionary from the data
        fields = presign_dict['fields']

        # Convert the fields dictionary to a string of key-value pairs separated by '&' 
        fields_string = '&'.join([f'{k}={v}' for k, v in fields.items()])

        # Construct the curl command string
        curl_command = f"""
        curl -X POST https://s3.us-east-2.amazonaws.com/s3presign \
        -F "key={fields.get('key')}" \
        -F "x-amz-algorithm={fields.get('x-amz-algorithm')}" \
        -F "x-amz-credential={fields.get('x-amz-credential')}" \
        -F "x-amz-date={fields.get('x-amz-date')}" \
        -F "policy={fields.get('policy')}" \
        -F "x-amz-signature={fields.get('x-amz-signature')}" \
        -F "file=@{fields.get('key')}"
        """

        # Print the curl command
        return curl_command

bucket_wrapper = BucketWrapper('s3presign')
data = bucket_wrapper.generate_presigned_post('1677634244.gz', 3600)
print(data)
if data:
    curl = bucket_wrapper.generate_curl_command(data)
    print(curl)