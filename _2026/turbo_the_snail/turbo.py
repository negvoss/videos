from manim_imports_ext import *
import random

class Tile(Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.top = TexturedSurface(
            Square3D(side_length = 1),
            "turbo_grid_assets/grass.png"
        )
        # self.block = Prism(
        # 	width = 1,
        # 	height = 1,
        # 	depth = 0.1
        # ).set_color(GREY)
        self.bot = TexturedSurface(
            Square3D(side_length = 1),
            "turbo_grid_assets/concrete.png"
        )
        self.add(self.top, self.bot)
        self.arrange(IN, buff = 0.001)

    def reveal(self, axis = RIGHT):
        if self.top.get_z() > self.bot.get_z():
            return Rotate(self, axis = axis, angle = PI)
        else:
            return Animation(Mobject())


class Turbo(Group):
    def __init__(self, grid, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid = grid
        self.add(Sphere(radius = 0.3).move_to(self.grid.get_tile(0, 0)).align_to(self.grid.get_tile(0, 0).get_zenith(), IN).shift(OUT*0.01))
        self.current_position = [0, 0]

    def move_to_position(self, i, j, **kwargs):
        target_tile = self.grid.get_tile(i, j)
        self.current_position = [i, j]
        return self.animate(**kwargs).match_x(target_tile).match_y(target_tile)

    def move_to_start(self, **kwargs):
        target_tile = self.grid.get_tile(0, 0)
        start_center = self.get_center()
        end_center = target_tile.get_center()
        move_vector = end_center - start_center
        
        arc_axis = np.cross(move_vector, IN)
        
        return self.move_to_position(
            0, 0,
            path_arc = PI*0.8,
            path_arc_axis = arc_axis,
            **kwargs
        )

    def move(self, direction):
        i, j = self.current_position
        if (direction == UP).all():
            new_position = (i, j - 1)
        elif (direction == RIGHT).all():
            new_position = (i + 1, j)
        elif (direction == DOWN).all():
            new_position = (i, j + 1)
        elif (direction == LEFT).all():
            new_position = (i - 1, j)
        else:
            raise ValueError("Direction of movement must be UP, RIGHT, DOWN, or LEFT")

        reveal_anim = self.grid.reveal_tile(*new_position, axis = [new_position[1] - j, new_position[0] - i, 0])
        if self.grid.is_monster(*new_position):
            reveal_anim = self.grid.reveal_monster(*new_position)
        return AnimationGroup(self.move_to_position(*new_position), reveal_anim, lag_ratio = 0.3)

class Monster(Group):
    def __init__(self, i, j, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add(Prism(width = 0.3, height = 0.3, depth = 1.2).set_color(RED))


class TurboGrid(Group):
    def __init__(self, n, monster_positions = [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.monster_positions = monster_positions

        self.tiles = Group(*[
            Tile()
            for _ in range(n*(n - 1))
        ]).arrange_in_grid(n_rows = n, n_cols = n - 1, buff = 0)
        self.get_row(0).flip(axis = RIGHT)
        self.get_row(self.n - 1).flip(axis = RIGHT)
        self.add(self.tiles)

        self.monsters = Group(*[
            Monster(i, j).move_to(self.get_tile(i, j)).align_to(self.get_tile(i, j).get_zenith(), IN).shift(OUT*0.01).set_opacity(0)
            for (i, j) in self.monster_positions
        ])
        self.add(self.monsters)

        self.turbo = Turbo(self)
        self.add(self.turbo)

    def create(self):
        tiles_sorted_from_center = sorted(self.tiles, key = lambda t: np.linalg.norm(t.get_center() - self.tiles.get_center()))
        return AnimationGroup(
            *[
                FadeIn(tile, shift = IN*0.3)
                for tile in tiles_sorted_from_center
            ],
            FadeIn(self.turbo, shift = IN*0.3)
        , lag_ratio = 0.1)

    def get_tile(self, i, j):
        if i < 0: raise IndexError("Tile column index is negative")
        if j < 0: raise IndexError("Tile row index is negative")
        if i >= self.n - 1: raise IndexError("Tile column index is greater than the number of columns")
        if j >= self.n: raise IndexError("Tile row index is greater than the number of rows")
        return self.tiles[i + j*(self.n - 1)]

    def reveal_tile(self, i, j, axis = RIGHT):
        return self.get_tile(i, j).reveal(axis = axis)

    def get_col(self, i):
        return Group(*[self.get_tile(i, j) for j in range(self.n)])

    def get_row(self, j):
        return Group(*[self.get_tile(i, j) for i in range(self.n - 1)])

    def is_monster(self, i, j):
        return (i, j) in self.monster_positions

    def reveal_monster(self, i, j):
        if not self.is_monster(i, j): raise LookupError(F"No monster at position ({i}, {j})")
        for monster, pos in zip(self.monsters, self.monster_positions):
            if pos == (i, j): break
        monster_tile = self.get_tile(i, j)
        def dist_to_monster_tile(tile):
            return np.linalg.norm(tile.get_center() - monster_tile.get_center())
        monster_col = sorted(self.get_col(i), key = dist_to_monster_tile)
        monster_row = sorted(self.get_row(j), key = dist_to_monster_tile)
        monster_col.remove(monster_tile)
        monster_row.remove(monster_tile)
        return AnimationGroup(
            monster_tile.reveal(),
            monster.animate.set_opacity(1),
            AnimationGroup(
                AnimationGroup(*[
                    t.reveal()
                    for t in monster_row
                ], lag_ratio = 0.1),
                AnimationGroup(*[
                    t.reveal()
                    for t in monster_col
                ], lag_ratio = 0.1)
            )
        , lag_ratio = 0.2)

class TurboScene(InteractiveScene):
    def __init__(self, n, monster_positions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid = TurboGrid(n, monster_positions)
        self.turbo = self.grid.turbo

    def move_turbo(self, direction, *args, **kwargs):
        self.play(self.turbo.move(direction), *args, **kwargs)
        if self.grid.is_monster(*self.turbo.current_position):
        	self.play(self.turbo.move_to_start())


class TurboTest(TurboScene, ThreeDScene):
    def __init__(self, *args, **kwargs):
        n = 10
        super().__init__(n, [(i, i) for i in range(1, n - 1)], *args, **kwargs)

    def construct(self):
        # Set the camera
        self.camera.frame.reorient(26, 58, 0, (-0.19, -0.72, -0.82), 8.21)

        # Add the grid
        grid, turbo = self.grid, self.turbo
        self.play(
            self.camera.frame.animate.reorient(-8, 38, 0, (-0.56, -0.79, -0.65), 9.93),
            grid.create()
        , run_time = 4)

        # Label the number of rows with "N"
        brace = Brace(grid.tiles, LEFT, buff = 0.4)
        label = brace.get_tex("N", font_size = 100)
        self.play(
            Succession(
                AnimationGroup(
                    GrowFromEdge(brace, RIGHT),
                    Write(label)
                , run_time = 1),
                Animation(VMobject(), run_time = 4),
                FadeOut(VGroup(brace, label), run_time = 1)
            ),
            self.camera.frame.animate(run_time = 30, rate_func = there_and_back).reorient(13, 47, 0, (0.82, -0.71, -0.92), 9.93)
        )

        # Move turbo
        moves = [RIGHT, RIGHT, RIGHT, DOWN, DOWN, DOWN]
        for direction in moves:
            self.move_turbo(direction, run_time = 0.5)
        moves = [DOWN, DOWN, DOWN, RIGHT, RIGHT, DOWN, RIGHT, DOWN, DOWN, DOWN, DOWN, DOWN]
        for direction in moves:
            self.move_turbo(direction, run_time = 0.5)


class SpriteTest(InteractiveScene):
    def construct(self):
        # Grid test
        sprite = Sprite("runner_sprite.gif", height=2)
        sprites = sprite.get_grid(5, 7, buff_ratio=0.1)
        sprites.set_height(7)
        sprites.sort(lambda p: get_norm(p))

        self.add(sprites)
        self.play(LaggedStart(
            (sprite.animate_set_time(10).rotate(90 * DEG)
            for sprite in sprites),
            lag_ratio=0.025,
            group=sprites,
        ))