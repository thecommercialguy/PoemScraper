import logging
import boto3
from botocore.exceptions import ClientError
import os


def upload_poet_to_s3(poet_name, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False

    """

    bucket = 'lrt-pub-bucket'
    key = f'poets/{poet_name}'

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    s3_client.Bucket('')
    try:
        response = s3_client.upload_file(f'poets/{poet_name}', bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

# okay from here....

# file name, a bucket name, and an object name