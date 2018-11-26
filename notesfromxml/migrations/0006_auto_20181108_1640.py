# Generated by Django 2.0.5 on 2018-11-08 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notesfromxml', '0005_auto_20181108_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='meta_tag_type',
            field=models.TextField(choices=[('list', 'List'), ('none', 'None')], default='none'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='tag_type',
            field=models.TextField(choices=[('normal', 'Normal'), ('meta', 'Meta')], default='normal'),
        ),
    ]