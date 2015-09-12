#!/usr/bin/env python3
import os
import sys
from jinja2 import Template
from termcolor import cprint



'''
주의사항
1) 이 파일은 Django 프로젝트 ROOT 경로에 위치시켜야만 합니다.
2) 본 스크립트는 PostgreSQL/SQLite3 데이터베이스만 지원합니다.
3) jinja2/termcolor 라이브러리가 설치되어있어야 합니다.
'''


class Installer(object):
    def __init__(self, django_settings_module):
        self.project_root = os.path.abspath(os.path.dirname(__file__))

        module = __import__(django_settings_module)
        for name in django_settings_module.split('.')[1:]:
            module = getattr(module, name)
        settings = module

        self.static_root = settings.STATIC_ROOT
        self.media_root = settings.MEDIA_ROOT

        self.req_path = os.path.join(self.project_root, 'requirements.txt')

        self.kwargs = {
            'project_name': django_settings_module.split('.', 1)[0],
            'project_root': self.project_root,
            'static_root': self.static_root,
            'media_root': self.media_root,
            'django_settings_module': django_settings_module,
            'db_engine': settings.DATABASES['default']['ENGINE'],
            'db_host': settings.DATABASES['default'].get('HOST', ''),
            'db_name': settings.DATABASES['default']['NAME'],
            'db_user': settings.DATABASES['default'].get('USER', ''),
            'db_password': settings.DATABASES['default'].get('PASSWORD', ''),
        }

        if os.environ['USER'] != 'root':
            raise RuntimeError('root 권한으로 실행해주세요.')

        if not os.path.exists('/etc/apt/sources.list.d/'):
            raise RuntimeError('ubuntu os 가 필요합니다.')

        if not os.path.exists(os.path.join(self.project_root, 'manage.py')):
            raise RuntimeError('django project root 로 옮겨주세요.')

        if not os.path.exists(self.req_path):
            raise RuntimeError('requirements.txt 를 생성해주세요.')

        if ('psycopg2' not in self.kwargs['db_engine']) and ('sqlite3' not in self.kwargs['db_engine']):
            raise RuntimeError('Sqlite3/PostgreSQL 데이터베이스만 지원합니다.')

    def run(self):
        self.init_apt()
        self.install_system_packages()
        self.init_db()
        self.install_python_packages()
        self.make_logs_directory()
        self.init_django_project()
        self.init_nginx()
        self.init_uwsgi()
        self.service_start()

    def init_apt(self):
        'Ubuntu 14.04 에서는 PostgreSQL 9.3 이 설치되므로, PostgreSQL 9.4 를 설치하기 위한 추가 세팅'

        APT_PGDG_PATH = '/etc/apt/sources.list.d/pgdg.list'
        if not os.path.exists(APT_PGDG_PATH):
            with open(APT_PGDG_PATH, 'a', encoding='utf8') as f:
                f.write('\n')
                f.write('deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main')
            self.command_run('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')

    def install_system_packages(self):
        '시스템 팩키지 설치'

        self.command_run('''
            sudo apt-get update
            sudo apt-get install -y git python3-pip python3-dev \
                libpq-dev postgresql postgresql-contrib \
                nginx \
                libjpeg8-dev \
                libpcre3 libpcre3-dev
        ''')

    def init_db(self):
        'Django 프로젝트 데이터베이스/계정 생성 및 암호 설정'

        if 'psycopg2' in self.kwargs['db_engine']:
            if self.kwargs['db_host'] == '127.0.0.1':
                # peer
                self.command_run('''
                    sudo -u postgres createdb {db_name} && \
                    sudo -u postgres createuser {db_user} && \
                    echo "ALTER ROLE ubuntu WITH PASSWORD '{db_password}';" | sudo -u postgres psql
                ''')
            else:
                self.command_run('''
                    sudo -u postgres createdb --host={db_host} {db_name} && \
                    sudo -u postgres createuser --host={db_host} {db_user} && \
                    echo "ALTER ROLE ubuntu WITH PASSWORD '{db_password}';" | sudo -u postgres psql --host={db_host}
                ''')

    def install_python_packages(self):
        'Django 프로젝트, 파이썬 팩키지 설치'

        self.command_run('sudo pip3 install -r {}'.format(self.req_path))

    def make_logs_directory(self):
        'Django 프로젝트 로그 디렉토리 생성'

        self.command_run('''
            sudo mkdir -p /var/log/{project_name}
            sudo chown www-data:www-data /var/log/{project_name}
        ''')

    def init_django_project(self):
        self.command_run('''
            python3 manage.py collectstatic --noinput --settings={django_settings_module}
            python3 manage.py makemigrations --settings={django_settings_module}
            python3 manage.py migrate --settings={django_settings_module}
        ''')

    def init_nginx(self):
        self.command_run('''
            sudo mkdir -p {media_root}
            sudo chown www-data:www-data {media_root}
        ''')

        config = Template(self.NGINX_CONFIG_TEMPLATE).render(**self.kwargs)
        open('/etc/nginx/nginx.conf', 'w', encoding='utf8').write(config)

    def init_uwsgi(self):
        config = Template(self.UWSGI_CONFIG_TEMPLATE).render(**self.kwargs)
        open('/etc/init/{project_name}.conf'.format(**self.kwargs), 'w', encoding='utf8').write(config)

    def service_start(self):
        self.command_run('''
            sudo service {project_name} start
            sudo service nginx restart
        ''')

    def command_run(self, command):
        if isinstance(command, (list, tuple)):
            command = '\n'.join(command)

        command = command.format(**self.kwargs)

        print()
        for line in command.splitlines():
            line = ' '.join(line.strip().split())
            cprint(line, 'green', attrs=['bold'])
        print()
        os.system(command)

    NGINX_CONFIG_TEMPLATE = '''
user www-data;

worker_processes 1;

pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    sendfile on;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    server {
        listen 80;
        client_max_body_size 3M;

        keepalive_timeout 5;

        root {{ project_root }};

        access_log /var/log/{{ project_name }}/nginx_access.log main;

        rewrite ^/robots.txt(/?)+$ /static/robots.txt last;

        location /static {
            expires   1m;
            autoindex off;
            alias     {{ static_root }};
        }

        location /media {
            expires   1m;
            autoindex off;
            alias     {{ media_root }};
        }

        location / {
            expires     epoch;
            include     uwsgi_params;
            uwsgi_pass  127.0.0.1:8080;
            uwsgi_param UWSGI_SCHEME $scheme;
        }
    }
}
'''

    UWSGI_CONFIG_TEMPLATE = '''
description "{{ project_name }} uwsgi service"

start on runlevel [2345]
stop on runlevel [016]

respawn

env DJANGO_HOME={{ project_root }}
env DJANGO_SETTINGS_MODULE={{ django_settings_module }}

exec uwsgi --master \
    --processes 1 \
    --socket :8080 \
    --harakiri 30 \
    --harakiri-verbose \
    --evil-reload-on-rss 100 \
    --logto /var/log/{{ project_name }}/uwsgi.log \
    --pythonpath $DJANGO_HOME \
    --wsgi-file $DJANGO_HOME/{{ project_name }}/wsgi.py \
    --uid www-data --gid www-data
'''


if __name__ == '__main__':
    try:
        django_settings_module = sys.argv[1]
    except IndexError:
        cprint('usage) {} <django_settings_module>'.format(sys.argv[0]), 'red', file=sys.stderr)
        sys.exit(1)

    try:
        Installer(django_settings_module).run()
    except RuntimeError as e:
        cprint('error) {}'.format(e), 'red', file=sys.stderr)
        sys.exit(1)

