from contextlib import contextmanager
import logging

logger = logging.getLogger('bot')

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

