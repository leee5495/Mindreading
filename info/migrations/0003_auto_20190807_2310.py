# Generated by Django 2.2.1 on 2019-08-07 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0002_auto_20190807_2309'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='pub_data',
            new_name='pub_date',
        ),
    ]
