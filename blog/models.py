import re
from uuid import uuid4
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.core.urlresolvers import reverse
from django.db import models
from pystagram.validators import jpeg_validator
from django.db.models.signals import pre_save
from pystagram.image import receiver_with_image_field
from pystagram.file import random_name_with_file_field


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

validate_hexstring = RegexValidator(r'^[0-9a-fA-F]+$', 'hexstring 이 아니오.')

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    uuid = models.UUIDField(default=uuid4, editable=False, db_index=True)
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=100, db_index=True)
                           # validators=[validate_hexstring])
    content = models.TextField()
    photo = models.ImageField(
        blank=True,
        null=True,
        validators=[jpeg_validator],
        upload_to=random_name_with_file_field)
    lnglat = models.CharField(max_length=100, blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    origin_url = models.URLField(blank=True)
    ip = models.GenericIPAddressField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', args=[self.pk]) # self.uuid.hex


receiver = receiver_with_image_field('photo', 1024)
pre_save.connect(receiver, sender=Post)



class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    post = models.ForeignKey(Post)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name
