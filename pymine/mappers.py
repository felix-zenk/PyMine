from typing import Literal

from PIL import Image

from .chunks import World, Block
from .ids import BlockID, BlockIDs


Face = Literal['top', 'bottom', 'front', 'back', 'left', 'right']


class TextureMapper:
    TEXTURE_SIZE: int = 16

    terrain_atlas: Image.Image
    world: World

    def __init__(self, world: World):
        self.world = world
        self.terrain_atlas = Image.open('terrain-atlas.tga')

    def _from_atlas_coord(self, x: int, y: int) -> Image.Image:
        return self.terrain_atlas.crop((
            self.TEXTURE_SIZE * y,
            self.TEXTURE_SIZE * x,
            self.TEXTURE_SIZE * y + self.TEXTURE_SIZE,
            self.TEXTURE_SIZE * x + self.TEXTURE_SIZE
        )).convert('RGBA')

    def _from_atlas_index(self, index: int) -> Image.Image:
        items_per_row = self.terrain_atlas.width // self.TEXTURE_SIZE
        return self._from_atlas_coord(
            index // items_per_row,
            index % items_per_row
        )

    def _coord_to_index(self, x: int, y: int) -> int:
        items_per_row = self.terrain_atlas.width // self.TEXTURE_SIZE
        return x * items_per_row + y

    def _map_texture(self, block: Block, face: Face) -> Image.Image:
        INVISIBLE = Image.new('RGBA', (self.TEXTURE_SIZE, self.TEXTURE_SIZE), (0, 0, 0, 0))
        DOES_NOT_EXIST = self._from_atlas_coord(0, 0)
        if block.id == BlockIDs.AIR:
            return INVISIBLE
        if block.id == BlockIDs.STONE:
            return self._from_atlas_coord(0, 4)
        if block.id == BlockIDs.GRASS_BLOCK:
            if face == 'top':
                return self._from_atlas_coord(0, 3)
            if face == 'bottom':
                return self._from_atlas_coord(0, 21)
            return self._from_atlas_index(self._coord_to_index(0, 1) + block.meta)
        if block.id == BlockIDs.DIRT:
            return self._from_atlas_coord(0, 21)
        if block.id == BlockIDs.COBBLESTONE:
            return self._from_atlas_coord(0, 5)
        if block.id == BlockIDs.PLANK:
            return self._from_atlas_index(self._coord_to_index(0, 22) + block.meta)
        if block.id == BlockIDs.SAPLING:
            if face in ('top', 'bottom'):
                return INVISIBLE
            return self._from_atlas_index(self._coord_to_index(1, 4) + block.meta)
        if block.id == BlockIDs.BEDROCK:
            return self._from_atlas_coord(0, 11)
        if block.id == BlockIDs.WATER:
            return self._from_atlas_coord(9, 0)
        if block.id == BlockIDs.WATER_SOURCE:
            return self._from_atlas_coord(7, 22)
        if block.id == BlockIDs.LAVA:
            return self._from_atlas_coord(9, 2)
        if block.id == BlockIDs.LAVA_SOURCE:
            return self._from_atlas_coord(7, 23)
        if block.id == BlockIDs.SAND:
            return self._from_atlas_coord(0, 14)
        if block.id == BlockIDs.GRAVEL:
            return self._from_atlas_coord(0, 20)
        if block.id == BlockIDs.GOLD_ORE:
            return self._from_atlas_coord(2, 0)
        if block.id == BlockIDs.IRON_ORE:
            return self._from_atlas_coord(2, 1)
        if block.id == BlockIDs.COAL_ORE:
            return self._from_atlas_coord(2, 2)
        if block.id == BlockIDs.LOG:
            if face in ('top', 'bottom'):
                return self._from_atlas_index(self._coord_to_index(1, 9) + block.meta * 2)
            return self._from_atlas_index(self._coord_to_index(1, 8) + block.meta * 2)
        if block.id == BlockIDs.LEAVES:
            return self._from_atlas_index(self._coord_to_index(2, 30) + block.meta)
        if block.id == BlockIDs.SPONGE:
            return self._from_atlas_coord(2, 24)
        if block.id == BlockIDs.GLASS:
            return self._from_atlas_coord(2, 25)
        if block.id == BlockIDs.LAPIS_LAZULI_ORE:
            return self._from_atlas_coord(2, 3)
        if block.id == BlockIDs.LAPIS_LAZULI_BLOCK:
            return self._from_atlas_coord(1, 20)
        if block.id == BlockIDs.BID_23:
            return DOES_NOT_EXIST
        if block.id == BlockIDs.SANDSTONE:
            if face == 'top':
                return self._from_atlas_coord(0, 18)
            if face == 'bottom':
                return self._from_atlas_coord(0, 19)
            return self._from_atlas_index(self._coord_to_index(0, 15) + block.meta)
        if block.id == BlockIDs.BID_25:
            return DOES_NOT_EXIST
        if block.id == BlockIDs.BED:
            if block.meta == 0:
                if face == 'top':
                    return self._from_atlas_coord(5, 5)
                if face == 'front':
                    return self._from_atlas_coord(5, 6)
                if face == 'right':
                    return self._from_atlas_coord(5, 7)
                if face == 'left':
                    return self._from_atlas_coord(5, 7).transform(
                        (self.TEXTURE_SIZE, self.TEXTURE_SIZE),
                        Image.FLIP_LEFT_RIGHT
                    )
                # no bottom, back?
            if block.meta == 1:
                if face == 'top':
                    return self._from_atlas_coord(5, 8)
                if face == 'back':
                    return self._from_atlas_coord(5, 9)
                if face == 'right':
                    return self._from_atlas_coord(5, 10)
                if face == 'left':
                    return self._from_atlas_coord(5, 10).transform(
                        (self.TEXTURE_SIZE, self.TEXTURE_SIZE),
                        Image.FLIP_LEFT_RIGHT
                    )
                # no bottom, front?
        if block.id == BlockIDs.POWERED_RAIL:
            if face == 'top':
                return self._from_atlas_coord(5, 0)
        if block.id == BlockIDs.BID_28:
            return DOES_NOT_EXIST
        if block.id == BlockIDs.BID_29:
            return DOES_NOT_EXIST
        if block.id == BlockIDs.COBWEB:
            if face in ('top', 'bottom'):
                return INVISIBLE
            return self._from_atlas_coord(1, 1)
        if block.id in (BlockIDs.DEAD_SHRUB, BlockIDs.BEAD_BUSH):
            if face in ('top', 'bottom'):
                return INVISIBLE
            return self._from_atlas_coord(2, 9)
        if block.id == BlockIDs.BID_33:
            return DOES_NOT_EXIST
        if block.id == BlockIDs.BID_34:
            return DOES_NOT_EXIST
        if block.id == BlockIDs.WOOL:
            return self._from_atlas_index(self._coord_to_index(7, 24) + block.meta)
        if block.id == BlockIDs.BID_36:
            return DOES_NOT_EXIST
        if block.id == BlockIDs.YELLOW_FLOWER:
            if face in ('top', 'bottom'):
                return INVISIBLE
            return self._from_atlas_coord(1, 3)
        if block.id == BlockIDs.CYAN_FLOWER:
            if face in ('top', 'bottom'):
                return INVISIBLE
            return self._from_atlas_coord(1, 2)
        if block.id == BlockIDs.BROWN_MUSHROOM:
            if face in ('top', 'bottom'):
                return INVISIBLE
            return self._from_atlas_coord(0, 31)
        if block.id == BlockIDs.RED_MUSHROOM:
            if face in ('top', 'bottom'):
                return INVISIBLE
            return self._from_atlas_coord(0, 30)
        if block.id == BlockIDs.GOLD_BLOCK:
            return self._from_atlas_coord(1, 17)
        if block.id == BlockIDs.IRON_BLOCK:
            return self._from_atlas_coord(1, 16)
        if block.id == BlockIDs.DOUBLE_STONE_SLAB:
            if face in ('top', 'bottom'):
                return self._from_atlas_coord(0, 26)
            return self._from_atlas_coord(0, 27)
        if block.id == BlockIDs.STONE_SLAB:
            if face in ('top', 'bottom'):
                return self._from_atlas_coord(0, 26)
            img = self._from_atlas_index(self._coord_to_index(0, 27))
            img.paste(
                Image.new(
                    mode='RGBA',
                    size=(self.TEXTURE_SIZE, self.TEXTURE_SIZE // 2),
                    color=(0, 0, 0, 0)
                ),
                (0, 0, img.width, img.height // 2) if block.meta == 0 else (0, img.height // 2, img.width, img.height)
            )
            return img
        if block.id == BlockIDs.BRICK_BLOCK:
            return self._from_atlas_coord(0, 28)
        if block.id == BlockIDs.TNT:
            if face == 'top':
                return self._from_atlas_coord(0, 30)
            if face == 'bottom':
                return self._from_atlas_coord(0, 31)
            return self._from_atlas_coord(0, 29)
        if block.id == BlockIDs.BOOKSHELF:
            if face in ('top', 'bottom'):
                return self._from_atlas_coord(0, 22)
            return self._from_atlas_coord(1, 0)
        if block.id == BlockIDs.MOSSY_COBBLESTONE:
            return self._from_atlas_coord(0, 6)

        return DOES_NOT_EXIST

    def _from_block(self, block: Block, face: Face) -> Image.Image:
        if block.is_transparent:
            if block.position.y > 0:
                return Image.alpha_composite(
                    self._from_block(self.world.get_block(block.position.down()), 'top'),
                    self._map_texture(block, face)
                )
            return Image.new('RGBA', (self.TEXTURE_SIZE, self.TEXTURE_SIZE), (0, 0, 0, 0))
        return self._map_texture(block, face)

    def top(self, block: Block) -> Image.Image:
        return self._from_block(block, 'top')

    def bottom(self, block: Block) -> Image.Image:
        return self._from_block(block, 'bottom')

    def front(self, block: Block) -> Image.Image:
        return self._from_block(block, 'front')

    def back(self, block: Block) -> Image.Image:
        return self._from_block(block, 'back')

    def left(self, block: Block) -> Image.Image:
        return self._from_block(block, 'left')

    def right(self, block: Block) -> Image.Image:
        return self._from_block(block, 'right')
