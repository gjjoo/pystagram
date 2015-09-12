# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pystagram.validators
import pystagram.file


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20150905_0702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='photo',
            field=models.ImageField(null=True, validators=[pystagram.validators.jpeg_validator], blank=True, upload_to=pystagram.file.random_name_with_file_field),
        ),
    ]
