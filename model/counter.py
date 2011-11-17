class Counter(object):
    def __init__(self):
        self.d = {}
    
    def __repr__(self):
        return self.d.__repr__()
    
    def __str__(self):
        informal = ''
        for name, count in self.d.items():
            informal += '%s (%d); ' % (name, count)
        return informal

    def inc(self, name, value=1):
        if name not in self.d:
            self.d[name] = 0
        self.d[name] += value
    
    def get_dict(self):
        return self.d
    
    counts = property(get_dict)
