from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image

from pymine import Position, World, Chunk, BlockIDs, Entities, Game, Level, TextureMapper


def height_map(world: World, image_path: str):
    """Create a height map of the world"""
    logging.info('Creating height map of the world')
    img = Image.new(
        'RGB',
        (world.chunks_per_direction * Chunk.X_SIZE, world.chunks_per_direction * Chunk.Z_SIZE)
    )
    logging.info('Getting highest blocks')
    for chunk in world:
        for block in chunk:
            if block.id == BlockIDs.AIR:
                continue
            img.putpixel(
                (block.position.x, block.position.z),
                (block.position.y, block.position.y, block.position.y)
            )

    image_path = Path(image_path)
    image_path.parent.mkdir(exist_ok=True)
    # Rotate image so that up is north
    img.rotate(-90).save(image_path)
    logging.info('Saved image to %s', image_path)


def top_down_view(world: World, image_path: str):
    """Create a top-down image of the world"""
    logging.info('Creating top-down image of the world')
    view = Image.new(
        'RGBA',
        (
            world.chunks_per_direction * Chunk.X_SIZE * mapper.TEXTURE_SIZE,
            world.chunks_per_direction * Chunk.Z_SIZE * mapper.TEXTURE_SIZE
        )
    )

    logging.info('Rendering blocks')
    for chunk in world:
        for block in chunk:
            if block.id == BlockIDs.AIR:
                continue
            view.paste(
                Image.alpha_composite(
                    mapper.top(block),
                    Image.new(
                        'RGBA',
                        (mapper.TEXTURE_SIZE, mapper.TEXTURE_SIZE),
                        (0, 0, 0, Chunk.Y_SIZE - 1 - block.position.y)
                    )
                ),
                (
                    block.position.x * mapper.TEXTURE_SIZE,
                    block.position.z * mapper.TEXTURE_SIZE,
                    block.position.x * mapper.TEXTURE_SIZE + mapper.TEXTURE_SIZE,
                    block.position.z * mapper.TEXTURE_SIZE + mapper.TEXTURE_SIZE
                )
            )

    image_path = Path(image_path)
    image_path.parent.mkdir(exist_ok=True)
    # Rotate image so that up is north
    (view
     # .rotate(-90)
     .save(image_path)
     )
    logging.info('Saved image to %s', image_path)


def create_flat_world(name: str = 'flat_world'):
    game = Game(
        level=Level(
            name=name,
            seed=0,
            spawn_position=Position(x=0, y=4, z=0),
            gamemode=0,
            difficulty=0,
            world_type='flat',
            generator_version=1,
            generator_options='3;minecraft:bedrock,2*minecraft:dirt,minecraft:grass;1;'
        ),
        world=World(
            chunks=[
                Chunk.from_layered_template(layers=[
                    BlockIDs.BEDROCK, *[BlockIDs.GRASS_BLOCK] * 2, BlockIDs.GRASS_BLOCK
                ])
                for idx in range((World.MAX_CHUNKS_PER_DIRECTION // 2) ** 2)
            ]
        ),
        entities=Entities([])
    )
    game.save()


def block_id_img(number: int):
    block_img = Image.new('RGBA', (16, 16), (0, 0, 0, 255))
    digits = [int(d) for d in str(number)]
    digit_width = digits_map.width // 10
    for idx, digit in enumerate(digits):
        digit_img = digits_map.crop((
            int(digit) * digit_width,
            0,
            int(digit) * digit_width + digit_width,
            digits_map.height
        ))
        padding = (block_img.width - len(digits) * digit_width)
        min_inline_padding = len(digits) - 1
        side_padding = (padding - min_inline_padding) // 2
        block_img.paste(digit_img, (
            side_padding + idx * (digit_width + 1),
            block_img.height // 2 - digit_img.height // 2
        ))
    return block_img


def block_id_map(world, image_path):
    """Create a top-down image of the world"""
    logging.info('Creating block ID map of the world')

    img = Image.new(
        'RGBA',
        (
            world.chunks_per_direction * Chunk.X_SIZE * mapper.TEXTURE_SIZE,
            world.chunks_per_direction * Chunk.Z_SIZE * mapper.TEXTURE_SIZE
        )
    )

    logging.info('Rendering blocks')
    for chunk in world:
        for block in chunk:
            if block.id == BlockIDs.AIR:
                continue
            img.paste(
                block_id_img(block.id),
                (
                    block.position.x * mapper.TEXTURE_SIZE,
                    block.position.z * mapper.TEXTURE_SIZE,
                    block.position.x * mapper.TEXTURE_SIZE + mapper.TEXTURE_SIZE,
                    block.position.z * mapper.TEXTURE_SIZE + mapper.TEXTURE_SIZE
                )
            )

    image_path = Path(image_path)
    image_path.parent.mkdir(exist_ok=True)
    # Rotate image so that up is north
    img.rotate(-90).save(image_path)
    logging.info('Saved image to %s', image_path)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    digits_map = Image.open('placeholders/digits.png')
    game = Game.load('world')
    mapper = TextureMapper(world=game.world)

    # height_map(world=game.world, image_path='images/height_map.png')
    top_down_view(world=game.world, image_path=f'images/{game.level.name}_top_down_view.png')
    # create_flat_world(name='flat_world')
    # block_id_map(world=game.world, image_path='images/block_id_map.png')
