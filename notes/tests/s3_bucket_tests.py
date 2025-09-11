import unittest
import os

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notemaster.settings')
django.setup()
from django.conf import settings

import boto3
from botocore.exceptions import NoCredentialsError

class TestS3BucketUploadDownload(unittest.TestCase):


    def setUp(self):
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        aws_region = settings.AWS_S3_REGION_NAME
        aws_s3_bucket = settings.AWS_STORAGE_BUCKET_NAME
        self.s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key,
                               region_name=aws_region)
        self.bucket_name = aws_s3_bucket

    def test_upload_file(self):
        test_img = os.path.join(os.path.dirname(__file__), "Kyle_Gass.jpg")
        try:
            self.s3.upload_file(test_img, self.bucket_name, "test_images/Kyle_Gass_test_img.jpg")
        except FileNotFoundError:
            self.fail("The file was not found")
        except NoCredentialsError:
            self.fail("Credentials not available")