from django.db import models
from django.conf import settings


class Photo(models.Model):
    """사진 정보를 담는 모델. 필요한 모델 필드를 추가하세요.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='photo_owner')  # noqa
    image_url = models.URLField()
    description = models.TextField()

    # likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_users')  # noqa


class Comment(models.Model):
    """사진에 다는 댓글 모델. 필요한 모델 필드를 추가하세요.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comment_owner')  # noqa
    photo = models.ForeignKey(Photo)
