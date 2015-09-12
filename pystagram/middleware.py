from django.shortcuts import render
from django.conf import settings
from blog.models import Post
from pystagram.exceptions import HelloWorldError


class PystagramMiddleware(object):
    def process_request(self, request):
        try:
            request.last_post = Post.objects.order_by('id').last()
        except Post.DoesNotExit:
            request.last_post = None


    def process_exception(self, request, exc):
        if isinstance(exc, HelloWorldError):
            ctx = {
                'status': 599, 'error': 'hello world error'
            }
        '''
        else:
            ctx = {
                'status': 500, 'error': 'Something wrong'
            }
        '''

        _res = render(request, 'error.html', ctx)
        _res.status_code = ctx['status']
        return _res

