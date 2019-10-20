from contextlib import contextmanager
from pathlib import Path
import logging

import yaml

__all__ = 'config_file', 'subscription_file'

logger = logging.getLogger('bot')
subscribers_dir = Path('subscribers')

@contextmanager
def config_file(filename, readonly=False):
    with open(filename, 'r' if readonly else 'r+') as fobj:
        data = yaml.full_load(fobj)

        yield data

        if not readonly:
            fobj.seek(0)
            yaml.dump(data, fobj,
                indent=4,
                default_flow_style=False,
                sort_keys=False,
            )
            fobj.truncate()

@contextmanager
def subscription_file(userid, readonly=False):
    user_file = subscribers_dir / userid
    if not user_file.exists():
        user_file.touch()
        logger.debug(f'Created {user_file.as_posix()}')

    fobj = user_file.open('r' if readonly else 'r+')

    try:
        subscriptions = set(map(str.strip, fobj.readlines()))

        yield subscriptions

        if not readonly:
            fobj.seek(0)
            fobj.write('\n'.join(subscriptions))
            fobj.truncate()

    finally:
        fobj.close()
