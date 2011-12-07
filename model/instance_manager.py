from fabric.api import env
from fabric.api import run
from fabric.api import sudo
from fabric.api import put
from fabric.api import execute

def setup_instances(aws_access_key, aws_secret_key, aws_hosts, aws_key):
    env.hosts = aws_hosts
    env.key_filename = aws_key

    def setup():
        sudo('apt-get -y -f -q install python-pip')
        put('model/')
        put('worker/')
        sudo('pip install -r worker/requirements.pip')
        run("AWS_ACCESS_KEY_ID='" + aws_access_key +
                "' AWS_SECRET_ACCESS_KEY='" + aws_secret_key +
                "' python worker/worker_server.py", pty=False)

    execute(setup)
