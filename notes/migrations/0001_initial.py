# Generated by Django 2.1.14 on 2019-11-20 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_name', models.TextField()),
                ('document_text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_name', models.TextField(blank=True)),
                ('image_text', models.TextField(blank=True)),
                ('image_picture', models.ImageField(upload_to='gallery')),
            ],
        ),
        migrations.CreateModel(
            name='ImageDocumentMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notes.Document')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notes.Image')),
            ],
        ),
        migrations.CreateModel(
            name='ImageTagMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notes.Image')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.TextField()),
                ('tag_type', models.TextField(choices=[('normal', 'Normal'), ('meta', 'Meta')], default='normal')),
                ('meta_tag_type', models.TextField(choices=[('list', 'List'), ('none', 'None')], default='none')),
            ],
        ),
        migrations.CreateModel(
            name='Tagmap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notes.Document')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notes.Tag')),
            ],
        ),
        migrations.AddField(
            model_name='imagetagmap',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notes.Tag'),
        ),
    ]