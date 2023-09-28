from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image

from pymine import Position, World, Chunk, Block, BlockIDs, BlockID, EmptyChunk
from pymine.game import Game
from pymine.level import Level

atlas = Image.open('terrain-atlas.tga')
TEXTURE_SIZE = 16


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
    TEXTURE_SIZE = 16
    img = Image.new(
        'RGBA',
        (
            world.chunks_per_direction * Chunk.X_SIZE * TEXTURE_SIZE,
            world.chunks_per_direction * Chunk.Z_SIZE * TEXTURE_SIZE
        )
    )

    logging.info('Rendering blocks')
    for chunk in world:
        for block in chunk:
            if block.id == BlockIDs.AIR:
                continue
            img.paste(
                Image.alpha_composite(
                    get_texture(world, block),
                    Image.new(
                        'RGBA',
                        (TEXTURE_SIZE, TEXTURE_SIZE),
                        (0, 0, 0, Chunk.Y_SIZE - 1 - block.position.y)
                    )
                ),
                (
                    block.position.x * TEXTURE_SIZE,
                    block.position.z * TEXTURE_SIZE,
                    block.position.x * TEXTURE_SIZE + TEXTURE_SIZE,
                    block.position.z * TEXTURE_SIZE + TEXTURE_SIZE
                )
            )

    image_path = Path(image_path)
    image_path.parent.mkdir(exist_ok=True)
    # Rotate image so that up is north
    img.rotate(-90).save(image_path)
    logging.info('Saved image to %s', image_path)


def get_texture(world: World, b: Block):
    def atlas_coord(x, y):
        return atlas.crop((TEXTURE_SIZE * y, TEXTURE_SIZE * x, TEXTURE_SIZE * y + TEXTURE_SIZE, TEXTURE_SIZE * x + TEXTURE_SIZE))

    texture = Image.new('RGBA', (TEXTURE_SIZE, TEXTURE_SIZE), (255, 0, 0, 255))
    if b.is_transparent:
        if b.position.y > 0:
            texture.alpha_composite(get_texture(world, world.get_block(Position(
                x=b.position.x,
                y=b.position.y - 1,
                z=b.position.z
            ))).convert('RGBA'))
        if b.id == BlockIDs.LEAVES:
            texture.alpha_composite(atlas_coord(2, 30))
        if b.id == BlockIDs.TORCH:
            torch = atlas_coord(3, 18)
            texture.alpha_composite(torch.crop((6, 6, 7, 7)))
        return texture

    if b.id == BlockIDs.GRASS_BLOCK:
        return atlas_coord(0, 3)
    if b.id == BlockIDs.LOG:
        return atlas_coord(1, 9)
    if b.id == BlockIDs.STONE:
        return atlas_coord(0, 4)
    if b.id == BlockIDs.SAND:
        return atlas_coord(0, 14)
    if b.id == BlockIDs.DIRT:
        return atlas_coord(0, 21)
    if b.id in (BlockIDs.STONE_BRICKS, BlockIDs.STONE_SLAB):
        return atlas_coord(0, 7)
    if b.id == BlockIDs.MOSS_STONE_MOSSY_COBBLESTONE:
        return atlas_coord(0, 6)
    if b.id == BlockIDs.PLANK:
        if b.meta == 0:
            return atlas_coord(0, 22)
        if b.meta == 1:
            return atlas_coord(0, 23)
        if b.meta == 2:
            return atlas_coord(0, 24)
        if b.meta == 3:
            return atlas_coord(0, 25)
    if b.id == BlockIDs.BRICK_BLOCK:
        return atlas_coord(0, 28)
    if b.id == BlockIDs.CLAY_BLOCK:
        return atlas_coord(0, 13)
    if b.id == BlockIDs.SANDSTONE:
        return atlas_coord(0, 18)
    if b.id == BlockIDs.GRAVEL:
        return atlas_coord(0, 20)
    if b.id == BlockIDs.NETHER_BRICK:
        return atlas_coord(4, 12)
    if b.id == BlockIDs.NETHERRACK:
        return atlas_coord(4, 11)
    if b.id == BlockIDs.BEDROCK:
        return atlas_coord(0, 11)
    # If not found return a red image
    # return Image.new('RGBA', (TEXTURE_SIZE, TEXTURE_SIZE), (b.id, b.id, b.id, 255))
    return texture


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
        )
    )
    game.save()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    game = Game.load('world')

    height_map(world=game.world, image_path='images/height_map.png')
    top_down_view(world=game.world, image_path='images/top_down_view.png')

    create_flat_world(name='flat_world')
