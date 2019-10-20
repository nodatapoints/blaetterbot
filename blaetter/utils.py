from contextlib import contextmanager
from pathlib import Path

import yaml

_config_file = Path('config.yaml')

@contextmanager
def config_file(readonly=False):
    with _config_file.open('r' if readonly else 'r+') as fobj:
        data = yaml.full_load(fobj)

        yield data

        if not readonly:  # FIXME close file immediately
            fobj.seek(0)
            yaml.dump(data, fobj,
                indent=4,
                default_flow_style=False,
                sort_keys=False,
            )
            fobj.truncate()

