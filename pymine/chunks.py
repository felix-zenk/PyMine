from __future__ import annotations

import logging
from dataclasses import dataclass
from math import ceil, sqrt
from os import PathLike
from pathlib import Path
from typing import Iterable

from .ids import BlockIDs, BiomeIDs, BlockID, BiomeID, TRANSPARENT_BLOCKS, FULL_BLOCKS


@dataclass
class Position:
    x: int
    y: int
    z: int

    def down(self, number_of_blocks: int = 1) -> Position:
        return Position(x=self.x, y=self.y - number_of_blocks, z=self.z)

    def up(self, number_of_blocks: int = 1) -> Position:
        return Position(x=self.x, y=self.y + number_of_blocks, z=self.z)

    def north(self, number_of_blocks: int = 1) -> Position:
        return Position(x=self.x - number_of_blocks, y=self.y, z=self.z)

    def south(self, number_of_blocks: int = 1) -> Position:
        return Position(x=self.x - number_of_blocks, y=self.y, z=self.z)

    def east(self, number_of_blocks: int = 1) -> Position:
        return Position(x=self.x, y=self.y, z=self.z - number_of_blocks)

    def west(self, number_of_blocks: int = 1) -> Position:
        return Position(x=self.x, y=self.y, z=self.z + number_of_blocks)

    def __add__(self, other: Position) -> Position:
        return Position(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def __sub__(self, other: Position) -> Position:
        return Position(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    def __mul__(self, scalar: int) -> Position:
        return Position(x=self.x * scalar, y=self.y * scalar, z=self.z * scalar)

    def __truediv__(self, scalar: int) -> Position:
        return self // scalar

    def __floordiv__(self, scalar: int) -> Position:
        return Position(x=self.x // scalar, y=self.y // scalar, z=self.z // scalar)


@dataclass
class Block:
    position: Position
    id: BlockID
    meta: int
    sky_light: int
    block_light: int

    @property
    def is_transparent(self):
        return self.id in TRANSPARENT_BLOCKS

    @property
    def is_full_block(self):
        return self.id in FULL_BLOCKS

    @classmethod
    def from_id(cls, block_id: BlockID) -> Block:  # TODO
        return cls(
            position=Position(x=0, y=0, z=0),
            id=block_id,
            meta=0,
            sky_light=0,
            block_light=0,
        )

    def update(self, position: Position = None, block_id: BlockID = None, meta: int = None, sky_light: int = None,
               block_light: int = None) -> Block:
        self.position = position or self.position
        self.id = block_id or self.id
        self.meta = meta or self.meta
        self.sky_light = sky_light or self.sky_light
        self.block_light = block_light or self.block_light
        return self


def fill_with_empty_chunks(chunks: list[Chunk]) -> list[Chunk]:
    chunks_per_direction = int(sqrt(len(chunks)))
    return [
        item for sublist
        in (
            (
                *chunks[idx:idx+chunks_per_direction],
                *[EmptyChunk()] * (World.MAX_CHUNKS_PER_DIRECTION - chunks_per_direction)
            )
            for idx
            in range(0, len(chunks), chunks_per_direction)
        )
        for item in sublist
    ] + [EmptyChunk()] * (World.MAX_CHUNKS_PER_DIRECTION - chunks_per_direction) * World.MAX_CHUNKS_PER_DIRECTION


class Chunk:
    """
    A chunk is a 16x16x128 area of blocks.
    """

    X_SIZE = 16
    """The size of the chunk in the x direction (north-south)."""

    Z_SIZE = 16
    """The size of the chunk in the z direction (east-west)."""

    Y_SIZE = 128
    """The size of the chunk in the y direction (height)."""

    blocks: list[Block]
    """A list of all blocks in the chunk."""

    biomes: list[BiomeID] | None
    """A list of all biomes in the chunk."""

    position: Position | None
    """The position of the chunk in the world."""

    __slots__ = ('blocks', 'biomes', 'position')

    def __init__(self, blocks: list[Block], biomes: list[BiomeID] = None, position: Position = None):
        self.blocks = blocks
        self.biomes = biomes
        self.position = position

    def __repr__(self):
        return f'<Chunk position={self.position} blocks={len(self.blocks)}>'

    def __bytes__(self):
        block_ids = b''.join(block.id.to_bytes(1, 'little') for block in self.blocks)
        meta = b''.join(
            (self.blocks[idx].meta << 4 | self.blocks[idx+1].meta).to_bytes(1, 'little')
            for idx in range(0, len(self.blocks), 2)
        )
        sky_light = b''.join(
            (self.blocks[idx].sky_light << 4 | self.blocks[idx+1].sky_light).to_bytes(1, 'little')
            for idx in range(0, len(self.blocks), 2)
        )
        block_light = b''.join(
            (self.blocks[idx].block_light << 4 | self.blocks[idx+1].block_light).to_bytes(1, 'little')
            for idx in range(0, len(self.blocks), 2)
        )
        biomes = b''.join(biome.to_bytes(1, 'little') for biome in self.biomes)

        data = b''.join([block_ids, meta, sky_light, block_light, biomes])
        header = (len(data) + 4).to_bytes(4, 'little')
        chunk_len = len(header) + len(data)
        padding = b'\x00' * (ceil(chunk_len / World.CHUNK_BLOCK_SIZE) * World.CHUNK_BLOCK_SIZE - chunk_len)
        return header + data + padding

    def __iter__(self) -> Iterable[Block]:
        return iter(self.blocks)

    @classmethod
    def from_layered_template(
            cls, layers: list[BlockID | None], biomes: list[BiomeID] = None, position: Position = None
    ) -> Chunk:
        """
        Create a chunk from a list of block ids.
        Each list item (Block ID) represents a layer of the chunk.
        Remaining space is filled with air.
        None == `BlockIDs.AIR` for convenience.
        """
        def get_layer(idx: int) -> BlockID:
            try:
                block_id = layers[idx]
            except IndexError:
                block_id = None
            if block_id is None:  # IndexError or None in layers
                block_id = BlockIDs.AIR
            return block_id

        blocks = [
            Block(
                id=get_layer(idx % cls.Y_SIZE),
                position=cls.index_to_block_position(idx),
                meta=0,
                # 15 if idx % cls.Y_SIZE + 1 != cls.Y_SIZE and get_layer(idx % cls.Y_SIZE + 1) == BlockIDs.AIR else 0,
                sky_light=0,
                block_light=0,
            ) for idx in range(cls.X_SIZE * cls.Z_SIZE * cls.Y_SIZE)
        ]

        return cls(
            blocks=blocks,
            biomes=biomes or [BiomeIDs.BID_0] * cls.X_SIZE * cls.Z_SIZE,
            position=position
        )

    @classmethod
    def index_to_block_position(cls, index: int) -> Position:
        return Position(
            x=index // cls.X_SIZE // cls.Y_SIZE,
            y=index % cls.Y_SIZE,
            z=index // cls.Y_SIZE % cls.Z_SIZE,
        )

    @classmethod
    def position_to_index(cls, position: Position) -> int:
        return position.y + position.z * cls.Y_SIZE + position.x * cls.Z_SIZE * cls.Y_SIZE

    def get_block(self, relative_position: Position) -> Block:
        """Get block at position relative to chunk."""
        if not all((
                0 <= relative_position.x < self.X_SIZE,
                0 <= relative_position.y < self.Y_SIZE,
                0 <= relative_position.z < self.Z_SIZE
        )):
            raise ValueError(f'Position must be inside the chunk! {relative_position}')
        return self.blocks[self.position_to_index(relative_position)]

    def update_block(self, relative_position: Position, block_id: BlockID, block_meta: int = None) -> None:
        """Update an existing block at position relative to chunk."""
        if not all((
                0 <= relative_position.x < self.X_SIZE,
                0 <= relative_position.y < self.Y_SIZE,
                0 <= relative_position.z < self.Z_SIZE
        )):
            raise ValueError(f'Position must be inside the chunk! {relative_position}')
        block = self.blocks[self.position_to_index(relative_position)]
        block.id = block_id
        if block_meta is not None:
            block.meta = block_meta

    def replace_block(self, block: Block):
        """Replace the block at position relative to chunk."""
        self.blocks[self.position_to_index(block.position)] = block


class EmptyChunk(Chunk):
    def __init__(self):
        super().__init__([], None, None)  # type: ignore

    def __bytes__(self):
        return b''


@dataclass(repr=False)
class World:
    CHUNK_BLOCK_SIZE = 4096
    MAX_CHUNKS_PER_DIRECTION = 32

    chunks: list[Chunk]

    __slots__ = ('chunks', )

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks if len(chunks) == self.MAX_CHUNKS_PER_DIRECTION ** 2 else fill_with_empty_chunks(chunks)

    def __repr__(self):
        empty_chunks = sum(1 for chunk in self.chunks if isinstance(chunk, EmptyChunk))
        return f'<World chunks={len(self.chunks) - empty_chunks} empty_chunks={empty_chunks}>'

    def __bytes__(self):
        chunk_index = b''
        chunk_data = b''
        data_index = 1

        for chunk in self.chunks:
            if isinstance(chunk, EmptyChunk):
                chunk_index += (0).to_bytes(4, 'little')
                continue
            data = bytes(chunk)
            chunk_data += data
            reserved_block_sizes = ceil(len(data) / self.CHUNK_BLOCK_SIZE)
            chunk_index += reserved_block_sizes.to_bytes(1, 'little')
            chunk_index += data_index.to_bytes(3, 'little')
            data_index += reserved_block_sizes

        return chunk_index + chunk_data

    def __iter__(self) -> Iterable[Chunk]:
        return iter(self.non_empty_chunks)

    def iter_blocks(self) -> Iterable[Block]:
        return iter(block for chunk in self for block in chunk)

    @property
    def non_empty_chunks(self):
        return list(filter(lambda chunk: not isinstance(chunk, EmptyChunk), self.chunks))

    @property
    def empty_chunks(self):
        return list(filter(lambda chunk: isinstance(chunk, EmptyChunk), self.chunks))

    @property
    def chunks_per_direction(self) -> int:
        return int(sqrt(len(self.non_empty_chunks)))

    @staticmethod
    def global_to_chunk_position(position: Position) -> tuple[Position, Position]:
        chunk_position = Position(
            x=position.x // Chunk.X_SIZE,
            y=position.y // Chunk.Y_SIZE,
            z=position.z // Chunk.Z_SIZE
        )
        chunk_relative_block_position = Position(
            x=position.x % Chunk.X_SIZE,
            y=position.y % Chunk.Y_SIZE,
            z=position.z % Chunk.Z_SIZE,
        )
        return chunk_position, chunk_relative_block_position

    @classmethod
    def chunk_to_global_position(cls, chunk_position: Position, relative_block_position: Position) -> Position:
        return Position(
            x=chunk_position.x * Chunk.X_SIZE + relative_block_position.x,
            y=relative_block_position.y,
            z=chunk_position.z * Chunk.Z_SIZE + relative_block_position.z
        )

    @classmethod
    def index_to_chunk_position(cls, idx: int) -> Position:
        return Position(
            x=idx % cls.MAX_CHUNKS_PER_DIRECTION,
            y=0,
            z=idx // cls.MAX_CHUNKS_PER_DIRECTION
        )

    @classmethod
    def chunk_position_to_index(cls, position: Position) -> int:
        return cls.MAX_CHUNKS_PER_DIRECTION * position.y + position.z

    @classmethod
    def load(cls, path: PathLike | str) -> World:
        path = Path(path)
        logging.getLogger(__name__).debug(f'Loading file: {path.name} ({path.stat().st_size / 1_000_000:.2f} MB)')
        with path.open('rb') as f:
            data = f.read()

        chunks = []
        chunk_index = data[:cls.CHUNK_BLOCK_SIZE]
        chunk_headers = [chunk_index[i:i + 4] for i in range(0, len(chunk_index), 4)]
        for idx, chunk_header in enumerate(chunk_headers):
            reserved_block_sizes = chunk_header[0]  # How many chunk blocks of storage are reserved for this chunk
            chunk_data_index = int.from_bytes(chunk_header[1:], 'little')
            if chunk_data_index == 0 and reserved_block_sizes == 0:
                chunks.append(EmptyChunk())
                continue
            chunk_data_offset = chunk_data_index * cls.CHUNK_BLOCK_SIZE
            chunk_header_block = data[chunk_data_offset:chunk_data_offset + 4]
            chunk_length = int.from_bytes(chunk_header_block, 'little')  # without padding
            if chunk_length == 0:
                raise ValueError(f'Chunk {idx} is empty!')
            chunk_data = data[chunk_data_offset + 4:chunk_data_offset + chunk_length]

            block_size = Chunk.X_SIZE * Chunk.Z_SIZE * Chunk.Y_SIZE
            block_ids = chunk_data[:block_size]
            block_meta = [
                item
                for sublist
                in (
                    ((meta & 0b11110000) >> 4, meta & 0b00001111)
                    for meta
                    in chunk_data[block_size:int(block_size * 1.5)]
                )
                for item
                in sublist
            ]
            block_sky_light = [
                item
                for sublist
                in (
                    ((lighting & 0b11110000) >> 4, lighting & 0b00001111)
                    for lighting
                    in chunk_data[int(block_size * 1.5):block_size * 2]
                )
                for item
                in sublist
            ]
            block_light = [
                item
                for sublist
                in (
                    ((lighting & 0b11110000) >> 4, lighting & 0b00001111)
                    for lighting
                    in chunk_data[block_size * 2:int(block_size * 2.5)]
                )
                for item
                in sublist
            ]
            block_biomes = [biome for biome in chunk_data[int(block_size * 2.5):]]

            chunk_position = cls.index_to_chunk_position(idx)
            blocks = [
                Block(
                    position=cls.chunk_to_global_position(chunk_position, Chunk.index_to_block_position(block_idx)),
                    id=block_ids[block_idx],
                    meta=block_meta[block_idx],
                    sky_light=block_sky_light[block_idx],
                    block_light=block_light[block_idx],
                )
                for block_idx in range(block_size)
            ]
            chunks.append(Chunk(blocks=blocks, biomes=block_biomes, position=chunk_position))
        logging.getLogger(__name__).debug(f'Loaded {len(chunks)} chunks')
        return cls(chunks=chunks)

    def save(self, path: PathLike | str) -> None:
        path = Path(path)
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(bytes(self))

    def get_block(self, absolute_block_position: Position) -> Block:
        """Get block relative to world."""
        chunk_position, chunk_relative_block_position = self.global_to_chunk_position(position=absolute_block_position)
        return self.chunks[self.chunk_position_to_index(chunk_position)].get_block(
            relative_position=chunk_relative_block_position
        )

    def update_block(self, absolute_block_position: Position, block_id: BlockID, block_meta: int = None) -> None:
        chunk_position, chunk_relative_block_position = self.global_to_chunk_position(position=absolute_block_position)
        self.chunks[self.chunk_position_to_index(chunk_position)].update_block(
            relative_position=chunk_relative_block_position,
            block_id=block_id,
            block_meta=block_meta
        )

    def replace_block(self, block: Block):
        chunk_position, chunk_relative_block_position = self.global_to_chunk_position(position=block.position)
        self.chunks[self.chunk_position_to_index(chunk_position)].replace_block(block)

    def get_chunk(self, absolute_chunk_position: Position) -> Chunk:
        return self.chunks[self.chunk_position_to_index(absolute_chunk_position)]

    def set_chunk(self, absolute_chunk_position: Position, chunk: Chunk) -> None:
        chunk.position = absolute_chunk_position
        self.chunks[self.chunk_position_to_index(absolute_chunk_position)] = chunk

    @classmethod
    def new(cls) -> World:  # TODO
        return cls(chunks=[EmptyChunk()])

    def possible_position(self, absolute_position: Position) -> bool:
        return all((
            0 <= absolute_position.x < Chunk.X_SIZE * self.chunks_per_direction,
            0 <= absolute_position.y < Chunk.Y_SIZE,
            0 <= absolute_position.z < Chunk.Z_SIZE * self.chunks_per_direction
        ))
