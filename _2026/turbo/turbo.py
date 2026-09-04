from manim_imports_ext import *
import random


class TurboGrid(Group):
	def __init__(self, n, monster_positions = None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.n = n
		self.monster_positions = monster_positions

		self.tiles = Group(*[
			Group(
				TexturedSurface(
					ParametricSurface(lambda u, v: [u, v, 0], u_range = (0, 1), v_range = (0, 1)),
					"turbo_grid_assets/grass.png"
				),
				Prism(
					width = 1,
					height = 1,
					depth = 0.1
				).set_color(GREY),
				TexturedSurface(
					ParametricSurface(lambda u, v: [u, v, 0], u_range = (0, 1), v_range = (0, 1)),
					"turbo_grid_assets/concrete.png"
				)
			).arrange(IN, buff = 0.001)
			for _ in range(n*(n - 1))
		]).arrange_in_grid(n_rows = n, n_cols = n - 1, buff = 0)
		self.add(self.tiles)

		self.turbo = Sphere(radius = 0.3).move_to(self.tiles[0]).align_to(self.tiles[0].get_zenith(), IN).shift(OUT*0.01)

	def create(self):
		return Succession(
			AnimationGroup(*[
				FadeIn(tile, shift = OUT*0.1)
				for tile in self.tiles
			], lag_ratio = 0.1),
			FadeIn(self.turbo, shift = IN*0.3)
		)


class TurboTest(InteractiveScene):
    def construct(self):
        # Add a grid
        grid = TurboGrid(5)
        self.play(grid.create())
