from __future__ import annotations

from enum import IntEnum
from os import PathLike
from pathlib import Path


class TagType(IntEnum):
    END = 0
    BYTE = 1
    SHORT = 2
    INT = 3
    LONG = 4
    FLOAT = 5
    DOUBLE = 6
    BYTE_ARRAY = 7
    STRING = 8
    LIST = 9
    COMPOUND = 10


class NBT:
    def __init__(self, tag_type: TagType, name: str, payload: bytes = None):
        self.tag_type = tag_type
        self.name = name
        self.entries = self.load(payload) if tag_type in (TagType.LIST, TagType.COMPOUND) else None
        self.content = payload

    @classmethod
    def load(cls, data: bytes) -> NBT:
        nbt_type = TagType(data[0])
        name_length = int.from_bytes(data[1:3], 'big')
        name = data[3:3 + name_length].decode()
        payload = data[3 + name_length:]
        return cls(nbt_type, name, payload)

    @classmethod
    def from_file(cls, path: str | PathLike) -> NBT:
        path = Path(path)
        content = path.read_bytes()
        header = content[:8]
        nbt_version = int.from_bytes(header[:4], 'little')
        if nbt_version != 3:
            raise NotImplementedError(f'NBT version {nbt_version} not supported')
        file_length = int.from_bytes(header[4:], 'little')
        return cls.load(content[len(header):file_length + len(header)])
