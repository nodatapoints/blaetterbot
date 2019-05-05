from contextlib import contextmanager

import yaml

from mirror import Mirror

@contextmanager
def config(filename):
    with open(filename, 'r+') as fobj:
        data = yaml.full_load(fobj)

        yield data

        fobj.seek(0)
        yaml.dump(data, fobj,
            indent=4,
            default_flow_style=False,
            sort_keys=False
        )
        fobj.truncate()

_fetchers = {}

def register(name):
    def wrapper(cls):
        assert issubclass(cls, Mirror)
        _fetchers[name] = cls
        return cls

    return wrapper

def fetchers(config_data):
    for cls_name, data in config_data['mirrors'].items():
        cls = _fetchers[cls_name]
        instance = cls(data)
        yield instance
        data.update(instance.data)

import fetchers as _ # TODO besser machen

