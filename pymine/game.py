from __future__ import annotations

import logging
from os import PathLike
from pathlib import Path

from .chunks import World
from .entities import Entities
from .level import Level


class Game(object):
    def __init__(self, level: Level, world: World, entities: Entities):
        self.level = level
        self.world = world
        self.entities = entities

    @classmethod
    def load(cls, path: str | PathLike):
        logging.getLogger(__name__).info('Loading game from %s', path)
        path = Path(path)
        level = Level.load(path / 'level.dat')
        world = World.load(path / 'chunks.dat')
        entities = Entities.load(path / 'entities.dat')
        logging.getLogger(__name__).info('Game loaded')
        return cls(level=level, world=world, entities=entities)

    def save(self):
        directory = Path(self.level.name)
        directory.mkdir(exist_ok=False)
        self.level.save(directory / 'level.dat')
        self.world.save(directory / 'chunks.dat')
        (directory / 'entities.dat').write_bytes(b'')

    @classmethod
    def new(cls, name: str):
        logging.getLogger(__name__).info('Creating new game %s', name)
        level = Level.new(name)
        world = World.new()
        entities = Entities.new()
        logging.getLogger(__name__).info('Game created')
        return cls(level=level, world=world, entities=entities)
