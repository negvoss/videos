from manim_imports_ext import *
import random

SPRITES_DIRECTORY = None


class TileFlip(Animation):
    def __init__(self, tile, axis=RIGHT, depth_margin=0.2, **kwargs):
        self.axis = normalize(np.array(axis, dtype=float))
        self.depth_margin = depth_margin
        super().__init__(tile, **kwargs)

    def begin(self):
        self.center = self.mobject.get_center().copy()
        half_extent = max(self.mobject.get_width(), self.mobject.get_height()) / 2
        self.depth = half_extent * (1 + self.depth_margin)
        super().begin()

    def interpolate_mobject(self, alpha):
        angle = PI * self.rate_func(alpha)

        pairs = zip(
            self.mobject.family_members_with_points(),
            self.starting_mobject.family_members_with_points()
        )
        for sm1, sm2 in pairs:
            for key in sm1.pointlike_data_keys:
                sm1.data[key][:] = sm2.data[key]

        self.mobject.rotate(angle, axis=self.axis, about_point=self.center)
        self.mobject.shift(IN * self.depth * np.sin(angle))


class Tile(Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.top = TexturedSurface(
            Square3D(side_length=1),
            os.path.join(SPRITES_DIRECTORY, "Manim-TileSet-1.png")
        )
        self.bot = TexturedSurface(
            Square3D(side_length=1),
            os.path.join(SPRITES_DIRECTORY, "Manim-TileSet-5.png")
        )
        self.add(self.top, self.bot)
        self.arrange(IN, buff=0.001)

    def reveal(self, axis=RIGHT, run_time=0.5, **kwargs):
        if self.top.get_z() > self.bot.get_z():
            return TileFlip(self, axis=axis, run_time=run_time, **kwargs)
        else:
            return Animation(Mobject(), run_time=run_time, **kwargs)


class Turbo(Sprite):
    IDLE_KEYFRAME_0 = 0
    IDLE_KEYFRAME_1 = 0.69

    def __init__(self, grid, *args, **kwargs):
        self.grid = grid
        self.current_position = [0, 0]
        super().__init__(
            os.path.join(SPRITES_DIRECTORY, "turbo.gif"),
            height=grid.get_tile(0, 0).get_height() * 0.8,
            *args,
            **kwargs
        )
        self.move_to(
            self.grid.get_tile(0, 0)
        ).align_to(
            self.grid.get_tile(0, 0).get_zenith(), IN
        ).shift(
            OUT * 0.02
        )

        self.time_tracker = ValueTracker(self.IDLE_KEYFRAME_0)
        # Hacky fix below: if self.time_tracker.add_updater(lambda t: self.set_time(t.get_value())) is used,
        # it causes the tracker to get stuck oscillating between the two keyframe values, since the other .animates
        # create copies of the tracker.
        self.time_tracker.add_updater(lambda _: self.set_time(self.time_tracker.get_value()))

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
            path_arc=PI * 0.8,
            path_arc_axis=arc_axis,
            **kwargs
        )

    def move(self, direction, run_time=0.5):
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

        reveal_anim = self.grid.reveal_tile(*new_position, axis=[new_position[1] - j, new_position[0] - i, 0])
        if self.grid.is_monster(*new_position):
            reveal_anim = self.grid.reveal_monster(*new_position)
        self.time_tracker.set_value(self.IDLE_KEYFRAME_0)
        return AnimationGroup(
            AnimationGroup(
                self.move_to_position(*new_position),
                self.time_tracker.animate.set_value(self.IDLE_KEYFRAME_1), run_time=run_time),
            reveal_anim, lag_ratio=0.3)


class Monster(Sprite):
    def __init__(self, grid, i, j, *args, **kwargs):
        self.grid = grid
        super().__init__(
            os.path.join(SPRITES_DIRECTORY, "monster.gif"),
            height=self.grid.get_tile(i, j).get_height() * 0.8,
            *args,
            **kwargs
        )
        self.move_to(
            self.grid.get_tile(i, j)
        ).align_to(
            self.grid.get_tile(i, j).get_zenith(), IN
        ).shift(
            OUT * 0.04
        )


class TurboGrid(Group):
    def __init__(self, n, monster_positions=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.monster_positions = monster_positions

        self.tiles = Group(*[
            Tile()
            for _ in range(n * (n - 1))
        ]).arrange_in_grid(
            n_rows=n, n_cols=n - 1, buff=0
        ).set_z_index(0)
        self.get_row(0).flip(axis=RIGHT)
        self.get_row(self.n - 1).flip(axis=RIGHT)
        self.add(self.tiles)

        self.turbo = Turbo(self).set_z_index(100)
        self.monsters = Group(*[
            Monster(self, i, j)
            for (i, j) in self.monster_positions
        ]).set_z_index(200)
        self.add(self.turbo, self.monsters)

    def create(self):
        tiles_sorted_from_center = sorted(self.tiles, key=lambda t: np.linalg.norm(t.get_center() - self.tiles.get_center()))
        return AnimationGroup(
            *[
                FadeIn(tile, shift=IN * 0.3)
                for tile in tiles_sorted_from_center
            ],
            FadeIn(self.turbo, shift=IN * 0.3),
            FadeIn(self.monsters), lag_ratio=0.1)

    def get_tile(self, i, j):
        if i < 0:
            raise IndexError("Tile column index is negative")
        if j < 0:
            raise IndexError("Tile row index is negative")
        if i >= self.n - 1:
            raise IndexError("Tile column index is greater than the number of columns")
        if j >= self.n:
            raise IndexError("Tile row index is greater than the number of rows")
        return self.tiles[i + j * (self.n - 1)]

    def reveal_tile(self, i, j, axis=RIGHT):
        return self.get_tile(i, j).reveal(axis=axis)

    def get_col(self, i):
        return Group(*[self.get_tile(i, j) for j in range(self.n)])

    def get_row(self, j):
        return Group(*[self.get_tile(i, j) for i in range(self.n - 1)])

    def is_monster(self, i, j):
        return (i, j) in self.monster_positions

    def get_monster(self, i, j):
        for monster, pos in zip(self.monsters, self.monster_positions):
            if pos == (i, j):
                return monster
        raise LookupError(F"No monster at position ({i}, {j})")

    def reveal_monster(self, i, j, run_time=3):
        monster = self.get_monster(i, j)
        monster_tile = self.get_tile(i, j)

        def dist_to_monster_tile(tile):
            return np.linalg.norm(tile.get_center() - monster_tile.get_center())
        monster_col = sorted(self.get_col(i), key=dist_to_monster_tile)
        monster_row = sorted(self.get_row(j), key=dist_to_monster_tile)
        monster_col.remove(monster_tile)
        monster_row.remove(monster_tile)
        return AnimationGroup(
            monster_tile.reveal(),
            monster.animate_set_time(1),
            AnimationGroup(
                AnimationGroup(*[
                    t.reveal()
                    for t in monster_row
                ], lag_ratio=0.1),
                AnimationGroup(*[
                    t.reveal()
                    for t in monster_col
                ], lag_ratio=0.1)
            ), lag_ratio=0.2, run_time=run_time)


class TurboScene(InteractiveScene):
    def __init__(self, n, monster_positions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global SPRITES_DIRECTORY
        SPRITES_DIRECTORY = os.path.join(self.file_writer.output_directory.parent, "Mitchell-Demos", "ManimPlaceholders")

        self.grid = TurboGrid(n, monster_positions)
        self.turbo = self.grid.turbo

    def move_turbo(self, direction, *args, **kwargs):
        self.play(self.turbo.move(direction), *args, **kwargs)
        if self.grid.is_monster(*self.turbo.current_position):
            monster = self.grid.get_monster(*self.turbo.current_position)
            self.play(
                AnimationGroup(
                    self.turbo.move_to_start(),
                    monster.animate_set_time(2), lag_ratio=0.6)
            )


class TurboTest(TurboScene, ThreeDScene):
    def __init__(self, *args, **kwargs):
        n = 6
        super().__init__(n, [(i, i) for i in range(1, n - 1)], *args, **kwargs)

    def construct(self):
        # Set the camera
        self.camera.frame.reorient(26, 58, 0, (-0.19, -0.72, -0.82), 8.21)

        # Add the grid
        grid, turbo = self.grid, self.turbo
        self.play(
            self.camera.frame.animate.reorient(-8, 38, 0, (-0.56, -0.79, -0.65), 9.93),
            grid.create(), run_time=4)

        # Label the number of rows with "N"
        brace = Brace(grid.tiles, LEFT, buff=0.4)
        label = brace.get_tex("N", font_size=100)
        self.play(
            Succession(
                AnimationGroup(
                    GrowFromEdge(brace, RIGHT),
                    Write(label), run_time=1),
                Animation(VMobject(), run_time=4),
                FadeOut(VGroup(brace, label), run_time=1)
            ),
            self.camera.frame.animate(run_time=30, rate_func=there_and_back).reorient(13, 47, 0, (0.82, -0.71, -0.92), 9.93)
        )

        # Reset the camera to an overhead position
        self.play(self.camera.frame.animate.reorient(0, 0, 0, (0, 0, 0), 7), run_time=2)

        # Move turbo
        moves = [RIGHT, RIGHT, RIGHT, DOWN, DOWN, DOWN]
        for direction in moves:
            self.move_turbo(direction)
        # moves = [DOWN, DOWN, DOWN, RIGHT, RIGHT, DOWN, RIGHT, DOWN, DOWN, DOWN, DOWN, DOWN]
        # for direction in moves:
        #     self.move_turbo(direction, run_time = 0.5)
