import logging
from math import log
from pathlib import Path

import numpy as np
from PIL import Image

from pymine import Position, World, Chunk, Block, BlockIDs, BlockID, EmptyChunk


def main():
    print('Loading world')
    world = World.load('world/chunks.dat')
    print('World loaded')

    # Create a top-down image of the world
    img = Image.new(
        'RGB',
        (world.chunks_per_direction * Chunk.X_SIZE, world.chunks_per_direction * Chunk.Z_SIZE)
    )
    for chunk in world:
        for block in chunk:
            if block.id == BlockIDs.AIR:
                continue
            print(block.position)
            img.putpixel(
                (block.position.x, block.position.z),
                (block.position.y, block.position.y, block.position.y)
            )

    images = Path('img')
    images.mkdir(exist_ok=True)
    img.save(images / 'world.png')

    # world.save('chunks.dat')
    # print('EXPORTED')
    # World.load('chunks.dat')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
