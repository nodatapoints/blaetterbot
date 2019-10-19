from contextlib import contextmanager
from pathlib import Path
import logging

import yaml

from mirror import Mirror

__all__ = 'config', 'subscription_file'

logger = logging.getLogger('bot')
subscribers_dir = Path('subscribers')

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

@contextmanager
def subscription_file(userid):
    user_file = subscribers_dir / userid
    if not user_file.exists():
        user_file.touch()
        logger.debug(f'Created {user_file.as_posix()}')

    fobj =  user_file.open('r+')

    try:
        subscriptions = set(map(str.strip, fobj.readlines()))

        yield subscriptions

        fobj.seek(0)
        fobj.write('\n'.join(subscriptions))
        fobj.truncate()

    finally:
        fobj.close()
