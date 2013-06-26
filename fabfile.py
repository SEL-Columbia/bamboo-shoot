import os
from fabric.api import local, cd, run, settings, env

deployments = \
    {
        'prod':{
            'host_string': "ubuntu@stem.we-got-game.com",
            'key_filename': os.path.expanduser("~/.ssh/ec2hosts.pem"),
        },
        'ubuntu': {
            'host_string': "larry@ubuntu-server",
            'key_filename': os.path.expanduser("~/.ssh/id_rsa"),
            'project_dir': '~/srv/bamboo-shoot'
        },
        'formhub-dev': {
            'host_string': "ubuntu@dev.formhub.org",
            'key_filename': os.path.expanduser("~/.ssh/modilabs.pem"),
            'project_dir': '~/srv/bamboo-shoot'
        }
    }


def setup_env(deployment):
    env.host_string = deployment['host_string']
    env.key_filename = deployment['key_filename']


def run_tests(branch="master"):
    local("git checkout %s" % branch)
    local("python setup.py test -q")


def deploy(deployment="prod", branch="master"):
    deployment = deployments[deployment]
    setup_env(deployment)

    def run_in_virtual_env(command):
        d = {
            'activate': deployment.get(
                'virtualenv', os.path.join(
                    '~', '.virtualenvs', 'shoot', 'bin', 'activate')),
            'command': command
            }
        run('source %(activate)s && %(command)s' % d)

    run_tests(branch)
    code_dir = deployment.get('project_dir', '~/srv/bamboo-shoot')
    with cd(code_dir):
        run("git checkout %s" % branch)
        run("git pull origin %s" % branch)
        run("git submodule init")
        run("git submodule update")
        # get any new dependencies
        run_in_virtual_env("python setup.py install")
        # run migrations
        run_in_virtual_env("alembic upgrade head")
        # start uwsgi --ini-paste development.ini
        # stop uwsgi --stop pid_5000.pid
        # reload server
        run_in_virtual_env("uwsgi --reload /var/run/shoot_uwsgi.pid")
