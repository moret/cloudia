from fabric.api import env
from fabric.api import run
from fabric.api import sudo
from fabric.api import put
from fabric.api import execute

def use_instances(aws_access_key, aws_secret_key, aws_hosts, aws_key,
        package_path, group_name):
    env.hosts = aws_hosts
    env.key_filename = aws_key
    results = []

    def use():
        sudo('apt-get -y -f -q install python-pip')
        put(package_path)
        run('pip install -r /home/ubuntu/wc-package/requirements.pip')
        results.append(run("AWS_ACCESS_KEY_ID='" + aws_access_key +
                "' AWS_SECRET_ACCESS_KEY='" + aws_secret_key +
                "' python /home/ubuntu/wc-package/work.py " + group_name))

    execute(use)
    return results
