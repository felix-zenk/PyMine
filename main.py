import logging

from pymine import Position, World, Chunk, Block, BlockId


def main():
    world = World.load('world/chunks.dat')

    # FUTURE:

    """
    layers: list[BlockId] = [
        BlockId.BEDROCK,
        *[BlockId.DIRT] * 2,
        BlockId.GRASS_BLOCK,
        *[BlockId.AIR] * (Chunk.Y_SIZE - 4),
    ]

    chunk = world.get_chunk(absolute_position=Position(x=0, y=0, z=0))
    new_chunk = Chunk.from_layered_template(Position(x=0, y=0, z=0), layers=layers)
    world.set_chunk(absolute_position=Position(x=0, y=0, z=0), chunk=new_chunk)
    chunk.get_block(relative_position=Position(x=0, y=0, z=0))
    chunk.set_block(
        relative_position=Position(x=0, y=0, z=0),
        block_id=BlockId.BEDROCK
    )
    world.set_block(
        absolute_position=Position(x=0, y=0, z=0),
        block_id=BlockId.BEDROCK
    )
    """

    world.save('chunks.dat')

    World.load('chunks.dat')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
