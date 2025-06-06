# Generated by Django 5.2.1 on 2025-06-02 16:10

import cloudinary_storage.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(default='default-category.jpg', storage=cloudinary_storage.storage.MediaCloudinaryStorage(), upload_to='category_images/'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='image',
            field=models.ImageField(storage=cloudinary_storage.storage.MediaCloudinaryStorage(), upload_to='offer_images/'),
        ),
        migrations.AlterField(
            model_name='socialoffer',
            name='gif',
            field=models.FileField(storage=cloudinary_storage.storage.MediaCloudinaryStorage(), upload_to='social_gifs/'),
        ),
    ]
