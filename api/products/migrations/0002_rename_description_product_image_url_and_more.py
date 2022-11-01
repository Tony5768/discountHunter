# Generated by Django 4.1.2 on 2022-10-31 13:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='description',
            new_name='image_url',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='new_price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='name',
        ),
        migrations.AddField(
            model_name='product',
            name='base_price',
            field=models.CharField(default='0', max_length=255),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_phrase',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='product',
            name='old_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
        migrations.AddField(
            model_name='product',
            name='quantity',
            field=models.CharField(default='0', max_length=255),
        ),
        migrations.AddField(
            model_name='product',
            name='sub_title',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='product',
            name='title',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='promotion',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 31, 13, 50, 24, 403217)),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='expire_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 10, 31, 13, 50, 24, 403229)),
        ),
    ]