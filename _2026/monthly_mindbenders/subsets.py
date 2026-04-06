from manim_imports_ext import *


class Subsets(InteractiveScene):
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
        groups = self.find_a_match(sample).copy()
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

    def find_a_match(self, group):
        value_to_mob = {mob.get_value(): mob for mob in group}
        values = list(value_to_mob.keys())
        sums_to_subsets = dict()
        match = ()
        subsets = it.chain(*(
            it.combinations(values, n)
            for n in range(len(values))
        ))
        for subset in subsets:
            sub_sum = sum(subset)
            if sub_sum in sums_to_subsets:
                match = (sums_to_subsets[sub_sum], subset)
                break
            sums_to_subsets[sub_sum] = subset

        clean_match = [
            set(match[0]).difference(match[1]),
            set(match[1]).difference(match[0]),
        ]

        return VGroup(
            VGroup(
                value_to_mob[value]
                for value in match
            )
            for match in clean_match
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
    random_seed = 3

class Subsets5(Subsets):
    random_seed = 4

class Subsets6(Subsets):
    random_seed = 5

class Subsets7(Subsets):
    random_seed = 6

class Subsets8(Subsets):
    random_seed = 7

class Subsets9(Subsets):
    random_seed = 8

class Subsets10(Subsets):
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
            Tex(f"{sample_list[i].get_value():010b}", font_size = 30).set_color(YELLOW_D)
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
                    YELLOW_D
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
        final_sample.set_color(YELLOW_D)
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
            R"$\leq {100} \cdot {10} = {1000}$ total sums", font_size = 40, tex_to_color_map = {"{1000}": RED}
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
        all_subsets = VGroup()
        for i in range(2**10):
            subset = (
                VGroup(*[sample[len(sample) - 1 - j].copy() for j in range(10) if (i//2**j) % 2 == 1]).arrange(buff = 0.1)
                if i > 0 else Tex(r"\varnothing").set_color(YELLOW)
            )
            rect = SurroundingRectangle(subset, fill_opacity = 0, stroke_width = 1, stroke_color = YELLOW)
            total = VGroup(Tex(R"\rightarrow"), Integer(sum([num.get_value() for num in subset]) if i > 0 else 0)).arrange(buff = 0.1).match_height(subset).set_color(RED).next_to(rect, RIGHT, buff = 0.1)
            all_subsets.add(VGroup(subset, rect, total) if i > 0 else VGroup(subset, total))
        all_subsets = VGroup(*sorted(all_subsets, key = lambda s: s.get_width()))
        n_cols = 16
        all_subsets.arrange_in_grid(n_cols = n_cols, h_buff = 0, buff = 0, fill_rows_first = False)
        columns = VGroup()
        for col in range(n_cols):
            columns.add(all_subsets[col*len(all_subsets)//n_cols:(col + 1)*len(all_subsets)//n_cols])
        columns.arrange(buff = 0.2).set_width(FRAME_WIDTH*0.99)
        bounds = VGroup(number_of_subsets_1024, number_of_sums_bound_trimmed)
        bounds_rect = BackgroundRectangle(bounds)
        self.add(bounds_rect, Point(), bounds)
        self.play(FadeIn(bounds_rect))
        # bounds_rect.fix_in_frame()
        self.bring_to_front(bounds_rect, bounds)
        self.play(
            FadeOut(VGroup(randy, morty), shift = DOWN),
            ReplacementTransform(sample, all_subsets),
            VGroup(bounds_rect, bounds).animate.to_edge(UP, buff = 0.2)
        , run_time = 1.5)
        VGroup(bounds_rect, bounds).fix_in_frame()
        self.add(VGroup(bounds_rect, bounds))

        # for i in range(len(all_subsets)):
        #     if all_subsets[i][-1][1].get_value() == 314:
        #         print(i)
        index1 = 498
        index2 = 784
        self.play(self.camera.frame.animate.reorient(0, 0, 0, (np.float32(-1.39), np.float32(-2.32), np.float32(0.0)), 1.75), run_time = 2)
        rect = SurroundingRectangle(all_subsets[index1], fill_opacity = 0, stroke_width = 3, stroke_color = PURE_GREEN, buff = 0.01)
        self.play(ShowCreation(rect))
        self.play(self.camera.frame.animate.reorient(0, 0, 0, (np.float32(3.09), np.float32(1.71), np.float32(0.0)), 1.74), run_time = 4)
        rect = SurroundingRectangle(all_subsets[index2], fill_opacity = 0, stroke_width = 3, stroke_color = PURE_GREEN, buff = 0.01)
        self.play(ShowCreation(rect))
        self.wait(3)


class WritePigeonholdPrinciple(Scene):
    def construct(self):
        self.play(Write(TexText("Pigeonhole Principle", font_size = 70)))