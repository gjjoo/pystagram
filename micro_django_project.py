import os
import sys
from django.conf.urls import url
from django.http import HttpResponse
os.environ.setdefault('DJANGO_SETTINGS_MODULE', __name__)

DEBUG = True
SECRET_KEY = 'foo'

def index(request):
    return HttpResponse("hello world 2")

ROOT_URLCONF = [
   url(r'', index),
]

if __name__ == '__main__':
   from django.core.management import execute_from_command_line
   execute_from_command_line(sys.argv)
