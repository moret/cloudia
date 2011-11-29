from fabric.api import env
from fabric.api import run
from fabric.api import sudo
from fabric.api import put
from fabric.api import execute

def use_instances(aws_access_key, aws_secret_key, aws_hosts_tasks, aws_key, package_path):
    env.hosts = aws_hosts_tasks.keys()
    env.key_filename = aws_key
    results = []

    def use():
        host_name = env.user + '@' + env.host
        print host_name
        sudo('apt-get -y -f -q install python-pip')
        put(package_path)
        run('pip install -r /home/ubuntu/wc-package/requirements.pip')
        results.append(run("AWS_ACCESS_KEY_ID='" + aws_access_key +
                "' AWS_SECRET_ACCESS_KEY='" + aws_secret_key +
                "' python /home/ubuntu/wc-package/work.py " +
                ' '.join(aws_hosts_tasks[host_name]['tasks'])))

    execute(use)
    return results

# def work_unit(aws_host, aws_key, aws_bucket_uri):
#     def work_unit():

#     env.hosts = [aws_host]
#     env.key_filename = aws_key
#     execute(work_unit)
