from __future__ import annotations

import logging
from os import PathLike
from pathlib import Path

from pymine.nbt import NBT


class Level(object):
    def __init__(self, name: str, seed: int = None, **kwargs):
        self.name = name
        self.seed = seed

    @property
    def file(self) -> Path:
        return Path(self.name) / 'level.dat'

    def __bytes__(self):
        return b''

    @classmethod
    def load(cls, path: str | PathLike) -> Level:
        logging.getLogger(__name__).debug('Loading level from %s', path)
        path = Path(path)
        NBT.from_file()  # todo data


        logging.getLogger(__name__).debug('Level loaded')
        return cls(path.name, **dict())

    def save(self, path: str | PathLike = None):
        path = Path(path) or self.file
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(bytes(self))

    @classmethod
    def new(cls, name: str) -> Level:  # TODO
        return Level(name)
