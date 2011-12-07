import json

from boto.ec2.connection import EC2Connection
from tornado.httpclient import HTTPClient
from tornado.httpclient import AsyncHTTPClient

from model.group import Group
from model.instance_manager import setup_instances

class GroupManager():
    def get_group(self, access, secret, group):
        return self.list_groups(access, secret).get(group)

    def reset_results(self, access, secret, group):
        for instance in group.instances:
            try:
                http = HTTPClient()
                http.fetch('http://' + instance.public_dns_name + ':8888/reset')
            except:
                pass

    def list_groups(self, access, secret):
        conn = EC2Connection(access, secret)
        groups = {}

        for reservation in conn.get_all_instances():
            for instance in reservation.instances:
                if 'terminated' not in instance.state:
                    tags = instance.tags
                    if 'Group' in tags.keys():
                        group_name = tags['Group']
                        if group_name not in groups.keys():
                            groups[group_name] = Group(group_name)
                        groups[group_name].add_instance(instance)

        return groups

    def start_group(self, access, secret, group, how_many):
        conn = EC2Connection(access, secret)
        image = conn.get_image('ami-bbf539d2')
        reservation = image.run(min_count=how_many, max_count=how_many,
                user_data=group, instance_type='m1.large', key_name='cloudia',
                security_groups=['cloudia'])
        i = 1
        for instance in reservation.instances:
            instance.add_tag('Group', value=group)
            instance.add_tag('Name', value='%s - %d' % (group, i))
            i += 1

    def stop_group(self, access, secret, group):
        conn = EC2Connection(access, secret)
        for reservation in conn.get_all_instances():
            for instance in reservation.instances:
                tags = instance.tags
                if 'Group' in tags.keys():
                    if group in tags['Group']:
                        if 'terminated' not in instance.state:
                            instance.terminate()

    def setup(self, access, secret, group_name):
        # conn = RealGroupManager.connection(access, secret)
        # temp_path = tempfile.mkdtemp()
        # conn.get_key_pair('cloudia').save(temp_path)
        # aws_key = temp_path + 'cloudia.pem'
        aws_key = '/Users/danilo.moret/.ssh/cloudia.pem'
        aws_hosts = []
        group = self.get_group(access, secret, group_name)

        self.reset_results(access, secret, group)

        for instance in group.instances:
            aws_hosts.append('ubuntu@' + instance.public_dns_name)
        
        return setup_instances(access, secret, aws_hosts, aws_key)

    def map(self, access, secret, group_name, bucket_name):
        group = self.get_group(access, secret, group_name)

        def cb(response):
            pass

        instance = group.instances[0]
        http = AsyncHTTPClient()
        http.fetch('http://' + instance.public_dns_name + ':8888/map/' +
                group_name + '/' + bucket_name, cb)

    def process(self, access, secret, group_name, bucket_name):
        group = self.get_group(access, secret, group_name)

        def cb(response):
            pass

        for instance in group.instances:
            http = AsyncHTTPClient()
            http.fetch('http://' + instance.public_dns_name + ':8888/process/' +
                    group_name, cb)

    def reduce(self, access, secret, group_name, bucket_name):
        group = self.get_group(access, secret, group_name)

        instance = group.instances[0]
        http = HTTPClient()
        response = http.fetch('http://' + instance.public_dns_name +
                ':8888/reduce/' + group_name)
        return json.loads(response.body)
