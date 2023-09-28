from typing import Literal

from PIL import Image

from .chunks import World, Block
from .ids import BlockID, BlockIDs


Face = Literal['top', 'bottom', 'front', 'back', 'left', 'right']


class TextureMapper:
    TEXTURE_SIZE: int = 16

    INVISIBLE: Image.Image
    DOES_NOT_EXIST: Image.Image
    MISSING: Image.Image
    terrain_atlas: Image.Image
    world: World

    def __init__(self, world: World):
        self.world = world
        self.terrain_atlas = Image.open('terrain-atlas.tga')
        self.INVISIBLE = Image.new('RGBA', (self.TEXTURE_SIZE, self.TEXTURE_SIZE), (0, 0, 0, 0))
        self.DOES_NOT_EXIST = self._from_atlas_coord(0, 0)
        self.MISSING = Image.new('RGBA', (self.TEXTURE_SIZE, self.TEXTURE_SIZE), (255, 0, 255, 255))

    def _from_atlas_coord(self, x: int, y: int) -> Image.Image:
        return self.terrain_atlas.crop((
            self.TEXTURE_SIZE * x,
            self.TEXTURE_SIZE * y,
            self.TEXTURE_SIZE * x + self.TEXTURE_SIZE,
            self.TEXTURE_SIZE * y + self.TEXTURE_SIZE
        )).convert('RGBA')

    def _from_atlas_index(self, index: int) -> Image.Image:
        items_per_row = self.terrain_atlas.width // self.TEXTURE_SIZE
        return self._from_atlas_coord(
            index % items_per_row,
            index // items_per_row
        )

    def _coord_to_index(self, x: int, y: int) -> int:
        items_per_row = self.terrain_atlas.width // self.TEXTURE_SIZE
        return y * items_per_row + x

    def _slab(self, block: Block, face: Face, view: Image.Image) -> Image.Image:
        if face in ('top', 'bottom'):
            return view

        view.paste(
            Image.new(
                mode='RGBA',
                size=(self.TEXTURE_SIZE, self.TEXTURE_SIZE // 2),
                color=(0, 0, 0, 0)
            ),
            (0, 0, view.width, view.height // 2) if block.meta == 0 else (0, view.height // 2, view.width, view.height)
        )
        return view

    def _stair(self, block: Block, face: Face, view: Image.Image) -> Image.Image:
        if face in ('top', 'bottom', 'front', 'back'):
            return view

        view.paste(
            Image.new(
                'RGBA',
                (self.TEXTURE_SIZE // 2, self.TEXTURE_SIZE // 2),
                (0, 0, 0, 0)
            ),
            (
                (
                    (self.TEXTURE_SIZE // 2, 0, self.TEXTURE_SIZE, self.TEXTURE_SIZE // 2)
                    if block.meta == 0
                    else (0, 0, self.TEXTURE_SIZE // 2, self.TEXTURE_SIZE // 2)
                )
                if face == 'left'
                else (
                    (0, 0, self.TEXTURE_SIZE // 2, self.TEXTURE_SIZE // 2)
                    if block.meta == 0
                    else (self.TEXTURE_SIZE // 2, 0, self.TEXTURE_SIZE, self.TEXTURE_SIZE // 2)
                )
            )
        )
        return view

    def _map_texture(self, block: Block, face: Face) -> Image.Image:
        if block.id == BlockIDs.AIR:
            return self.INVISIBLE
        if block.id == BlockIDs.STONE:
            return self._from_atlas_coord(4, 0)
        if block.id == BlockIDs.GRASS_BLOCK:
            if face == 'top':
                return self._from_atlas_coord(3, 0)
            if face == 'bottom':
                return self.bottom(Block.from_id(BlockIDs.DIRT))
            return self._from_atlas_index(self._coord_to_index(1, 0) + block.meta)
        if block.id == BlockIDs.DIRT:
            return self._from_atlas_coord(21, 0)
        if block.id == BlockIDs.COBBLESTONE:
            return self._from_atlas_coord(5, 0)
        if block.id == BlockIDs.PLANK:
            return self._from_atlas_index(self._coord_to_index(22, 0) + block.meta)
        if block.id == BlockIDs.SAPLING:
            if face in ('top', 'bottom'):
                return self.INVISIBLE
            return self._from_atlas_index(self._coord_to_index(4, 1) + block.meta)
        if block.id == BlockIDs.BEDROCK:
            return self._from_atlas_coord(11, 0)
        if block.id == BlockIDs.WATER:
            return self._from_atlas_coord(0, 9)
        if block.id == BlockIDs.WATER_SOURCE:
            return self._from_atlas_coord(22, 7)
        if block.id == BlockIDs.LAVA:
            return self._from_atlas_coord(2, 9)
        if block.id == BlockIDs.LAVA_SOURCE:
            return self._from_atlas_coord(23, 7)
        if block.id == BlockIDs.SAND:
            return self._from_atlas_coord(14, 0)
        if block.id == BlockIDs.GRAVEL:
            return self._from_atlas_coord(20, 0)
        if block.id == BlockIDs.GOLD_ORE:
            return self._from_atlas_coord(0, 2)
        if block.id == BlockIDs.IRON_ORE:
            return self._from_atlas_coord(1, 2)
        if block.id == BlockIDs.COAL_ORE:
            return self._from_atlas_coord(2, 2)
        if block.id == BlockIDs.LOG:
            if face in ('top', 'bottom'):
                return self._from_atlas_index(self._coord_to_index(9, 1) + block.meta * 2)
            return self._from_atlas_index(self._coord_to_index(8, 1) + block.meta * 2)
        if block.id == BlockIDs.LEAVES:
            return self._from_atlas_index(self._coord_to_index(30, 2) + block.meta)
        if block.id == BlockIDs.SPONGE:
            return self._from_atlas_coord(24, 2)
        if block.id == BlockIDs.GLASS:
            return self._from_atlas_coord(25, 2)
        if block.id == BlockIDs.LAPIS_LAZULI_ORE:
            return self._from_atlas_coord(3, 2)
        if block.id == BlockIDs.LAPIS_LAZULI_BLOCK:
            return self._from_atlas_coord(20, 1)
        if block.id == BlockIDs.BID_23:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.SANDSTONE:
            if face == 'top':
                return self._from_atlas_coord(18, 0)
            if face == 'bottom':
                return self._from_atlas_coord(19, 0)
            return self._from_atlas_index(self._coord_to_index(15, 0) + block.meta)
        if block.id == BlockIDs.BID_25:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BED:
            if block.meta == 0:
                if face == 'top':
                    return self._from_atlas_coord(5, 5)
                if face == 'front':
                    return self._from_atlas_coord(6, 5)
                if face == 'right':
                    return self._from_atlas_coord(7, 5)
                if face == 'left':
                    return self._from_atlas_coord(7, 5).transform(
                        (self.TEXTURE_SIZE, self.TEXTURE_SIZE),
                        Image.FLIP_LEFT_RIGHT
                    )
                # no bottom, back?
            if block.meta == 1:
                if face == 'top':
                    return self._from_atlas_coord(8, 5)
                if face == 'back':
                    return self._from_atlas_coord(9, 5)
                if face == 'right':
                    return self._from_atlas_coord(10, 5)
                if face == 'left':
                    return self._from_atlas_coord(10, 5).transform(
                        (self.TEXTURE_SIZE, self.TEXTURE_SIZE),
                        Image.FLIP_LEFT_RIGHT
                    )
                # no bottom, front?
        if block.id == BlockIDs.POWERED_RAIL:
            if face == 'top':
                return self._from_atlas_coord(0, 5)
        if block.id == BlockIDs.BID_28:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_29:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.COBWEB:
            if face in ('top', 'bottom'):
                return self.INVISIBLE
            return self._from_atlas_coord(1, 1)
        if block.id in (BlockIDs.DEAD_SHRUB, BlockIDs.BEAD_BUSH):
            if face in ('top', 'bottom'):
                return self.INVISIBLE
            return self._from_atlas_coord(9, 2)
        if block.id == BlockIDs.BID_33:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_34:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.WOOL:
            return self._from_atlas_index(self._coord_to_index(24, 7) + block.meta)
        if block.id == BlockIDs.BID_36:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.YELLOW_FLOWER:
            if face in ('top', 'bottom'):
                return self.INVISIBLE
            return self._from_atlas_coord(3, 1)
        if block.id == BlockIDs.CYAN_FLOWER:
            if face in ('top', 'bottom'):
                return self.INVISIBLE
            return self._from_atlas_coord(2, 1)
        if block.id == BlockIDs.BROWN_MUSHROOM:
            if face in ('top', 'bottom'):
                return self.INVISIBLE
            return self._from_atlas_coord(31, 0)
        if block.id == BlockIDs.RED_MUSHROOM:
            if face in ('top', 'bottom'):
                return self.INVISIBLE
            return self._from_atlas_coord(30, 0)
        if block.id == BlockIDs.GOLD_BLOCK:
            return self._from_atlas_coord(17, 1)
        if block.id == BlockIDs.IRON_BLOCK:
            return self._from_atlas_coord(16, 1)
        if block.id == BlockIDs.DOUBLE_STONE_SLAB:
            if face in ('top', 'bottom'):
                return self._from_atlas_coord(26, 0)
            return self._from_atlas_coord(27, 0)
        if block.id == BlockIDs.STONE_SLAB:
            return self._slab(block, face, self._from_atlas_index(self._coord_to_index(27, 0)))
        if block.id == BlockIDs.BRICK_BLOCK:
            return self._from_atlas_coord(28, 0)
        if block.id == BlockIDs.TNT:
            if face == 'top':
                return self._from_atlas_coord(30, 0)
            if face == 'bottom':
                return self._from_atlas_coord(31, 0)
            return self._from_atlas_coord(29, 0)
        if block.id == BlockIDs.BOOKSHELF:
            if face in ('top', 'bottom'):
                return self._from_block(Block.from_id(BlockIDs.PLANK), face=face)
            return self._from_atlas_coord(0, 1)
        if block.id == BlockIDs.MOSSY_COBBLESTONE:
            return self._from_atlas_coord(6, 0)
        if block.id == BlockIDs.OBSIDIAN:
            return self._from_atlas_coord(12, 0)
        if block.id == BlockIDs.TORCH:
            if face == 'top':
                view = self.INVISIBLE.copy()
                view.paste(
                    self._from_atlas_coord(18, 3).crop((7, 6, 9, 8)),
                    (7, 6)
                )
                return view
            if face == 'bottom':
                view = self.INVISIBLE.copy()
                view.paste(
                    self._from_atlas_coord(18, 3).crop((7, 8, 9, 10)),
                    (7, 8)
                )
                return view
            return self._from_atlas_coord(18, 3)
        if block.id == BlockIDs.FIRE:
            return self.INVISIBLE
        if block.id == BlockIDs.MOB_SPAWNER:
            return self._from_atlas_coord(6, 3)
        if block.id == BlockIDs.WOODEN_STAIRS:
            return self._stair(
                block,
                face,
                self._from_block(Block.from_id(BlockIDs.PLANK), face=face)
            )
        if block.id == BlockIDs.CHEST:
            if face == 'bottom':
                return self._from_atlas_coord(18, 7)
            if face == 'front':
                return self._from_atlas_coord(20, 7)
            return self._from_atlas_coord(19, 7)
        if block.id == BlockIDs.BID_55:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.DIAMOND_ORE:
            return self._from_atlas_coord(4, 2)
        if block.id == BlockIDs.DIAMOND_BLOCK:
            return self._from_atlas_coord(18, 1)
        if block.id == BlockIDs.CRAFTING_TABLE:
            if face == 'top':
                return self._from_atlas_coord(13, 2)
            if face == 'bottom':
                return self._from_block(Block.from_id(BlockIDs.PLANK), face=face)
            if face in ('left', 'right'):
                return self._from_atlas_coord(14, 2)
            return self._from_atlas_coord(15, 2)
        if block.id == BlockIDs.WHEAT_SEEDS:
            return self.INVISIBLE
        if block.id == BlockIDs.FARMLAND:
            if face == 'top':
                return self._from_atlas_index(self._coord_to_index(29, 3) - block.meta)
            if face == 'bottom':
                return self._from_block(Block.from_id(BlockIDs.DIRT), face=face)
            transparent = self.INVISIBLE.copy().crop((0, 0, int(self.TEXTURE_SIZE * 0.1), int(self.TEXTURE_SIZE * 0.1)))
            view = self._from_block(Block.from_id(BlockIDs.DIRT), face=face)
            view.paste(transparent)
            return view
        if block.id == BlockIDs.FURNACE:
            if face == 'front':
                return self._from_atlas_index(self._coord_to_index(16, 2))
            if face in ('top', 'bottom'):
                return self._from_atlas_coord(18, 2)
            return self._from_atlas_coord(19, 2)
        if block.id == BlockIDs.BURNING_FURNACE:
            if face == 'front':
                return self._from_atlas_coord(17, 2)
            return self._from_block(Block.from_id(BlockIDs.FURNACE), face=face)
        if block.id == BlockIDs.SIGN_POST:
            return self.INVISIBLE
        if block.id == BlockIDs.WOODEN_DOOR:
            return self.INVISIBLE
        if block.id == BlockIDs.LADDER:
            return self.INVISIBLE
        if block.id == BlockIDs.RAIL:  # TODO rotation
            return self._from_atlas_index(self._coord_to_index(29, 4) + block.meta)
        if block.id == BlockIDs.COBBLESTONE_STAIRS:
            return self._stair(
                block,
                face,
                self._from_block(Block.from_id(BlockIDs.COBBLESTONE), face=face)
            )
        if block.id == BlockIDs.WALL_SIGN:
            return self.INVISIBLE
        if block.id == BlockIDs.BID_69:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_70:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.IRON_DOOR:
            return self.INVISIBLE
        if block.id == BlockIDs.BID_72:
            return self.DOES_NOT_EXIST
        if block.id in (BlockIDs.REDSTONE_ORE, BlockIDs.GLOWING_REDSTONE_ORE):
            return self._from_atlas_coord(5, 2)
        if block.id == BlockIDs.BID_75:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_76:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_77:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.SNOW:
            if face in ('top', 'bottom'):
                return self._from_atlas_coord(7, 3)
            transparent = self.INVISIBLE.copy().crop((0, 0, int(self.TEXTURE_SIZE * 0.95), int(self.TEXTURE_SIZE * 0.95)))
            view = self._from_atlas_coord(7, 3)
            view.paste(transparent)
            return view
        if block.id == BlockIDs.ICE:
            return self._from_atlas_coord(8, 3)
        if block.id == BlockIDs.SNOW_BLOCK:
            return self._from_atlas_coord(7, 3)
        if block.id == BlockIDs.CACTUS:
            if face == 'top':
                return self._from_atlas_coord(9, 3)
            if face == 'bottom':
                return self._from_atlas_coord(11, 3)
            return self._from_atlas_coord(10, 3)
        if block.id == BlockIDs.CLAY_BLOCK:
            return self._from_atlas_coord(13, 0)
        if block.id == BlockIDs.SUGAR_CANE:
            if face in ('top', 'bottom'):
                return self.INVISIBLE
            return self._from_atlas_coord(12, 3)
        if block.id == BlockIDs.BID_84:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.FENCE:
            view = self.INVISIBLE.copy()
            view.paste(
                self._from_block(Block.from_id(BlockIDs.PLANK), face=face).crop(
                    (self.TEXTURE_SIZE // 2 - 2, self.TEXTURE_SIZE // - 2, self.TEXTURE_SIZE // 2 + 2, self.TEXTURE_SIZE // 2 + 2)
                ),
                (self.TEXTURE_SIZE // 2 - 2, self.TEXTURE_SIZE // 2 - 2)
            )
            return view
        if block.id == BlockIDs.BID_86:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.NETHERRACK:
            return self._from_atlas_coord(11, 4)
        if block.id == BlockIDs.BID_88:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_89:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_90:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_91:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_92:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_93:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_94:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_95:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.TRAPDOOR:
            return self._from_atlas_coord(4, 4)
        if block.id == BlockIDs.BID_97:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.STONE_BRICKS:
            return self._from_atlas_index(self._coord_to_index(7, 0) + block.meta)
        if block.id == BlockIDs.BID_99:
            return self.DOES_NOT_EXIST
        if block.id == BlockIDs.BID_100:
            return self.DOES_NOT_EXIST

        return self.MISSING

    def _from_block(self, block: Block, face: Face) -> Image.Image:
        if block.is_transparent:
            if block.position.y > 0 and self.world is not None:
                try:
                    return Image.alpha_composite(
                        self._from_block(self.world.get_block(block.position.down()), 'top'),
                        self._map_texture(block, face)
                    )
                except Exception as e:
                    raise Exception(f'Error at block {block}') from e
            return self.INVISIBLE
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
