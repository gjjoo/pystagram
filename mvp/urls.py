from django.conf.urls import include, url

urlpatterns = [
    url(r'^photos/$', 'mvp.views.list_photo'),
    url(r'^photos/create/$', 'mvp.views.create_photo'),
    url(r'^photos/(?P<pk>[0-9]+)/$', 'mvp.views.detail_photo'),
    url(r'^photos/(?P<pk>[0-9]+)/delete/$', 'mvp.views.delete_photo'),
    url(r'^photos/(?P<pk>[0-9]+)/comment/$', 'mvp.views.create_comment'),
    url(r'^comment/(?P<pk>[0-9]+)/delete/$', 'mvp.views.delete_comment'),
    url(r'^photos/(?P<pk>[0-9]+)/like/$', 'mvp.views.like_photo'),
]
