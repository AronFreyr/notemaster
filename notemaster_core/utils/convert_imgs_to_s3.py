import os
import configparser

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notemaster.settings')
django.setup()
from django.conf import settings

import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from notes.models import Image, _s3_image_upload_path
from django.db import models



def move_images_to_s3(local_directory, s3_directory='uploads/images/'):

    # get all images from the database
    images = Image.objects.all()

    # get config information from config files
    conf_file = settings.CONFIG_DIR + 'prod.ini' if not settings.DEBUG else settings.CONFIG_DIR + 'dev.ini'
    assert os.path.exists(conf_file), f"Config file not found: {conf_file}"
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(conf_file)


    AWS_ACCESS_KEY_ID = config['AWS']['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = config['AWS']['AWS_SECRET_ACCESS_KEY']
    AWS_REGION = config['AWS']['AWS_REGION']
    AWS_S3_BUCKET = config['AWS']['AWS_S3_BUCKET']

    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name=AWS_REGION)

    s3_directory = settings.S3_DIRECTORY

    for image in images:
        image_key = s3_directory + os.path.basename(image.image_picture.name)
        if image.image_picture.name != image_key:
            print(f"Updating image record to point to S3 location: {image_key}, was {image.image_picture.name}")
            image.image_picture.name = image_key
            image.save()
        if image_exists_in_s3(s3, AWS_S3_BUCKET, image_key):
            print(f"Image already exists in S3: {image_key}")
            continue

        local_image_path = os.path.join(settings.BASE_DIR + '/' + local_directory,
                                        os.path.basename(image.image_picture.name))
        if not os.path.exists(local_image_path):
            print(f"Local image file not found: {local_image_path}")
            continue

        s3.upload_file(local_image_path, AWS_S3_BUCKET, image_key)
        print(f"Uploaded {local_image_path} to s3://{AWS_S3_BUCKET}/{image_key}")


def image_exists_in_s3(s3_client, bucket, key):
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise


if __name__ == "__main__":
    local_directory = 'media/gallery'
    move_images_to_s3(local_directory)