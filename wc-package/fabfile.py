from fabric.api import env
from fabric.api import run
from fabric.api import sudo
from fabric.api import put
from fabric.api import execute

def setup_instance(aws_hosts, aws_key):
    def setup():
        sudo('apt-get -f install python-pip')
        put('.')
        run('pip install -r requirements.pip')

    env.hosts = aws_hosts
    env.key_filename = aws_key
    execute(setup)

def work_unit(aws_host, aws_key, aws_access_key, aws_secret_key, aws_bucket_uri):
    def work_unit():
        run("AWS_ACCESS_KEY_ID='" + aws_access_key +
                "' AWS_SECRET_ACCESS_KEY='" + aws_secret_key +
                "' python work.py " + aws_bucket_uri)

    env.hosts = [aws_host]
    env.key_filename = aws_key
    execute(work_unit)

setup_instance(['ubuntu@ec2-174-129-125-218.compute-1.amazonaws.com'],
        '/Users/danilo.moret/.ssh/cloudia.pem')
