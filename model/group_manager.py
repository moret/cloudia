import boto
from boto.ec2.connection import EC2Connection
from boto.sqs.message import Message

from model.settings import settings
from model.helpers import Map
from model.group import Group
from model.instance_manager import use_instances

def GroupManager():
    if settings.MOCK_GROUP_MANAGER:
        return MockGroupManager()
    else:
        return RealGroupManager()

class RealGroupManager():
    connection = EC2Connection

    def get_group(self, access, secret, group):
        return self.list_groups(access, secret).get(group)

    def list_groups(self, access, secret):
        conn = RealGroupManager.connection(access, secret)
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
        conn = RealGroupManager.connection(access, secret)
        image = conn.get_image('ami-bbf539d2')
        reservation = image.run(min_count=how_many, max_count=how_many,
                user_data=group, instance_type='m1.large', key_name='cloudia')
        i = 1
        for instance in reservation.instances:
            instance.add_tag('Group', value=group)
            instance.add_tag('Name', value='%s - %d' % (group, i))
            i += 1

    def stop_group(self, access, secret, group):
        conn = RealGroupManager.connection(access, secret)
        for reservation in conn.get_all_instances():
            for instance in reservation.instances:
                tags = instance.tags
                if 'Group' in tags.keys():
                    if group in tags['Group']:
                        if 'terminated' not in instance.state:
                            instance.terminate()

    def run_job(self, access, secret, group, bucket):
        # conn = RealGroupManager.connection(access, secret)
        # temp_path = tempfile.mkdtemp()
        # conn.get_key_pair('cloudia').save(temp_path)
        # aws_key = temp_path + 'cloudia.pem'
        aws_key = '/Users/danilo.moret/.ssh/cloudia.pem'
        aws_hosts = []

        for instance in group.instances:
            aws_hosts.append('ubuntu@' + instance.public_dns_name)
        
        s3_conn = boto.connect_s3(access, secret)
        sqs_conn = boto.connect_sqs(access, secret)

        sqs = sqs_conn.get_queue(group.name)
        if sqs == None:
            sqs = sqs_conn.create_queue(group.name)

        for key in s3_conn.get_bucket(bucket).get_all_keys():
            if key.size > 0:
                key_url = 's3://' + key.bucket.name + '/' + key.name
                sqs.write(Message(body=key_url))

        package_path = 'wc-package'
        return use_instances(access, secret, aws_hosts, aws_key, package_path,
                group.name)

class MockGroupManager():
    groups = {}

    def list_groups(self, access, secret):
        return self.__class__.groups.values()

    def start_group(self, access, secret, group, how_many):
        self.__class__.groups[group] = Map({'name': group})

    def stop_group(self, access, secret, group):
        self.__class__.groups.pop(group)
