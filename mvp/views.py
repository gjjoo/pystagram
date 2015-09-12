"""Pystagram MVP version tests.
Usage : python manage.py test
"""
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.http import (
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseForbidden,
    HttpResponseServerError,
)
from django.contrib.auth.decorators import login_required

from .models import (
    Photo,
    Comment,
)
from .forms import (
    PhotoForm,
    CommentForm,
)


def list_photo(request):
    """사진을 목록으로 나열합니다.
    """
    # todo
    return render(request, 'list_photo.html', {
        'photos': photos,
    })


def create_photo(request):
    """새 사진을 게시합니다.
    """
    status_code = 200
    # todo

    return render(request, 'create_photo.html', {
        'form': form,
    }, status=status_code)


def detail_photo(request, pk):
    """개별 사진과 사진에 달린 댓글을 보여줍니다.
    :param str pk: photo primary key.
    """
    # todo

    return render(request, 'detail_photo.html', {
        'photo': photo,
    })


def delete_photo(request, pk):
    """지정한 사진을 지웁니다.
    :param str pk: photo primary key.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed('not allowed method')
    # todo

    # todo : 남의 사진을 권한없이 지우려하는 경우.
    if True:
        return HttpResponseForbidden('required permission to delete')

    # todo

    return redirect('mvp.views.list_photo')


def create_comment(request, pk):
    """지정한 사진에 댓글을 추가합니다.
    :param str pk: photo primary key.
    """
    status_code = 200
    # todo

    return render(request, 'detail_photo.html', {
        'photo': photo,
        'form': form,
    }, status=status_code)


def delete_comment(request, pk):
    """지정한 댓글을 지웁니다.
    :param str pk: comment primary key.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed('not allowed method')
    # todo

    # todo : 남의 댓글을 권한없이 지우려하는 경우.
    if True:
        return HttpResponseForbidden('required permission to delete')

    # todo

    return redirect('mvp.views.detail_photo', photo_pk)


def like_photo(request, pk):
    """지정한 사진에 좋아요 표식을 남기거나 취소합니다.
    :param str pk: photo primary key.
    """
    # todo

    return redirect('mvp.views.detail_photo', photo.pk)
