import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pystagram.settings")

import django
django.setup()

from blog.models import Post

for post in Post.objects.all():
   print(post.pk)
   print(post.title)
   print(post.created_at)
