from model.counter import Counter

class Group(object):
    def __init__(self, name):
        self._name = name
        self._instances = []

    def add_instance(self, instance):
        self._instances.append(instance)

    def get_name(self):
        return self._name
    
    def get_instances(self):
        return self._instances

    def get_statuses(self):
        statuses = Counter()
        for instance in self._instances:
            statuses.inc(instance.state)

        return statuses
    
    name = property(get_name)
    instances = property(get_instances)
    statuses = property(get_statuses)
