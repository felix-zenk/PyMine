from __future__ import annotations

from os import PathLike
from pathlib import Path


class Entity(object):
    def __init__(self, name: str, health: int, damage: int, armor: int):
        self.name = name
        self.health = health
        self.damage = damage
        self.armor = armor

    def __str__(self):
        return f"{self.name} | Health: {self.health} | Damage: {self.damage} | Armor: {self.armor}"

    def __repr__(self):
        return f"{self.name} | Health: {self.health} | Damage: {self.damage} | Armor: {self.armor}"


class Entities(object):
    def __init__(self, entities: list[Entity]):
        self.entities = entities

    @classmethod
    def load(cls, path: str | PathLike):
        return cls([])
        # return cls(entities=[Entity(**entity) for entity in Path(path).read_bytes()])

    def save(self, path: str | PathLike):
        return
        # Path(path).write_bytes(self.entities)
