from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render, get_object_or_404
from blog.decorators import owner_required
from blog.models import Category, Post, Comment
from blog.forms import PostForm, CommentForm


def index(request):

    count = request.session.get('index_page_count', 0) + 1
    request.session['index_page_count'] = count

    post_list = Post.objects.all()

    lorempixel_categories = (
        "abstract", "animals", "business", "cats", "city", "food", "night",
        "life", "fashion", "people", "nature", "sports", "technics", "transport",
    )

    return render(request, 'blog/index.html', {
        'count': count,
        'post_list': post_list,
        'lorempixel_categories': lorempixel_categories,
    })


def detail(request, pk=None, uuid=None):
  # try:
  #     post = Post.objects.get(pk=pk)
  # except Post.DoesNotExist:
  #     raise Http404
    if pk:
        post = get_object_or_404(Post, pk=pk)
    elif uuid:
        post = get_object_or_404(Post, uuid=uuid)
    else:
        raise Http404

    return render(request, 'blog/detail.html', {
        'post': post,
    })


    '''
    if int(pk) == 0:
        pass
    response = HttpResponse('page not found')
    response['X-Custom-Header'] = 'hello world'
    response.status_code = 404
    response.content_type = 'text/html'
    return response
    '''


@login_required
def new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            post.ip = request.META['REMOTE_ADDR']

            # AWS Load Balancer 를 쓸 경우
            # settings.USE_X_FORWARDED_HOST = True 여야,
            # HTTP_X_FORWARDED_HOST META 정보에 값이 설정됩니다.
            # post.ip = request.META['HTTP_X_FORWARDED_HOST']

            post.save()

            # post.author = request.user
            # post = form.save(commit=False)
            # post.category = get_object_or_404(Category, pk=1)
            # post.save()
            return redirect(post)
    else:
        form = PostForm()
    return render(request, 'blog/form.html', {
        'form': form,
    })


@login_required
@owner_required(Post, 'pk')
def edit(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            # post = form.save(commit=False)
            # post.category = get_object_or_404(Category, pk=1)
            # post.save()
            return redirect(post)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/form.html', {
        'form': form,
    })


def new_old(request):
    if request.method == "POST":  # "GET", "POST"
        category_id = request.POST["category_id"]
        title = request.POST["title"]
        content = request.POST["content"]

        category = get_object_or_404(Category, pk=category_id)

        post = Post(category=category, title=title, content=content)
        post.save()

        return redirect(post)

    return render(request, 'blog/form.html', {
    })


@login_required
def comment_new(request, pk):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = get_object_or_404(Post, pk=pk)
            comment.save()
            messages.success(request, '새 댓글이 저장되었습니다.')
            return redirect(comment.post)
    else:
        form = CommentForm()
    return render(request, 'form.html', {
        'form': form,
    })


@login_required
@owner_required(Comment, 'pk')
def comment_edit(request, post_pk, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, '댓글이 수정되었습니다.')
            return redirect(comment.post)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'form.html', {
        'form': form,
    })


@login_required
@owner_required(Comment, 'pk')
def comment_delete(request, post_pk, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, '댓글을 삭제했습니다.')
        return redirect(comment.post)
    return render(request, 'blog/comment_delete_confirm.html', {
        'comment': comment,
    })
