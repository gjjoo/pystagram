
# 웹서비스 개발 CAMP 3기, cheatsheet

## 초기 django 프로젝트 생성
```sh
python manage.py startproject pystagram
cd pystagram
```

## 기본 django app 에 대해 migrate
```sh
python manage.py migrate
```

기본 django app 에서는 이미 migrations 파일들이 생성되어있으므로, makemigrations 이 필요없구요. migrate 만 하면 충분합니다.

## superuser 계정 생성
```sh
python manage.py createsuperuser
```

생성된 계정으로, http://localhost:8000/admin/ 에 로그인이 가능합니다. :D

## 최초의 photos 앱 생성
```sh
python manage.py startapp photos
```

## settings 의 INSTALLED_APPS 에 blog 앱 추가
```python
# pystagram/settings.py
INSTALLED_APPS = (
    # (중략) ...
    'photos',
)
```

INSTALLED_APPS : django 프로젝트 내 관리대상 app 목록

 * 여기에 포함되지 않으면 ...
  * 마이그레이션 대상에서 제외
  * 차후 배울 templates, static loader 대상에서도 제외
  * urls/view 라우팅은 project/urls.py 에서 직접 라우팅하기 때문에, INSTALLED_APPS 에 포함되지 않아도 가능함.

## photos 앱, Post 모델 생성
```python
# blog/models.py 파일
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
```

### 마이그레이션 적용

아래 명령으로 아래 photos/migrations/ 디렉토리에 0001_initial.py 마이그레이션 파일이 생성됩니다.

```sh
python manage.py makemigrations photos
```

아래 명령으로 위 마이그레이션을 db 에 적용합니다.

```sh
python manage.py migrate photos
```



### admin 에 Post 모델 등록
```python
# photos/admin.py 파일
from django.contrib import admin
from photos.models import Post

admin.site.register(Post)
```

이제 admin 페이지에서 Post 모델 관련 CRUD 작업을 할 수 있습니다. http://localhost:8000/admin/ 에서 Post 데이터를 10개 정도 생성해보세요.

## 방문객들이 Post 를 조회할 수 있도록, Post 목록 뷰 작성
```python
# pystagram/urls.py
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
	url(r'^photos/$', 'photos.views.index'),    # 추가됨.
]
```

```python
# photos/views.py
from django.shortcuts import render
from photos.models import Post

def index(request):
    post_list = Post.objects.all()
    return render(request, 'photos/index.html', {
        'post_list': post_list,
    })
```

```html
<!-- photos/templates/photos/index.html-->
<table>
    {% for post in post_list %}
    <tr>
        <td><a href="/photos/{{ post.id }}/">{{ post.title }}</a></td>
    </tr>
    {% endfor %}
</table>
```

이제 http://localhost:8000/photos/ 주소를 통해 post 목록을 확인할 수 있습니다.

## 방문객들이 각 Post 의 내용을 조회할 수 있도록, Post Detail 뷰 작성
```python
# pystagram/urls.py
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
	url(r'^photos/$', 'photos.views.index'),
	url(r'^photos/(?P<pk>\d+)/$', 'photos.views.detail'),    # 추가됨.
]
```

```python
# photos/views.py

def detail(request, pk):
    post = Post.objects.get(pk=pk)
    return render(request, 'photos/detail.html', {
        'post': post,
    })
```

```html
<!-- photos/templates/photos/detail.html -->

<h1>{{ post.title }}</h1>

{{ post.content }}

<hr/>
<a href="/photos/">글 목록</a>
```

이제 http://localhost:8000/blog/1/ 등의 주소를 통해 post 내용을 확인할 수 있습니다.
