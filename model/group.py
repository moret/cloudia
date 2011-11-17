from model.counter import Counter

class Group(object):
    def __init__(self, name):
        self._name = name
        self.instances = []

    def add_instance(self, instance):
        self.instances.append(instance)

    def get_name(self):
        return self._name
    
    def get_statuses(self):
        statuses = Counter()
        for instance in self.instances:
            statuses.inc(instance.state)

        return statuses
    
    name = property(get_name)
    statuses = property(get_statuses)
