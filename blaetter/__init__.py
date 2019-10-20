from .utils import config_file

with config_file(readonly=True) as cfg:
    config = cfg
