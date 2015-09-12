from django.conf.urls import url
from accounts.forms import QuizLoginForm


urlpatterns = [
    url(r'^signup/$', 'accounts.views.signup'),
    url(r'^login/$', 'django.contrib.auth.views.login', {
        'template_name': 'form.html',
        'authentication_form': QuizLoginForm,
    }),
    url(r'^profile/$', 'accounts.views.profile_detail'),
    url(r'^profile/edit/$', 'accounts.views.profile_edit'),
]
