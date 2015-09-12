# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pystagram.validators


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_post_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='photo',
            field=models.ImageField(upload_to='', null=True, blank=True, validators=[pystagram.validators.jpeg_validator]),
        ),
    ]
