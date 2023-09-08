from __future__ import annotations

import logging
from dataclasses import dataclass
from math import ceil
from os import PathLike
from pathlib import Path
from typing import NamedTuple

from .ids import BlockId, BiomeId

Position = NamedTuple('Position', x=int, y=int, z=int)
Block = NamedTuple('Block', position=Position, id=BlockId, meta=int, sky_light=int, block_light=int)


class Chunk:
    X_SIZE = 16
    Z_SIZE = 16
    Y_SIZE = 128

    position: Position
    blocks: list[Block]
    biomes: list[BiomeId]
    data_index: int

    __slots__ = ('position', 'blocks', 'biomes', 'data_index')

    def __init__(self, position: Position, blocks: list[Block], biomes: list[BiomeId]):
        self.position = position
        self.blocks = blocks
        self.biomes = biomes

    def __repr__(self):
        return f'<Chunk position={self.position} blocks={len(self.blocks)}>'

    def __bytes__(self):
        block_ids = b''.join(block.id.value.to_bytes(1, 'little') for block in self.blocks)
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
        biomes = b''.join(biome.value.to_bytes(1, 'little') for biome in self.biomes)

        data = b''.join([block_ids, meta, sky_light, block_light, biomes])
        header = len(data).to_bytes(4, 'little')
        chunk_len = len(header) + len(data)
        padding = b'\x00' * (ceil(chunk_len / World.CHUNK_BLOCK_SIZE) * World.CHUNK_BLOCK_SIZE - chunk_len)
        return header + data + padding

    @classmethod
    def from_layered_template(cls, position: Position, layers: list[BlockId | None]):
        def get_layer(idx: int) -> BlockId:
            try:
                block_id = layers[idx]
            except IndexError:
                block_id = None
            if block_id is None:  # IndexError or None in layers
                block_id = BlockId.AIR
            return block_id

        return cls(
            position=position,
            blocks=[
                Block(
                    id=get_layer(idx % cls.Y_SIZE),
                    position=Position(
                        x=(idx // cls.Y_SIZE) // cls.Z_SIZE,
                        y=idx % cls.Y_SIZE,
                        z=(idx // cls.Y_SIZE) % cls.Z_SIZE,
                    ),
                    meta=0,
                    sky_light=0,
                    block_light=0,
                ) for idx in range(cls.X_SIZE * cls.Z_SIZE * cls.Y_SIZE)
            ],
            biomes=[BiomeId.PLAINS] * cls.X_SIZE * cls.Z_SIZE,
        )

    @classmethod
    def index_to_block_position(cls, index: int) -> Position:
        return Position(
            x=(index // cls.Y_SIZE) // cls.Z_SIZE,
            y=index % cls.Y_SIZE,
            z=(index // cls.Y_SIZE) % cls.Z_SIZE,
        )

    @classmethod
    def position_to_index(cls, position: Position) -> int:
        return position.y + position.z * cls.Y_SIZE + position.x * cls.Z_SIZE * cls.Y_SIZE

    def get_block(self, relative_position: Position) -> Block:
        """Get block at position relative to chunk."""
        return self.blocks[self.position_to_index(relative_position)]

    def set_block(self, relative_position: Position, block_id: BlockId, block_meta: int = None) -> None:
        """Set the block ID and meta of the block at position relative to chunk."""
        block = self.get_block(relative_position)
        block.id = block_id
        if block_meta is not None:
            block.meta = block_meta


class EmptyChunk(Chunk):
    def __init__(self):
        super().__init__(None, [], [])  # type: ignore

    def __bytes__(self):
        return b''


@dataclass(repr=False)
class World:
    CHUNK_BLOCK_SIZE = 4096
    MAX_CHUNKS_PER_DIRECTION = 32

    chunks: list[Chunk]

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
    def index_to_chunk_position(cls, idx: int) -> Position:
        return Position(
            x=idx // cls.MAX_CHUNKS_PER_DIRECTION,
            y=0,
            z=idx % cls.MAX_CHUNKS_PER_DIRECTION
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

        logging.getLogger(__name__).debug(f'Chunk block size: {cls.CHUNK_BLOCK_SIZE}')
        chunks = []
        chunk_index = data[:cls.CHUNK_BLOCK_SIZE]
        chunk_headers = [chunk_index[i:i + 4] for i in range(0, len(chunk_index), 4)]
        logging.getLogger(__name__).debug(f'Found {len(chunk_headers)} chunk headers')
        for idx, chunk_header in enumerate(chunk_headers):
            logging.getLogger(__name__).debug(f'Processing chunk {idx} ...')
            # reserved_block_sizes = chunk_header[0]  # How many chunk blocks of storage are reserved for this chunk
            chunk_data_index = int.from_bytes(chunk_header[1:], 'little')
            if chunk_data_index == 0:
                logging.getLogger(__name__).debug(f'Found empty chunk at chunk index: {idx} ({chunk_data_index}/+0)')
                chunks.append(EmptyChunk())
                continue
            chunk_data_offset = chunk_data_index * cls.CHUNK_BLOCK_SIZE
            logging.getLogger(__name__).debug(
                f'Found non-empty chunk at chunk index: {idx} ({chunk_data_index}/+{chunk_data_offset})'
            )
            chunk_header_block = data[chunk_data_offset:chunk_data_offset + 4]
            logging.getLogger(__name__).debug(f'Chunk header block: {chunk_header_block}')
            if chunk_header_block == b'\x00\x00\x00\x00':
                logging.getLogger(__name__).error(f'MISTAKEN EMPTY CHUNK AT CHUNK INDEX: {idx} ({chunk_data_index})')
                chunks.append(EmptyChunk())
                continue
            chunk_length = int.from_bytes(chunk_header_block, 'little')  # without padding
            chunk_data = data[chunk_data_offset + 4:chunk_data_offset + chunk_length]  # truncate padding automatically

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
            block_biomes = [BiomeId(biome) for biome in chunk_data[int(block_size * 2.5):]]

            chunk_position = cls.index_to_chunk_position(idx)
            blocks = [
                Block(
                    position=Position(
                        x=chunk_position.x * Chunk.X_SIZE + (idx // Chunk.Y_SIZE) // Chunk.Z_SIZE,
                        y=idx % Chunk.Y_SIZE,
                        z=chunk_position.z * Chunk.Z_SIZE + (idx // Chunk.Y_SIZE) % Chunk.Z_SIZE,
                    ),
                    id=BlockId(block_ids[idx]),
                    meta=block_meta[idx],
                    sky_light=block_sky_light[idx],
                    block_light=block_light[idx],
                )
                for idx in range(block_size)
            ]
            chunks.append(Chunk(position=chunk_position, blocks=blocks, biomes=block_biomes))
        return cls(chunks=chunks)

    def save(self, path: PathLike | str) -> None:
        with Path(path).open('wb') as f:
            f.write(bytes(self))

    def get_block(self, absolute_position: Position) -> Block:
        """Get block relative to world."""
        chunk_position, chunk_relative_block_position = self.global_to_chunk_position(position=absolute_position)
        return self.chunks[self.chunk_position_to_index(chunk_position)].get_block(
            relative_position=chunk_relative_block_position
        )

    def set_block(self, absolute_position: Position, block_id: BlockId, block_meta: int = None) -> None:
        pass

    def get_chunk(self, absolute_position: Position) -> Chunk:
        pass

    def set_chunk(self, absolute_position: Position, chunk: Chunk) -> None:
        pass
