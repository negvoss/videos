from manim_imports_ext import *


class Subsets(InteractiveScene):
    def __init__(self, min_example_elements = 1, *args, **kwargs):
        self.min_example_elements = min_example_elements
        super().__init__(*args, **kwargs)

    def construct(self):
        # Add pi creatures
        randy, morty = pis = VGroup(Randolph(), Mortimer())
        pis.arrange(RIGHT)

        self.play(LaggedStart(
            VFadeIn(randy),
            randy.change("tease", morty.eyes),
            VFadeIn(morty),
            morty.change("hesitant", randy.eyes),
            lag_ratio=0.5,
            run_time=1.5
        ))
        self.play(Blink(randy))

        # Add numbers
        number_grid = VGroup(Integer(n) for n in range(1, 101))
        number_grid.arrange_in_grid(10, 10, v_buff=0.3, h_buff=0.1)
        number_grid.set_width(5)
        number_grid.to_edge(UP)

        self.play(
            FadeIn(number_grid, lag_ratio=0.01, shift=0.05 * UP, run_time=2),
            randy.change("pondering", number_grid).set_height(1).next_to(number_grid, DOWN, 1.25, LEFT),
            morty.change("raise_right_hand").set_height(1.5).next_to(number_grid, DOWN, 0.75, RIGHT),
        )
        self.wait()

        # Choose a random subset
        sample_list = random.sample(list(number_grid), 10)
        sample_list.sort(key=lambda m: m.get_value())
        sample = VGroup(*sample_list)
        number_grid.remove(*sample)
        sample_rects = VGroup(
            SurroundingRectangle(num, buff=0.1)
            for num in sample
        )
        sample_rects.set_stroke(TEAL, 2)

        self.play(
            number_grid.animate.set_fill(opacity=0.25).set_anim_args(lag_ratio=0.005),
            sample.animate.set_fill(TEAL).set_anim_args(lag_ratio=0.2),
            Write(sample_rects),
            run_time=3
        )
        self.play(Blink(morty))
        self.wait()

        # Organize
        sample_groups = VGroup(
            VGroup(num, rect)
            for num, rect in zip(sample, sample_rects)
        )
        sample_groups.target = sample_groups.generate_target()
        sample_groups.target.arrange_in_grid(2, 5)
        sample_groups.target.set_width(number_grid.get_width())
        sample_groups.target.next_to(pis, UP, MED_LARGE_BUFF)

        self.play(
            MoveToTarget(sample_groups),
            FadeOut(number_grid),
            randy.change("hesitant", sample_groups),
            morty.change("tease", randy.eyes),
        )
        self.play(
            Blink(randy),
            FadeOut(sample_rects),
        )
        self.wait()
        self.play(
            randy.animate.set_height(1.25, about_edge=DL),
            morty.animate.set_height(0.75, about_edge=DR),
        )
        self.wait()

        # Find a collision
        groups = self.find_a_match(sample, min_total_elements = self.min_example_elements).copy()
        group_rects = self.get_group_rects(groups)

        self.play(
            randy.change("raise_right_hand"),
            sample.animate.set_fill(WHITE, 0.5),
            groups[0].animate.set_fill(group_rects[0].get_color(), 1),
            Write(group_rects[0], run_time=1.5, lag_ratio=0.2),
        )
        self.play(
            groups[1].animate.set_fill(group_rects[1].get_color(), 1),
            Write(group_rects[1], run_time=1.5, lag_ratio=0.2),
        )
        self.wait()

        # Show the same sum
        top_groups, plusses, equals = equation = self.get_top_sum(groups)

        self.play(LaggedStart(
            TransformFromCopy(groups[0], top_groups[0]),
            Write(plusses[0]),
            FadeIn(equals, UP),
            TransformFromCopy(groups[1], top_groups[1]),
            Write(plusses[1]),
            randy.change("happy"),
            morty.change("pondering")
        ))
        self.play(Blink(randy))
        self.wait()

        self.play(
            FadeOut(groups),
            FadeOut(group_rects),
            FadeOut(equation),
        )

        # Show some unequal subsets
        for n in range(40):
            subsets = VGroup(
                VGroup(*random.sample(list(sample), random.randint(2, 5)))
                for n in range(2)
            )
            intersection = [
                mob for mob in sample
                if mob in subsets[0] and mob in subsets[1]
            ]
            for subset in subsets:
                subset.remove(*intersection)
            if len(subsets[0]) == 0 or len(subsets[0]) == 0:
                break

            subsets = subsets.copy()
            rects = self.get_group_rects(subsets, colors=[RED, PINK])
            for subset, rect in zip(subsets, rects):
                subset.set_fill(rect.get_color(), 1)

            equation = self.get_top_sum(subsets)

            self.add(subsets, rects, equation)
            randy.change_mode("hesitant")
            self.wait(0.5)
            self.remove(subsets, rects, equation)

    def find_a_match(self, group, min_total_elements = 1):
        value_to_mob = {mob.get_value(): mob for mob in group}
        values = list(value_to_mob.keys())
        sums_to_subsets = dict()
        match = None
        subsets = it.chain(*(
            it.combinations(values, n)
            for n in range(len(values))
        ))
        for subset in subsets:
            sub_sum = sum(subset)
            if sub_sum in sums_to_subsets:
                other_subset = sums_to_subsets[sub_sum]
                match = [
                    set(other_subset).difference(subset),
                    set(subset).difference(other_subset),
                ]
                if len(match[0]) + len(match[1]) >= min_total_elements:
                    break
            sums_to_subsets[sub_sum] = subset

        if match is None:
            return "No match found!"


        return VGroup(
            VGroup(
                value_to_mob[value]
                for value in match
            )
            for match in match
        )

    def get_group_rects(self, groups, colors=[BLUE, GREEN]):
        group_rects = VGroup(
            VGroup(SurroundingRectangle(mob) for mob in group)
            for group in groups
        )
        for rect, color in zip(group_rects, colors):
            rect.set_stroke(color, 2)
        return group_rects

    def get_top_sum(self, groups):
        top_groups = groups.copy()
        sums = []
        for group in top_groups:
            group.arrange(RIGHT, buff=0.5)
            sums.append(sum(m.get_value() for m in group))
        top_groups.arrange(DOWN, buff=1)
        top_groups.to_edge(UP)

        equals = Tex(R"=")
        equals.rotate(90 * DEG)
        equals.move_to(top_groups)
        if sums[0] != sums[1]:
            slash = Line(equals.get_bottom(), equals.get_top())
            slash.set_stroke(RED, 5)
            slash.rotate(45 * DEG)
            equals.add(slash)

        plusses = VGroup()
        for group in top_groups:
            plus_line = VGroup()
            for m1, m2 in zip(group, group[1:]):
                plus = Tex(R"+").move_to(midpoint(m1.get_right(), m2.get_left()))
                plus_line.add(plus)
            plusses.add(plus_line)

        return VGroup(top_groups, plusses, equals)


class Subsets2(Subsets):
    random_seed = 1

class Subsets3(Subsets):
    random_seed = 2

class Subsets4(Subsets):
    def __init__(self, *args, **kwargs):
        super().__init__(min_example_elements = 5, *args, **kwargs)
    random_seed = 3

class Subsets5(Subsets):
    def __init__(self, *args, **kwargs):
        super().__init__(min_example_elements = 6, *args, **kwargs)
    random_seed = 4

class Subsets6(Subsets):
    def __init__(self, *args, **kwargs):
        super().__init__(min_example_elements = 4, *args, **kwargs)
    random_seed = 5

class Subsets7(Subsets):
    def __init__(self, *args, **kwargs):
        super().__init__(min_example_elements = 7, *args, **kwargs)
    random_seed = 6

class Subsets8(Subsets):
    def __init__(self, *args, **kwargs):
        super().__init__(min_example_elements = 3, *args, **kwargs)
    random_seed = 7

class Subsets9(Subsets):
    def __init__(self, *args, **kwargs):
        super().__init__(min_example_elements = 4, *args, **kwargs)
    random_seed = 8

class Subsets10(Subsets):
    def __init__(self, *args, **kwargs):
        super().__init__(min_example_elements = 6, *args, **kwargs)
    random_seed = 9

class Subsets11(Subsets):
    random_seed = 10

class Subsets12(Subsets):
    random_seed = 11

class Subsets13(Subsets):
    random_seed = 12

class Subsets14(Subsets):
    random_seed = 13

class Subsets15(Subsets):
    random_seed = 13


class BinaryRepresentation(InteractiveScene):
    def construct(self):
        # Add pi creatures
        randy, morty = pis = VGroup(Randolph(), Mortimer())
        pis.arrange(RIGHT)

        self.play(LaggedStart(
            VFadeIn(randy),
            randy.change("tease", morty.eyes),
            VFadeIn(morty),
            morty.change("hesitant", randy.eyes),
            lag_ratio=0.5,
            run_time=1.5
        ))
        self.play(Blink(randy))

        # Add numbers
        number_grid = VGroup(Integer(n) for n in range(1, 101))
        number_grid.arrange_in_grid(10, 10, v_buff=0.3, h_buff=0.1)
        number_grid.set_width(5)
        number_grid.to_edge(UP)

        self.play(
            FadeIn(number_grid, lag_ratio=0.01, shift=0.05 * UP, run_time=2),
            randy.change("pondering", number_grid).set_height(1).next_to(number_grid, DOWN, 1.25, LEFT),
            morty.change("raise_right_hand").set_height(1.5).next_to(number_grid, DOWN, 0.75, RIGHT),
        )
        self.wait()

        # Choose a random subset
        sample_list = random.sample(list(number_grid), 10)
        sample_list.sort(key=lambda m: m.get_value())
        sample = VGroup(*sample_list)
        number_grid.remove(*sample)
        sample_rects = VGroup(
            SurroundingRectangle(num, buff=0.1)
            for num in sample
        )
        sample_rects.set_stroke(TEAL, 2)

        self.play(
            number_grid.animate.set_fill(opacity=0.25).set_anim_args(lag_ratio=0.005),
            sample.animate.set_fill(TEAL).set_anim_args(lag_ratio=0.2),
            Write(sample_rects),
            run_time=3
        )
        self.play(Blink(morty))
        self.wait()

        # Organize
        sample_groups = VGroup(
            VGroup(num, rect)
            for num, rect in zip(sample, sample_rects)
        )
        sample_groups.target = sample_groups.generate_target()
        sample_groups.target.arrange_in_grid(2, 5)
        sample_groups.target.set_width(number_grid.get_width())
        sample_groups.target.next_to(pis, UP, MED_LARGE_BUFF)

        self.play(
            MoveToTarget(sample_groups),
            FadeOut(number_grid),
            randy.change("hesitant", sample_groups),
            morty.change("tease", randy.eyes)
        )
        self.play(
            Blink(randy),
            FadeOut(sample_rects),
        )
        self.wait()

        # Represent the numbers in binary
        binary_representations = VGroup(*[
            Tex(f"{sample_list[i].get_value():010b}", font_size = 30).set_color(MAROON_B)
            for i in range(len(sample_groups))
        ]).arrange(DOWN, buff = 0.17).to_edge(UP, buff = 0.4)
        self.play(
            AnimationGroup(
                AnimationGroup(*[
                    ReplacementTransform(sample_groups[i][0], binary_representations[i], path_arc = PI*0.2)
                    for i in range(len(sample_groups))
                ], lag_ratio = 0.15, run_time = 2),
                morty.change("raise_right_hand")
            , lag_ratio = 0.1)
        )

        # Flicker through some different random samples and then land on one with all powers of 2
        num_samples = 4
        # samples = [random.sample(list(range(1, 101)), 10) for _ in range(3)] + [[1, 2, 4, 8, 16, 32, 64, 128, 256, 512]]
        samples = [
            VGroup(*[
                Tex(
                    (f"".join([str(random.choice([0, 1])) for _ in range(10)])) if i < num_samples - 1 else f"{2**j:010b}",
                    font_size = 30
                ).set_color(
                    MAROON_B
                ).move_to(
                    binary_representations[j]
                )
                for j in range(10)
            ])
            for i in range(num_samples)
        ]
        prev = binary_representations
        for sample in samples:
            self.play(randy.change("thinking", sample), AnimationGroup(FadeOut(prev), FadeIn(sample), lag_ratio = 0.3))
            prev = sample
            self.wait(0.2)
        final_sample = prev

        # Show the powers of 2
        for num in final_sample:
            num["1"].set_color(RED)
        for num in final_sample:
            num["0"].set_color(TEAL_A)
        final_sample.save_state()
        final_sample.set_color(MAROON_B)
        powers_of_2 = VGroup(*[
            Tex(f"2^{i} = ", font_size = 30).next_to(final_sample[i], LEFT, buff = 0.14)
            for i in range(len(final_sample))
        ])
        for i in range(len(powers_of_2)):
            powers_of_2[i].shift(UP*(final_sample[i].get_y() - powers_of_2[i][-1].get_y()))
        for num in final_sample:
            num.generate_target()
        VGroup(powers_of_2, VGroup(*[num.target for num in final_sample])).set_x(0)
        self.play(
            Blink(randy),
            AnimationGroup(*[
                AnimationGroup(
                    MoveToTarget(final_sample[i]),
                    FadeIn(powers_of_2[i], shift = RIGHT*0.3)
                , lag_ratio = 0.05)
                for i in range(len(powers_of_2))
            ], lag_ratio = 0.06)
        )
        powers_of_2_nums = final_sample.copy()
        self.play(Blink(morty))

        # Indicate the 1s and 0s
        for num in final_sample:
            num["1"].set_color(RED)
        self.wait(1.4)
        for num in final_sample:
            num["0"].set_color(TEAL_A)
        self.play(Blink(randy))
        self.wait(2)
        self.play(final_sample.animate.restore(), FadeOut(powers_of_2, shift = LEFT*0.5), Blink(morty))

        # Pick a subset
        subset_indices = [0, 1, 4, 6, 7, 9]
        subset = VGroup()
        complement = VGroup()
        for i in range(len(final_sample)):
            if i in subset_indices:
                subset.add(final_sample[i])
            else:
                complement.add(final_sample[i])
        self.play(
            randy.change("confused").scale(1.5).align_to(randy, DL),
            morty.change("conniving").scale(1/1.5).align_to(morty, DR),
            # AnimationGroup(*[num.animate.set_color(YELLOW) for num in subset]),
            AnimationGroup(*[num.animate.fade(0.8) for num in complement]),
        )

        # Add up the subset
        vinculum = Line(LEFT, RIGHT).set_color(
            WHITE
        ).set_stroke(
            width = 4
        ).match_width(
            subset
        ).scale(
            1.3
        ).next_to(
            final_sample, DOWN
        ).align_to(
            final_sample, RIGHT
        )
        plus = Tex("+", font_size = 40).next_to(final_sample[-1], LEFT).align_to(vinculum, LEFT)
        self.play(AnimationGroup(ShowCreation(vinculum), GrowFromCenter(plus), lag_ratio = 0.4))
        result = Tex(
            "".join(["1" if i in subset_indices else "0" for i in range(len(final_sample[0]))][::-1]),
            tex_to_color_map = {"1": RED, "0": TEAL_A}
        ).match_height(
            final_sample[0]
        ).next_to(
            vinculum, DOWN
        ).align_to(
            final_sample[-1], RIGHT
        )
        self.play(
            AnimationGroup(*[
                (
                    ReplacementTransform(final_sample[len(final_sample) - 1 - i][i].copy(), result[i])
                    if len(final_sample) - 1 - i in subset_indices
                    else FadeIn(result[i], shift = DOWN*0.2)
                )
                for i in range(len(result))
            ], lag_ratio = 0.1)
        , run_time = 2)
        self.play(Blink(morty))

        # Pick a second subset and add it up
        example1 = VGroup(final_sample, plus, vinculum, result)
        example2 = VGroup(final_sample.copy().set_opacity(1), plus.copy(), vinculum.copy())
        subset_indices_2 = [2, 3, 8]
        subset2 = VGroup()
        complement2 = VGroup()
        for i in range(len(example2[0])):
            if i in subset_indices_2:
                subset2.add(example2[0][i])
            else:
                complement2.add(example2[0][i])
        for num in complement2:
            num.fade(0.8) 
        result2 = Tex(
            "".join(["1" if i in subset_indices_2 else "0" for i in range(len(example2[0][0]))][::-1]),
            tex_to_color_map = {"1": RED, "0": TEAL_A}
        ).match_height(
            example2[0][0]
        ).next_to(
            vinculum, DOWN
        ).align_to(
            example2[0][-1], RIGHT
        )
        example2.add(result2)
        example1.generate_target()
        VGroup(example1.target, example2).arrange(buff = 0.5).align_to(example1, UP)
        self.play(
            randy.animate.look_at(example1.target[-1].get_center()),
            morty.animate.look_at(example1.target[-1].get_center()),
            MoveToTarget(example1)
        )
        self.play(
            randy.animate.look_at(result2.get_center()),
            morty.animate.look_at(result2.get_center()),
            TransformFromCopy(example1[:-1], example2[:-1])
        )
        self.play(
            AnimationGroup(*[
                (
                    ReplacementTransform(example2[0][len(example2[0]) - 1 - i][i].copy(), result2[i])
                    if len(example2[0]) - 1 - i in subset_indices_2
                    else FadeIn(result2[i], shift = DOWN*0.2)
                )
                for i in range(len(result2))
            ], lag_ratio = 0.1, run_time = 2)
        )
        self.play(randy.change("angry"), morty.change("hooray"))
        self.play(Blink(randy))
        self.wait(1)

        # Go back to viewing the powers of 2
        final_sample.generate_target()
        final_sample.target.become(powers_of_2_nums).arrange(DOWN, buff = 0.23).to_edge(UP, buff = 0.5)
        powers_of_2.generate_target()
        for i in range(len(powers_of_2.target)):
            powers_of_2.target[i].next_to(final_sample.target[i], LEFT, buff = 0.14)
            powers_of_2.target[i].shift(UP*(final_sample.target[i].get_y() - powers_of_2.target[i][-1].get_y()))
        expanded_powers_of_2 = VGroup(*[
            Tex(str(2**i) + "=").match_height(
                powers_of_2_nums[0]
            ).set_color(
                RED
            ).set_color_by_tex(
                "=", WHITE
            ).next_to(
                powers_of_2.target[i][0], LEFT, buff = 0.15
            )
            for i in range(len(powers_of_2))
        ])
        VGroup(expanded_powers_of_2, powers_of_2.target, final_sample.target).set_x(0)
        powers_of_2.move_to(powers_of_2.target).shift(LEFT*0.5).set_opacity(0)

        self.play(
            randy.change("erm"),
            morty.change("pondering"),
            AnimationGroup(
                FadeOut(example2, shift = RIGHT*0.5),
                FadeOut(example1[1:]),
                MoveToTarget(final_sample),
                MoveToTarget(powers_of_2),
                FadeIn(expanded_powers_of_2, shift = RIGHT*0.5)
            , run_time = 2)
        )
        self.play(Blink(morty))
        self.wait(2)

        # Show that there are only 7 powers of 2 between 1 and 100
        box1 = SurroundingRectangle(
            VGroup(expanded_powers_of_2[:7], powers_of_2[:7], final_sample[:7]),
            fill_opacity = 0,
            stroke_width = 2,
            stroke_color = PURE_GREEN
        ).round_corners(0.1)
        self.play(ShowCreation(box1), Blink(randy))

        # Show that 10 numbers are needed
        box2 = DashedVMobject(
            SurroundingRectangle(
                VGroup(expanded_powers_of_2, powers_of_2, final_sample),
                buff = 0.2,
                stroke_width = 4
            ).rotate(0.1*DEG),
            num_dashes = 50
        ).set_color(ORANGE)
        self.play(
            ShowCreation(box2),
            randy.change("conniving").scale(1/1.5).align_to(randy, DL),
            morty.change("confused", box2).scale(1.5).align_to(morty, DR)
        )
        self.wait(2)
        self.play(Blink(randy), morty.change("pondering", box2))
        self.play(Blink(morty))
        self.wait(2)

        # Pi creatures think for a bit more
        self.play(Blink(randy))
        self.play(
            randy.change("pondering").set_height(1.2).align_to(randy, DL),
            morty.change("confused").set_height(1.2).align_to(morty, DR)
        )
        self.play(Blink(morty))
        self.wait(2)
        self.play(Blink(randy))

class Solution(InteractiveScene):
    def construct(self):
        # Add pi creatures
        randy, morty = pis = VGroup(Randolph(), Mortimer())
        pis.arrange(RIGHT)

        self.play(LaggedStart(
            VFadeIn(randy),
            randy.change("tease", morty.eyes),
            VFadeIn(morty),
            morty.change("hesitant", randy.eyes),
            lag_ratio=0.5,
            run_time=1.5
        ))
        self.play(Blink(randy))

        # Add numbers
        number_grid = VGroup(Integer(n) for n in range(1, 101))
        number_grid.arrange_in_grid(10, 10, v_buff=0.3, h_buff=0.1)
        number_grid.set_width(5)
        number_grid.to_edge(UP)

        self.play(
            FadeIn(number_grid, lag_ratio=0.01, shift=0.05 * UP, run_time=2),
            randy.change("pondering", number_grid).set_height(1).next_to(number_grid, DOWN, 0.75, LEFT),
            morty.change("raise_right_hand").set_height(1).next_to(number_grid, DOWN, 0.75, RIGHT),
        )
        self.wait()

        # Choose a random subset
        sample_indices = [20, 33, 38, 49, 51, 53, 61, 62, 65, 97]
        sample_list = [number_grid[i] for i in sample_indices]
        sample_list.sort(key=lambda m: m.get_value())
        sample = VGroup(*sample_list)
        number_grid.remove(*sample)
        sample_rects = VGroup(
            SurroundingRectangle(num, buff=0.1)
            for num in sample
        )
        sample_rects.set_stroke(TEAL, 2)

        self.play(
            number_grid.animate.set_fill(opacity=0.25).set_anim_args(lag_ratio=0.005),
            sample.animate.set_fill(TEAL).set_anim_args(lag_ratio=0.2),
            Write(sample_rects),
            run_time=3
        )
        self.play(Blink(morty))
        self.wait()

        # Organize
        sample_groups = VGroup(
            VGroup(num, rect)
            for num, rect in zip(sample, sample_rects)
        )
        sample_groups.target = sample_groups.generate_target()
        sample_groups.target.arrange_in_grid(2, 5)
        sample_groups.target.set_width(number_grid.get_width())
        sample_groups.target.next_to(pis, UP, MED_LARGE_BUFF)

        self.play(
            MoveToTarget(sample_groups),
            FadeOut(number_grid),
            randy.change("hesitant", sample_groups),
            morty.change("tease", randy.eyes)
        )
        self.play(
            Blink(randy),
            FadeOut(sample_rects),
        )
        self.wait()

        # Write the number of subsets and flash through some of them
        number_of_subsets = TexText("$2^{10}$ total subsets", font_size = 50).next_to(sample_groups, UP, buff = 1)
        for i in range(12):
            anim = AnimationGroup(*[
                num.animate.set_opacity(1 if random.random() > 0.5 else 0.1)
                for num in sample
            ], run_time = 1)
            if i == 0:
                self.play(Write(number_of_subsets, run_time = 1), Blink(randy), anim)
            else:
                self.play(anim)
        self.play(Blink(morty))

        # Organize the numbers into a row and calculate the number of subsets
        self.play(
            randy.change("raise_right_hand", number_of_subsets),
            morty.change("pondering", number_of_subsets),
            sample.animate.set_opacity(1).arrange().scale(0.7).set_y(0.5)
        )
        calculation = Tex(
            R"2 \times 2 \times 2 \times 2 \times 2 \times 2 \times 2 \times 2 \times 2 \times 2",
            font_size = 27.8
        ).next_to(sample, UP)
        self.play(Write(calculation), Blink(randy))
        brace = Brace(calculation, UP)
        self.play(GrowFromEdge(brace, DOWN))
        number_of_subsets_1024 = TexText(
            "$1024$ total subsets", font_size = 50, tex_to_color_map = {"$1024$": YELLOW}
        ).move_to(number_of_subsets)
        self.play(
            ReplacementTransform(number_of_subsets["$2^{10}$"], number_of_subsets_1024["$1024$"]),
            ReplacementTransform(number_of_subsets["total subsets"], number_of_subsets_1024["total subsets"])
        )
        self.play(FadeOut(VGroup(brace, calculation)), Blink(morty))
        self.wait(2)
        self.play(Blink(randy), sample.animate.shift(DOWN*0.7))

        # Show that all the numbers are at most 100
        box = SurroundingRectangle(sample, fill_opacity = 0, stroke_width = 3, stroke_color = GREEN).round_corners(0.05)
        self.play(ShowCreation(box))
        at_most_100 = Tex(R"\text{all}\leq {100}", font_size = 30).next_to(box, UP)
        self.play(Write(at_most_100))
        self.wait(0.5)

        # Show that there are at most 10 numbers per subset
        at_most_10_numbers = Tex(R"\leq {10} \text{ numbers per subset}", font_size = 30)
        at_most_100.generate_target()
        VGroup(at_most_100.target, at_most_10_numbers).arrange(buff = 0.4).match_y(at_most_100)
        self.play(
            AnimationGroup(
                MoveToTarget(at_most_100),
                Write(at_most_10_numbers)
            , lag_ratio = 0.5)
        )

        # Show that there are at most 1000 possible sums
        number_of_sums_bound = TexText(
            R"$\leq {100} \cdot {10} = {1000}$ total sums", font_size = 40, tex_to_color_map = {"{1000}": GOLD}
        ).next_to(number_of_subsets_1024, DOWN)
        self.play(
            AnimationGroup(
                Write(number_of_sums_bound[R"\leq"]),
                TransformFromCopy(at_most_100["{100}"], number_of_sums_bound["{100}"]),
                GrowFromCenter(number_of_sums_bound[R"\cdot"]),
                TransformFromCopy(at_most_100["{10}"], number_of_sums_bound["{10}"]),
                Write(number_of_sums_bound["= {1000}$ total sums"], run_time = 1.5)
            , lag_ratio = 0.3)
        )
        number_of_sums_bound_trimmed = VGroup(number_of_sums_bound[R"\leq"], number_of_sums_bound["{1000}$ total sums"])
        number_of_sums_bound_trimmed.generate_target()
        number_of_sums_bound_trimmed.target.arrange(center = False)
        number_of_sums_bound_trimmed.target.scale(
            number_of_subsets_1024["1"].get_height()/number_of_sums_bound_trimmed.target[1][0][0].get_height()
        )
        number_of_sums_bound_trimmed.target.shift(
            RIGHT*(number_of_subsets_1024["4"].get_right()[0] - number_of_sums_bound_trimmed.target[1][0][3].get_right()[0]) + LEFT*0.01
        )
        self.play(Blink(randy))
        self.play(
            randy.change("happy", number_of_sums_bound_trimmed.target),
            morty.change("confused"),
            FadeOut(VGroup(at_most_100, at_most_10_numbers, box, number_of_sums_bound[R"{100} \cdot {10} ="])),
            MoveToTarget(number_of_sums_bound_trimmed),
            sample.animate.shift(UP*0.5)
        )
        self.play(Blink(morty))

        # Show all the subsets
        bounds = VGroup(number_of_subsets_1024, number_of_sums_bound_trimmed)
        bounds_rect = Rectangle(
            width = FRAME_WIDTH*1.5,
            height = bounds.get_height()*1.2,
            fill_opacity = 1,
            fill_color = BLACK,
            stroke_width = 0
        ).move_to(bounds)
        self.add(bounds_rect, Point(), bounds)
        self.play(FadeIn(bounds_rect))
        # bounds_rect.fix_in_frame()
        self.bring_to_front(bounds_rect, bounds)

        all_subsets = VGroup()
        for i in range(2**10):
            subset = (
                VGroup(*[sample[len(sample) - 1 - j].copy() for j in range(10) if (i//2**j) % 2 == 1]).arrange(buff = 0.1)
                if i > 0 else Tex(r"\varnothing").set_color(BLUE)
            )
            rect = SurroundingRectangle(subset, fill_opacity = 0, stroke_width = 1, stroke_color = GREY_B)
            total = VGroup(Tex(R"\rightarrow"), Integer(sum([num.get_value() for num in subset]) if i > 0 else 0)).arrange(buff = 0.1).match_height(subset).set_color(GOLD).next_to(rect, RIGHT, buff = 0.1)
            all_subsets.add(VGroup(subset, rect, total) if i > 0 else VGroup(subset, total))
        all_subsets = VGroup(*sorted(all_subsets, key = lambda s: s.get_width()))
        n_cols = 16
        all_subsets.arrange_in_grid(n_cols = n_cols, h_buff = 0, buff = 0, fill_rows_first = False)
        columns = VGroup()
        for col in range(n_cols):
            columns.add(all_subsets[col*len(all_subsets)//n_cols:(col + 1)*len(all_subsets)//n_cols])
        columns.arrange(
            buff = 0.2
        ).set_height(
            (FRAME_HEIGHT - bounds_rect.get_height())*0.99
        ).to_edge(
            UP, buff = bounds_rect.get_height()
        )
        self.play(
            FadeOut(VGroup(randy, morty), shift = DOWN),
            ReplacementTransform(sample, all_subsets),
            VGroup(bounds_rect, bounds).animate.to_edge(UP, buff = 0)
        , run_time = 1.5)
        VGroup(bounds_rect, bounds).fix_in_frame()
        self.add(VGroup(bounds_rect, bounds))

        # for i in range(len(all_subsets)):
        #     if all_subsets[i][-1][1].get_value() == 314:
        #         print(i)
        index1 = 498
        index2 = 784
        self.play(self.camera.frame.animate.move_to(all_subsets[index1]).scale(0.2), run_time = 2)
        rect = SurroundingRectangle(all_subsets[index1], fill_opacity = 0, stroke_width = 3, stroke_color = PURE_GREEN, buff = 0.01)
        self.play(bounds.animate.to_edge(LEFT, buff = 0.4), ShowCreation(rect))
        self.play(self.camera.frame.animate.move_to(all_subsets[index2]), run_time = 4)
        rect = SurroundingRectangle(all_subsets[index2], fill_opacity = 0, stroke_width = 3, stroke_color = PURE_GREEN, buff = 0.01)
        self.play(ShowCreation(rect))
        self.wait(3)


class WritePigeonholePrinciple(Scene):
    def construct(self):
        self.play(Write(TexText("Pigeonhole Principle", font_size = 70)))

class EightElementSets(InteractiveScene):
    def construct(self):
        # Show examples of eight element sets from 1 to 100 with distinct subset sums
        eight_element_examples_numbers = [
            [40, 60, 71, 77, 80, 82, 83, 84],
            [42, 62, 73, 79, 82, 84, 85, 86],
            [44, 64, 75, 81, 84, 86, 87, 88],
            [50, 70, 81, 87, 90, 92, 93, 94],
            [54, 76, 87, 93, 96, 98, 99, 100]
        ]

        eight_element_examples = VGroup()
        for numbers in eight_element_examples_numbers:
            tex_string = R"\{"
            for i in range(len(numbers)):
                tex_string += str(numbers[i])
                if i < len(numbers) - 1:
                    tex_string += ", "
            tex_string += R"\}"
            example = Tex(
                tex_string, font_size = 60
            ).set_color(
                BLUE
            ).set_color_by_tex_to_color_map(
                {R"\{": WHITE, ",": WHITE, R"\}": WHITE}
            )
            eight_element_examples.add(example)
        eight_element_examples.arrange(DOWN, buff = 0.5)
        self.play(
            AnimationGroup(*[
                FadeIn(example, shift = DOWN*0.2)
                for example in eight_element_examples
            ], lag_ratio = 1.2)
        )
        self.wait(3)

        # Randy looks at the numbers and is puzzled by their apparent patternlessness
        randy = Randolph("confused", color = GREY_BROWN).to_edge(LEFT, buff = 1)
        self.play(eight_element_examples.animate.to_edge(RIGHT, buff = 1), FadeIn(randy, shift = RIGHT*0.5))
        self.play(randy.animate.look_at(eight_element_examples[0]))
        self.wait(1)
        self.play(randy.animate.look_at(eight_element_examples[4]))
        self.play(Blink(randy))
        self.play(randy.animate.look_at(eight_element_examples[0]))
        self.wait(1)

        # Focus on one of the examples
        main_example = eight_element_examples[4]
        main_example.generate_target()
        main_example.target.set_y(0)
        self.play(
            AnimationGroup(
                *[FadeOut(example, shift = UP*0.5) for example in eight_element_examples[:4]],
                MoveToTarget(main_example, run_time = 2),
                randy.animate.look_at(main_example.target)
            , lag_ratio = 0.1),
        )
        self.play(Blink(randy))
        self.wait(2)

        # Attempt to find a pattern in the numbers
        main_example_numbers = eight_element_examples_numbers[-1]
        arrows = VGroup(*[
            CurvedArrow(
                main_example[str(main_example_numbers[i])].get_top() + UP*0.2,
                main_example[str(main_example_numbers[i - 1])].get_top() + UP*0.2
            ).set_color(YELLOW)
            for i in range(len(main_example_numbers) - 1, 2, -1)
        ])
        difference_numbers = [1, 1, 2, 3, 6]
        differences = VGroup(*[
            Tex(RF"-{str(difference_numbers[i])}").set_color(GREEN if i < len(difference_numbers) - 1 else RED).next_to(arrows[i], UP)
            for i in range(len(difference_numbers))
        ])
        self.play(randy.change("pondering", main_example), Indicate(main_example["100"]))
        for i in range(4):
            self.play(
                AnimationGroup(
                    GrowArrow(arrows[i]),
                    Write(differences[i]),
                    Indicate(main_example[str(main_example_numbers[::-1][i + 1])])
                , lag_ratio = 0.4)
            )
            self.wait(1)
        self.play(Blink(randy))
        self.wait(2)
        fibonacciText = TexText("Fibonacci?").next_to(main_example, UP, buff = 2)
        self.play(Write(fibonacciText))
        self.wait(2)
        self.play(GrowArrow(arrows[4]), Write(differences[4]))
        questionMarks = VGroup(*[
            TexText("?", font_size = 80).set_color(PINK).next_to(main_example[str(main_example_numbers[i])], UP, buff = 0.3)
            for i in [1, 0]
        ])
        self.play(Blink(randy))
        self.play(AnimationGroup(*[FadeIn(qm, shift = UP*0.4) for qm in questionMarks], lag_ratio = 0.2))
        self.wait(2)

        # Bring the numbers back to the center of the screen
        self.play(
            FadeOut(randy, shift = LEFT),
            FadeOut(questionMarks),
            FadeOut(arrows),
            FadeOut(differences),
            FadeOut(fibonacciText),
            main_example.animate(run_time = 2).scale(1.3).center()
        )
        self.wait(2)

        # Tease a 9-element example
        nine_element_example = Tex(
            R"\{a_1, a_2, a_3, a_4, a_5, a_6, a_7, a_8, a_9\}", font_size = 60
        ).set_color(
            BLUE
        ).set_color_by_tex_to_color_map(
            {R"\{": WHITE, ",": WHITE, R"\}": WHITE}
        ).match_height(
            main_example
        ).move_to(
            main_example
        )
        self.play(ReplacementTransform(main_example, nine_element_example))
        nobodyKnows = TexText("Nobody knows...", font_size = 70).set_color(YELLOW).shift(UP*2)
        self.play(FadeIn(nobodyKnows))

from itertools import chain, combinations

def powerset(iterable):
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
class EightElementSetsV2(InteractiveScene):
    def construct(self):
        # Create a list of eight-element dss sets from 1 to 100
        eight_element_examples_numbers = [
            [40, 60, 71, 77, 80, 82, 83, 84],
            [42, 62, 73, 79, 82, 84, 85, 86],
            [44, 64, 75, 81, 84, 86, 87, 88],
            [50, 70, 81, 87, 90, 92, 93, 94],
            [54, 76, 87, 93, 96, 98, 99, 100]
        ]

        eight_element_examples = VGroup()
        for numbers in eight_element_examples_numbers:
            tex_string = R"\{"
            for i in range(len(numbers)):
                tex_string += str(numbers[i])
                if i < len(numbers) - 1:
                    tex_string += ", "
            tex_string += R"\}"
            example = Tex(
                tex_string, font_size = 60
            ).set_color(
                BLUE
            ).set_color_by_tex_to_color_map(
                {R"\{": WHITE, ",": WHITE, R"\}": WHITE}
            )
            eight_element_examples.add(example)
        eight_element_examples.arrange(DOWN, buff = 0.5)
        winkler_example = eight_element_examples[-1]
        winkler_example.save_state()
        winkler_example.scale(1.1).center()
        self.add(winkler_example)

        # Show the different subsets flashing by
        num_iterations = 10
        for iteration in range(num_iterations):
            subset_indices = sorted(random.sample(list(range(8)), random.randint(2, 6)))
            circles = VGroup(*[
                Circle(
                    radius = 0.5, fill_opacity = 0, stroke_width = 3, stroke_color = YELLOW
                ).move_to(
                    winkler_example[str(eight_element_examples_numbers[-1][i])]
                )
                for i in subset_indices
            ])
            self.add(circles)
            sum_equation_string = ""
            for i in subset_indices:
                sum_equation_string += str(eight_element_examples_numbers[-1][i])
                if i != subset_indices[-1]:
                    sum_equation_string += "+"
                else:
                    sum_equation_string += "=" + str(sum([eight_element_examples_numbers[-1][j] for j in subset_indices]))
            sum_equation = Tex(sum_equation_string, font_size = 50).shift(UP*2)
            for i in subset_indices:
                sum_equation[str(eight_element_examples_numbers[-1][i])].set_color(BLUE)
            sum_equation[str(sum([eight_element_examples_numbers[-1][j] for j in subset_indices]))].set_color(YELLOW)
            self.add(sum_equation)
            self.wait(0.5)
            if iteration < num_iterations - 1:
                self.remove(circles, sum_equation)
            else:
                self.wait(1)
                self.play(FadeOut(VGroup(circles, sum_equation)))

        # Show the other examples
        self.play(
            winkler_example.animate(run_time = 2).restore(),
            AnimationGroup(*[
                FadeIn(example, shift = DOWN*0.2)
                for example in eight_element_examples[:-1]
            ], lag_ratio = 0.4)
        )
        self.wait(3)

        # Randy looks at the numbers and is puzzled by their apparent patternlessness
        randy = Randolph("confused", color = GREY_BROWN).to_edge(LEFT, buff = 1)
        randy.look_at(self.camera.frame.get_right())
        self.play(
             AnimationGroup(
                *[FadeOut(example, shift = UP*0.5) for example in eight_element_examples[:4]],
                winkler_example.animate(run_time = 1.5).set_y(0).to_edge(RIGHT, buff = 1),
                FadeIn(randy, shift = RIGHT*0.5)
            , lag_ratio = 0.1),
        )
        self.wait(1)
        self.play(Blink(randy))
        self.wait(2)
        self.play(randy.change("pondering", winkler_example))
        self.wait(2)
        self.play(Blink(randy))

        # Show the method of construction (greedy strategy from the top down)
        sums_so_far = TexText("Sums so far:").match_x(winkler_example).to_edge(UP, buff = 0.8)
        self.add(sums_so_far)
        winkler_example.save_state()
        max_iters = 6
        for i in range(max_iters):
            for j in range(len(eight_element_examples_numbers[-1])):
                num = eight_element_examples_numbers[-1][7 - j]
                if j <= i:
                    winkler_example[str(num)].set_opacity(1).set_color(YELLOW)
                else:
                    winkler_example[str(num)].set_opacity(0.3)
            sums_string = ""
            all_subsets = powerset(eight_element_examples_numbers[-1][8 - i:])
            for k in range(len(all_subsets)):
                sums_string += str(sum(all_subsets[k]))
                if k < len(all_subsets) - 1:
                    sums_string += ", "
                if (k + 1) % 8 == 0:
                    sums_string += R"\\"
            sums = TexText(R"\begin{center}" + sums_string + R"\end{center}", font_size = 40).next_to(sums_so_far, DOWN)
            self.add(sums_so_far)
            self.add(sums)
            if i < max_iters - 1:
                self.wait(1)
                self.remove(sums)
            else:
                self.wait(3)
                self.remove(sums, sums_so_far)
                winkler_example.restore()

class BruteForce9Elements(InteractiveScene):
    def construct(self):
        # Add pi creatures
        randy, morty = pis = VGroup(Randolph(), Mortimer())
        pis.arrange(RIGHT)

        self.play(LaggedStart(
            VFadeIn(randy),
            randy.change("tease", morty.eyes),
            VFadeIn(morty),
            morty.change("hesitant", randy.eyes),
            lag_ratio=0.5,
            run_time=1.5
        ))
        self.play(Blink(randy))

        # Add numbers
        number_grid = VGroup(Integer(n) for n in range(1, 101))
        number_grid.arrange_in_grid(10, 10, v_buff=0.3, h_buff=0.1)
        number_grid.set_width(5)
        number_grid.to_edge(UP)

        self.play(
            FadeIn(number_grid, lag_ratio=0.01, shift=0.05 * UP, run_time=2),
            randy.change("pondering", number_grid).set_height(1).next_to(number_grid, DOWN, 1.25, LEFT),
            morty.change("raise_right_hand").set_height(1.5).next_to(number_grid, DOWN, 0.75, RIGHT),
        )
        self.wait()

        # Choose a bunch of random 9-element subsets
        for _ in range(50):
            sample_list = random.sample(list(number_grid), 9)
            sample_list.sort(key=lambda m: m.get_value())
            sample = VGroup(*sample_list)
            number_grid.remove(*sample)
            sample_rects = VGroup(
                SurroundingRectangle(num, buff=0.1)
                for num in sample
            )
            sample_rects.set_stroke(TEAL, 2)

            number_grid.save_state()
            number_grid.set_fill(opacity=0.25)
            sample.set_fill(TEAL)
            self.add(sample_rects, sample, number_grid)
            self.wait(0.25)
            self.remove(sample_rects)
            sample.set_color(WHITE)
            number_grid.restore()
            number_grid.add(*sample)

class NineElementSetsCombinationsCalculation(InteractiveScene):
    def construct(self):
        # Calculate the total number of 9-element subsets from 100 numbers
        number_of_sets = Tex(
            R"\text{Number of sets} = {100 \choose 9} = 1,902,231,808,400", font_size = 45
        ).set_color(BLUE)
        first_part = number_of_sets[:19]
        first_part.save_state()
        first_part.center()
        self.play(Write(first_part), run_time = 2)
        self.play(
            AnimationGroup(
                first_part.animate.restore(),
                FadeIn(number_of_sets[19:])
            , lag_ratio = 0.6)
        , run_time = 1.75)
        self.wait(1)

        # Write the total number of subsets from those 9 numbers
        self.play(number_of_sets.animate.shift(UP*0.75))
        number_of_subsets = Tex(
            R"\text{Subsets per set} = 2^9 = 512", font_size = 45
        ).set_color(RED).shift(DOWN*0.75)
        number_of_subsets.shift(LEFT*(number_of_subsets["="][0].get_x() - number_of_sets["="][0].get_x()))
        self.play(Write(number_of_subsets), run_time = 2)

        # Write the total number of combinations (973942685900800)
        self.play(VGroup(number_of_sets, number_of_subsets).animate.shift(UP*0.75))
        total_combinations = Tex(
            R"\text{Subsets to check} = 512 \times 1,902,231,808,400 \approx 973 \text{ trillion}", font_size = 45,
            tex_to_color_map = {"Subsets to check": YELLOW, "512": RED, "1,902,231,808,400": BLUE, R"973 \text{ trillion}": YELLOW}
        ).shift(DOWN*1.5)
        # total_combinations.shift(LEFT*(total_combinations["="][0].get_x() - number_of_sets["="][0].get_x()))
        self.play(FadeIn(total_combinations), run_time = 1.5)

class ErdosQuestion(InteractiveScene):
    def construct(self):
        # Create a standin n-element set S with distinct subset sums
        s = Tex(
            R"S = \{a_1, a_2, ..., a_n\}", font_size = 80
        ).set_color_by_tex_to_color_map(
            {"S": TEAL}
        )
        self.play(Write(s), run_time = 2)
        # self.play(s.animate.shift(UP*0.75))
        # distinct_subset_sums_condition = Tex(
        #     R"\forall A, B \subseteq S (A \neq B \implies \sum A \neq \sum B)",
        #     tex_to_color_map = {"A": YELLOW, "B": YELLOW, "S": TEAL}
        # ).shift(DOWN*0.75)
        # self.play(FadeIn(distinct_subset_sums_condition))
        distinct_subset_sums = TexText(
            "(DSS)", font_size = 40
        ).set_color(GREY_B).next_to(s[R"\{a_1, a_2, ..., a_n\}"], UP)
        self.play(FadeIn(distinct_subset_sums))
        self.play(VGroup(s, distinct_subset_sums).animate.shift(UP*0.75))

        # Write the lower bound question
        lower_bound = Tex(
            R"\max(S) \ge f(n)?", font_size = 60, tex_to_color_map = {"S": TEAL}
        ).shift(DOWN*0.75)
        self.play(Write(lower_bound), run_time = 2)
        self.wait(1)
        lower_bound_c = Tex(
            R"\max(S) \ge c \cdot 2^n?", tex_to_color_map = {"S": TEAL, "c": RED}
        ).match_height(lower_bound).move_to(lower_bound)
        self.play(ReplacementTransform(lower_bound, lower_bound_c))
        self.wait(3)

        # Suppose that c = 0.2
        c_equals_0_point_2 = Tex("c = 0.2").set_color(RED).next_to(lower_bound_c["c"], DOWN)
        self.play(Write(c_equals_0_point_2))

        # Transform the ns into 9s
        s_n = s["n"]
        s_n.save_state()
        lower_bound_c.save_state()
        nine1 = Tex(
            "_9", font_size = 80
        ).set_color(
            YELLOW
        ).move_to(
            s["n"]
        ).match_y(
            s["1"]
        )
        nine2 = Tex(
            "^9", font_size = 60
        ).set_color(
            YELLOW
        ).move_to(
            lower_bound_c["n"]
        ).align_to(
            lower_bound_c["n"], DOWN
        )
        self.play(
            ReplacementTransform(s["n"], nine1),
            ReplacementTransform(lower_bound_c["n"], nine2),
            ShrinkToCenter(lower_bound_c["?"])
        )
        self.wait(1)

        # Highlight the original set
        rect = SurroundingRectangle(s, color = GREEN, buff = 0.15).round_corners(0.1)
        self.play(FadeIn(rect))
        self.wait(2)
        self.play(
            rect.animate.become(
                SurroundingRectangle(
                    lower_bound_c[:-1], color = GREEN, buff = 0.15
                ).round_corners(0.1)
            )
        , run_time = 1.5)
        self.wait(2)
        self.play(FadeOut(rect))

        # Substitute in c = 0.2
        lower_bound_substituted = Tex(
            R"\max(S) \ge 0.2 \cdot 2^9 = 102.4", tex_to_color_map = {"S": TEAL, "0.2": RED, "n": YELLOW, "9": YELLOW, "102.4": ORANGE}
        ).match_height(VGroup(lower_bound_c, nine2)).move_to(lower_bound)
        self.play(
            FadeOut(c_equals_0_point_2["c ="]),
            ShrinkToCenter(lower_bound_c["c"]),
            TransformMatchingShapes(lower_bound_c[R"\max(S) \ge"], lower_bound_substituted[R"\max(S) \ge"], run_time = 1),
            ReplacementTransform(lower_bound_c[R"\cdot 2"], lower_bound_substituted[R"\cdot 2"]),
            nine2.animate.match_width(lower_bound_substituted["9"]).move_to(lower_bound_substituted["9"]),
            ReplacementTransform(c_equals_0_point_2["0.2"], lower_bound_substituted["0.2"], path_arc = -PI*0.2)
        )
        self.wait(0.5)
        self.play(FadeIn(lower_bound_substituted["= 102.4"]))
        self.remove(nine2)
        self.add(lower_bound_substituted)

        # Put everything back in terms of n
        self.play(
            ReplacementTransform(nine1, s_n.restore()),
            FadeOut(lower_bound_substituted),
            FadeIn(lower_bound_c.restore())
        , run_time = 2)
        self.wait(2)

        # Write what we know
        self.play(VGroup(s, distinct_subset_sums, lower_bound_c).animate.shift(UP*0.75))
        what_we_know = Tex(
            R"\text{What we know: } c \leq 0.22002",
            tex_to_color_map = {"c": RED, "0.22002": RED},
            font_size = 60
        ).shift(DOWN*1.5)
        self.play(Write(what_we_know["What we know:"]), run_time = 2)
        bohman_credit = TexText("(Tom Bohman, 1998)", font_size = 30).set_color(GREY_B).next_to(what_we_know["What we know:"], DOWN)
        self.play(FadeIn(bohman_credit), run_time = 2)
        self.wait(1)
        self.play(Write(what_we_know[R"c \leq 0.22002"]), run_time = 2.5)
        self.wait(2)
        self.wait(0.5)

        # Show what happens when you plug in n = 9
        plugged_in_n_and_c = Tex(
            R"0.22002 \cdot 2^9 \approx 112.65",
            tex_to_color_map = {"0.22002": RED, "9": YELLOW},
            font_size = 60
        ).next_to(lower_bound_c, DOWN)
        plugged_in_n_and_c.shift(RIGHT*(lower_bound_c[R"\cdot"].get_x() - plugged_in_n_and_c[R"\cdot"].get_x()))
        self.play(
            AnimationGroup(
                AnimationGroup(
                    VGroup(what_we_know, bohman_credit).animate.scale(0.7).to_edge(DOWN, buff = 0.5),
                    TransformFromCopy(what_we_know["0.22002"], plugged_in_n_and_c["0.22002"])
                ),
                FadeIn(plugged_in_n_and_c[R"\cdot 2^9 \approx 112.65"])
            , lag_ratio = 0.6)
        , run_time = 2)
        self.wait(2)

        # Show that 0.22002 is the best bound we have so far
        rect = SurroundingRectangle(VGroup(what_we_know, bohman_credit), color = GREEN_D, buff = 0.15).round_corners(0.1)
        self.play(ShowCreation(rect))
        self.wait(3)

        # Show that the bound would decrease to about 0.195 if there was an example for n = 9
        plugged_in_100 = Tex(
            R"0.1953125 \cdot 2^{9} = 100",
            tex_to_color_map = {"0.1953125": RED, "{9}": YELLOW},
            font_size = 60
        ).move_to(plugged_in_n_and_c)
        plugged_in_100.shift(RIGHT*(plugged_in_n_and_c[R"\cdot"].get_x() - plugged_in_100[R"\cdot"].get_x()))
        self.play(
            FadeOut(rect),
            ReplacementTransform(plugged_in_n_and_c["0.22002"], plugged_in_100["0.1953125"]),
            ReplacementTransform(plugged_in_n_and_c[R"\cdot"], plugged_in_100[R"\cdot"]),
            ReplacementTransform(plugged_in_n_and_c["2^9"], plugged_in_100["2^{9}"]),
            ReplacementTransform(plugged_in_n_and_c[R"\approx"], plugged_in_100["="]),
            ReplacementTransform(plugged_in_n_and_c["112.65"], plugged_in_100["100"])
        , run_time = 1)
        rect = SurroundingRectangle(plugged_in_100["0.1953125"], color = GREEN_D, buff = 0.15).round_corners(0.1)
        self.play(ShowCreation(rect))
        self.wait(3)

class PigeonHoleWith8(InteractiveScene):
    def construct(self):
        # Write the total number of subsets and sums
        n_equals_8 = Tex(
            "n = 8",
            font_size = 60,
            tex_to_color_map = {"n": YELLOW, "8": YELLOW}
        ).to_edge(UP, buff = 2)
        self.add(n_equals_8)
        total_subsets = Tex(
            R"\text{Total subsets}= 2^8 = 256",
            font_size = 45,
            tex_to_color_map = {"8": YELLOW, "256": BLUE}
        ).shift(UP)
        self.play(Write(total_subsets), run_time = 1.5)
        self.wait(0.5)
        total_sums = Tex(
            R"\text{Total sums}\leq 100 + 99 + 98 + 97 + 96 + 95 + 94 + 93 = 772 \ge 256",
            font_size = 45,
            tex_to_color_map = {"772": GREEN, "256": BLUE}
        ).next_to(total_subsets, DOWN, buff = 0.5)
        self.play(FadeIn(total_sums), run_time = 2)

class PigeonHoleWith9(InteractiveScene):
    def construct(self):
        # Write the total number of subsets and sums
        n_equals_9 = Tex(
            "n = 9",
            font_size = 60,
            tex_to_color_map = {"n": YELLOW, "9": YELLOW}
        ).to_edge(UP, buff = 2)
        self.add(n_equals_9)
        total_subsets = Tex(
            R"\text{Total subsets}= 2^9 = 512",
            font_size = 45,
            tex_to_color_map = {"9": YELLOW, "512": BLUE}
        ).shift(UP)
        self.play(Write(total_subsets), run_time = 1.5)
        self.wait(0.5)
        total_sums = Tex(
            R"\text{Total sums}\leq 100 + 99 + 98 + 97 + 96 + 95 + 94 + 93 + 92 = 864 \ge 512",
            font_size = 45,
            tex_to_color_map = {"864": GREEN, "512": BLUE}
        ).next_to(total_subsets, DOWN, buff = 0.5)
        self.play(FadeIn(total_sums), run_time = 2)

class ConnectionsToBroaderMath(InteractiveScene):
    def construct(self):
        # Add the Pi Creature
        randy = Randolph("happy").look_at(self.camera.frame.get_right()).set_width(4).to_edge(LEFT, buff = 1.5)
        self.add(randy)
        self.wait(1)
        self.play(Blink(randy))

        # Randy looks at the pigeons
        self.play(randy.animate.look_at(self.camera.frame.get_corner(UR) + DOWN*2))
        self.wait(2)

        # Randy looks at the Erdos question
        self.play(randy.animate.look_at(self.camera.frame.get_corner(DR)))
        self.wait(1)
        self.play(Blink(randy))
        self.wait(3)

        # Randy is confused at the Erdoes question
        self.play(randy.change("confused"))

class WriteDistinctSubsetSumProperty(InteractiveScene):
    def construct(self):
        # Write "distinct subset sum property"
        dss_unabbreviated = TexText("Distinct Subset Sum Property", font_size = 80)
        self.play(Write(dss_unabbreviated))
        dss = TexText("DSS Set", font_size = 160)
        part1 = dss[:3]
        part1.save_state()
        part1.center()
        self.play(
            dss_unabbreviated.animate.shift(DOWN*1.8).scale(0.8),
            TransformMatchingShapes(dss_unabbreviated.copy(), dss[:3])
        , run_time = 1)
        self.wait(2.5)
        self.play(AnimationGroup(part1.animate(run_time = 1).restore(), FadeIn(dss[3:], run_time = 2), lag_ratio = 0.3))

        # Show arrows to the sets and write "DSS Sets"
        # arrows = VGroup(*[
        #     Arrow(dss.get_left() + LEFT*0.6, dss.get_left() + LEFT*5 + DOWN*1.85*(i - 2), buff = 0, thickness = 7).set_color(YELLOW)
        #     for i in range(5)
        # ])
        # self.play(AnimationGroup(*[GrowArrow(arrow) for arrow in arrows], lag_ratio = 0.2))
        # self.wait(0.5)
        # self.play(FadeIn(dss[3:]), run_time = 2)

class PowersOf2Strategy(InteractiveScene):
    def construct(self):
        # Add morty above
        morty = Mortimer("tease").set_width(3)
        self.add(morty)
        self.wait(0.5)
        self.play(morty.animate.set_width(2).to_edge(UP))

        # Add the powers of 2
        tex_string = ""
        n = 13
        for i in range(n):
            tex_string += str(2**i)
            if i < n - 1:
                tex_string += R",\ "
        powers_of_2 = Tex(tex_string, font_size = 47).set_color(BLUE).set_color_by_tex(",", WHITE)
        self.play(FadeIn(powers_of_2, shift = UP*0.5), morty.animate.look_at(powers_of_2.get_left()))

        # Morty ponders the powers of 2
        self.play(morty.change("pondering"))
        self.wait(2)
        self.play(Blink(morty))
        self.play(morty.change("happy", powers_of_2.get_left() + RIGHT*2))
        self.wait(2)

        # # Box the first n powers of 2
        # box = SurroundingRectangle(powers_of_2[:-10], stroke_width = 6, buff = 0.08, stroke_color = YELLOW)
        # self.play(ShowCreation(box), run_time = 2)
        # n_equals_11 = Tex(R"n = 11\\\text{DSS Set}")
        # n_equals_11["DSS Set"].match_x(n_equals_11["n = 11"])
        # n_equals_11.set_color(YELLOW).next_to(box, DOWN)
        # self.play(FadeIn(n_equals_11))

        # # Show that 1024 = 2^(11 - 1)
        # two_to_the_n_minus_1 = Tex(
        #     "1024 = 2^{n - 1}"
        # ).set_color_by_tex_to_color_map(
        #     {"1024": BLUE, "n": YELLOW}
        # ).match_x(
        #     powers_of_2["1024"]
        # ).match_y(
        #     n_equals_11
        # )
        # self.play(TransformFromCopy(powers_of_2["1024"], two_to_the_n_minus_1["1024"], path_arc = PI*0.2), run_time = 1.5)
        # self.play(Write(two_to_the_n_minus_1["= 2^{n - 1}"]), run_time = 1.5)
        # self.wait(3)

        # Highlight the n = 8 set
        # self.remove(box, n_equals_11, two_to_the_n_minus_1)
        box = SurroundingRectangle(powers_of_2[:-23], stroke_width = 6, buff = 0.09, stroke_color = YELLOW)
        self.play(ShowCreation(box), run_time = 2)
        n_equals_8 = Tex(R"n = 8\\\text{DSS Set}")
        n_equals_8["DSS Set"].match_x(n_equals_8["n = 8"])
        n_equals_8.set_color(YELLOW).next_to(box, DOWN)
        self.play(FadeIn(n_equals_8), morty.change("lower_right_hand", powers_of_2.get_left()))

        # Show that 128 = 2^(8 - 1)
        two_to_the_n_minus_1 = Tex(
            R"128 = 2^{n - 1} = \frac{1}{2}2^n"
        ).set_color_by_tex_to_color_map(
            {"128": BLUE, "n": YELLOW}
        ).match_y(
            n_equals_8
        ).shift(RIGHT*2)
        self.play(TransformFromCopy(powers_of_2["128"], two_to_the_n_minus_1["128"], path_arc = PI*0.2), run_time = 1.5)
        self.play(Write(two_to_the_n_minus_1["= 2^{n - 1}"]), run_time = 1.5)
        self.wait(3)

        # Show that it's half of 2^n
        self.play(Write(two_to_the_n_minus_1[R"= \frac{1}{2}2^n"]), run_time = 2)
        self.wait(1.5)

        # Show that c must therefore be at most 0.5
        c_upper_bound = Tex(R"\Longrightarrow c \leq 0.5").set_color_by_tex("c", RED).next_to(two_to_the_n_minus_1, DOWN, buff = 0.4)
        c_upper_bound.shift(RIGHT*(two_to_the_n_minus_1["="][1].get_x() - c_upper_bound[R"\leq"].get_x()))
        self.play(Write(c_upper_bound), run_time = 2)

class CUpperBound100(InteractiveScene):
    def construct(self):
        # Show that c must be less than 100/2^8
        c_upper_bound = Tex(
            R"c \leq \frac{100}{2^8} = 0.390625", font_size = 80, tex_to_color_map = {"c": RED, "100": BLUE, "8": YELLOW}
        )
        self.play(Write(c_upper_bound[R"c \leq \frac{100}{2^8}"]), run_time = 2.5)
        self.wait(1)
        self.play(FadeIn(c_upper_bound["= 0.390625"], run_time = 2))

class CUpperBound9From1To100(InteractiveScene):
    def construct(self):
        # Show what the bound would be if you found a 9-element DSS from 1 to 100
        nine_element_dss_text = TexText("9-element DSS Set from 1 to 100:", font_size = 80).shift(UP*2)
        self.play(Write(nine_element_dss_text), run_time = 2.5)
        self.wait(1)
        c_upper_bound = Tex(
            R"c \leq \frac{100}{2^{9}} = 0.1953125", font_size = 80, tex_to_color_map = {"c": RED, "100": BLUE, "{9}": YELLOW}
        )
        self.play(Write(c_upper_bound[R"c \leq \frac{100}{2^{9}}"]), run_time = 2.5)
        self.wait(1)
        self.play(FadeIn(c_upper_bound["= 0.1953125"], run_time = 2))

class QuestionTable(InteractiveScene):
    def construct(self):
        # Add the table
        table = VGroup(*[
            VGroup(*[
                Rectangle(width = 4 if i == 0 else 3, height = 1, fill_opacity = 0, stroke_width = 3, stroke_color = GREY)
                for i in range(2)
            ]).arrange(RIGHT, buff = 0)
            for _ in range(4)
        ]).arrange(DOWN, buff = 0)
        data = VGroup(
            VGroup(TexText("7 elements").set_color(BLUE), TexText("possible").set_color(GREEN)),
            VGroup(TexText("8 elements").set_color(BLUE), TexText("?").set_color(YELLOW).set_opacity(0)),
            VGroup(TexText("9 elements").set_color(BLUE), TexText("?").set_color(YELLOW).set_opacity(0)),
            VGroup(TexText("10 elements").set_color(BLUE), TexText("impossible").set_color(RED))
        )
        for i in range(len(data)):
            data[i][0].move_to(table[i][0])
            data[i][1].move_to(table[i][1]).align_to(data[i][0], UP)
            table.add(data)
        self.add(table)
        self.wait(1)
        group = VGroup(data[1][1], data[2][1])
        self.camera.frame.save_state()
        self.play(
            self.camera.frame.animate(run_time = 4).scale(0.7, about_point = group.get_center()),
            group.animate(run_time = 2).set_opacity(1)
        )
        self.wait(2)

        # Fill in the row for n = 8
        self.play(data[1][1].animate.become(TexText("possible").set_color(GREEN).move_to(data[1][1])), run_time = 1.2)
        self.wait(3)

        # Fill to the row for n = 9
        rect = SurroundingRectangle(table[2], buff = 0, stroke_width = 6).set_color(YELLOW)
        self.play(Succession(ShowCreation(rect, run_time = 2), FadeOut(rect)), self.camera.frame.animate.match_y(table[2]), run_time = 2)
        self.wait(1)
        self.play(data[2][1].animate.become(TexText("unknown!").set_color(YELLOW).move_to(data[2][1])), run_time = 1.2)
        self.wait(3)

        # Change that row to "unlikely"
        self.camera.frame.restore()
        self.wait(0.5)
        self.play(data[2][1].animate.become(TexText("unlikely").set_color(YELLOW).move_to(data[2][1]).align_to(data[2][1], UP)), run_time = 1.2)
