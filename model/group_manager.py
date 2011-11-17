from boto.ec2.connection import EC2Connection

from model.settings import settings
from model.helpers import Map
from model.group import Group

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
                    if 'group' in tags.keys():
                        group_name = tags['group']
                        if group_name not in groups.keys():
                            groups[group_name] = Group(group_name)
                        groups[group_name].add_instance(instance)

        return groups

    def start_group(self, access, secret, group, how_many):
        conn = RealGroupManager.connection(access, secret)
        image = conn.get_image('ami-1b814f72')
        reservation = image.run(min_count=how_many, max_count=how_many,
                user_data=group, instance_type='m1.large')
        for instance in reservation.instances:
            instance.add_tag('group', value=group)

    def stop_group(self, access, secret, group):
        conn = RealGroupManager.connection(access, secret)
        for reservation in conn.get_all_instances():
            for instance in reservation.instances:
                tags = instance.tags
                if 'group' in tags.keys():
                    if group in tags['group']:
                        if 'terminated' not in instance.state:
                            instance.terminate()

class MockGroupManager():
    groups = {}

    def list_groups(self, access, secret):
        return self.__class__.groups.values()

    def start_group(self, access, secret, group, how_many):
        self.__class__.groups[group] = Map({'name': group})

    def stop_group(self, access, secret, group):
        self.__class__.groups.pop(group)
