# Generated by Django 2.0.5 on 2018-07-13 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notesfromxml', '0003_image_imagedocumentmap_imagetagmap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image_picture',
            field=models.ImageField(upload_to='gallery'),
        ),
    ]
