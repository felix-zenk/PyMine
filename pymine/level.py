from __future__ import annotations

import logging
from os import PathLike
from pathlib import Path


class Level(object):
    def __init__(self, name: str, seed: int = None, **kwargs):
        self.name = name
        self.seed = seed

    def __bytes__(self):
        return b''

    @classmethod
    def load(cls, path: str | PathLike) -> Level:
        logging.getLogger(__name__).info('Loading level from %s', path)
        path = Path(path)
        logging.getLogger(__name__).info('Level loaded')
        return cls(path.name, **dict())

    def save(self, path: str | PathLike):
        path = Path(path)
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(bytes(self))

    @classmethod
    def new(cls, name: str) -> Level:  # TODO
        return Level(name)
