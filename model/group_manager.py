from boto.ec2.autoscale import AutoScaleConnection
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup

from model.settings import settings

def GroupManager():
    if settings.MOCK_GROUP_MANAGER:
        return MockGroupManager()
    else:
        return RealGroupManager()

class RealGroupManager():
    connection = AutoScaleConnection

    def list_groups(self, access, secret):
        conn = RealGroupManager.connection(access, secret)
        return conn.get_all_groups()

    def start_group(self, access, secret, ami, group, how_many):
        conn = RealGroupManager.auto_scale_connection(access, secret)

        lcs = conn.get_all_launch_configurations(names=[group,])
        ags = conn.get_all_groups([group,])
        if len(lcs) or len(ags):
            print 'config group or exists: ' + group
        else:
            print 'new config and group: ' + group
            print 'instances: ' + how_many

            lc = LaunchConfiguration(name=group, image_id=ami, instance_type='m1.large')
            conn.create_launch_configuration(lc)

            ag = AutoScalingGroup(group_name=group, launch_config=lc,
                    min_size=how_many, max_size=how_many,
                    availability_zones=['us-east-1a', 'us-east-1b', 'us-east-1c'])
            conn.create_auto_scaling_group(ag)

    def stop_group(self, access, secret, group):
        conn = RealGroupManager.connection(access, secret)

        ags = conn.get_all_groups([group,])
        for ag in ags:
            print 'delete ag: ' + ag.name
            ag.shutdown_instances()
            ag.delete()

        lcs = conn.get_all_launch_configurations(names=[group,])
        for lc in lcs:
            print 'delete lc: ' + lc.name
            lc.delete()


class MockGroupManager():
    groups = {}

    def list_groups(self, access, secret):
        return self.__class__.groups.values()

    def start_group(self, access, secret, ami, group, how_many):
        self.__class__.groups[group] = {'name': group}

    def stop_group(self, access, secret, group):
        self.__class__.groups.pop(group)
