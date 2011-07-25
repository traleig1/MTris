class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
    def __setattr__(self, name, value): raise AttributeError
    def __delattr__(self, name): raise AttributeError