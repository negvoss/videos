import math
from functools import lru_cache

from manim_imports_ext import *
from _2026.cross_entropy.distribution import DynamicInterval
from _2026.cross_entropy.distribution import StackedProbDistribution
from _2026.cross_entropy.next_char import CHAR_ALPHABET
from _2026.cross_entropy.next_char import get_next_char_distribution
from _2026.cross_entropy.next_char import total_information


def get_random_distribution(length):
    dist = np.random.random(30)
    dist /= sum(dist)
    return dist


@lru_cache(maxsize=None)
def cached_next_char_distribution(context):
    # Filling in branch layers can mean hundreds of model calls, many repeated across renders
    return np.array(get_next_char_distribution(context), dtype=float)


class RenormalizeAnimation(MoveToTarget):
    def begin(self):
        self.mobject.is_renormalizing = True
        self.mobject.ids_in_transform = {id(mob) for mob in self.mobject.get_family()}
        super().begin()

    def finish(self):
        super().finish()
        self.mobject.is_renormalizing = False
        self.mobject.ids_in_transform = set()
        self.mobject.target = None


class ArithmeticCodingDiagram(Group):
    def __init__(
        self,
        width=12,
        buff_to_bars=0.25,
        show_decimal_labels=True,
        interval_subdivisions=10,
        char_alphabet=CHAR_ALPHABET,
        highlight_colors=(GREEN_E, GREEN_D),
        label_to_bar_height_ratio=0.5,
        context=" ",
    ):
        self.layers = VGroup()
        self.branches = VGroup()
        self.layer_by_prefix = dict()
        self.min_branch_width = 0
        self.is_renormalizing = False
        self.ids_in_transform = set()
        self.intervals = VGroup()
        self.full_width = width
        self.show_decimal_labels = show_decimal_labels
        self.interval_subdivisions = interval_subdivisions
        self.char_alphabet = char_alphabet
        self.label_to_bar_height_ratio = label_to_bar_height_ratio
        self.context = context

        self.highlight_color_iter = it.cycle(highlight_colors)

        self.unit_interval = DynamicInterval(width=width)
        self.intervals.add(self.unit_interval)
        self.interval_keys = {(1, 0)}  # Of the form (step_size, lower_bound_int)

        self.curr_text = ""  # Start with a neutral context
        self.char_labels_template = Text(char_alphabet)
        self.layers.add(self.get_new_layer(buff=SMALL_BUFF))

        super().__init__(self.intervals, Point(), self.branches, self.layers)

    def get_distribution(self, prefix):
        return cached_next_char_distribution(self.context + prefix).copy()

    def get_new_layer(self, buff=0.1):
        if len(self.layers) == 0:
            mob_above = self.unit_interval[0]
        else:
            mob_above = self.get_letter_bar(self.curr_text[-1])
        return self.make_layer(self.curr_text, mob_above, buff=buff)

    def make_layer(self, prefix, mob_above, buff=0.1, build_width=None):
        distribution = self.get_distribution(prefix)
        # if len((self.context + prefix).strip()) == 0:
        #     # Artificially suppress punctuation
        #     distribution[26:] *= 1e-3
        #     distribution /= sum(distribution)

        target_width = mob_above.get_width()
        layer = StackedProbDistribution(
            distribution,
            labels=self.char_labels_template.copy(),
            width=build_width or target_width,
            label_height_ratio=self.label_to_bar_height_ratio
        )
        if build_width is not None:
            layer.stretch(target_width / layer.bars.get_width(), 0)
            layer.reposition_labels()
        layer.next_to(mob_above, DOWN, buff=buff)

        layer.prefix = prefix
        layer.default_bar_style = [
            (bar.get_fill_color(), bar.get_fill_opacity())
            for bar in layer.bars
        ]
        first_bar = layer.bars[0]
        layer.default_stroke_style = (
            first_bar.get_stroke_color(),
            float(first_bar.get_stroke_width()),
            float(first_bar.get_stroke_opacity()),
        )
        self.layer_by_prefix[prefix] = layer
        return layer

    def make_branch_layer(self, prefix, parent_bar, buff=0.1):
        layer = self.make_layer(prefix, parent_bar, buff=buff, build_width=self.full_width)
        self.update_bar_strokes(layer)
        layer.highlight_state = "default"
        layer.is_branch = True
        layer.is_visible = False
        return layer

    def update_visible_path(self, value):
        x = self.unit_interval.n2p(value)[0]
        n_rows = len(self.layers)
        path = {""}
        prefix = ""
        layer = self.layer_by_prefix[""]
        while True:
            index = int(np.clip(layer.x_value_to_index(x), 0, len(layer.bars) - 1))
            child_prefix = prefix + self.char_alphabet[index]
            if len(child_prefix) >= n_rows:
                break
            child = self.layer_by_prefix.get(child_prefix)
            if child is None:
                bar = layer.bars[index]
                if bar.get_width() <= self.min_branch_width:
                    break
                child = self.make_branch_layer(child_prefix, bar)
            self.set_layer_visibility(child, True)
            if self.is_renormalizing and id(child.bars) not in self.ids_in_transform:
                self.fit_layer_to_parent(child)
            path.add(child_prefix)
            prefix, layer = child_prefix, child

        for other_prefix, other_layer in self.layer_by_prefix.items():
            if other_prefix not in path:
                self.set_layer_visibility(other_layer, False)

    def show_all_layers(self):
        for prefix in sorted(self.layer_by_prefix, key=len):
            if prefix:
                self.set_layer_visibility(self.layer_by_prefix[prefix], True)

    def set_layer_visibility(self, layer, visible):
        if getattr(layer, "is_visible", True) == visible:
            return
        is_branch = getattr(layer, "is_branch", False)
        if visible:
            if is_branch:
                self.branches.add(layer)
            else:
                layer.set_submobjects(layer.stashed_submobjects)
            self.fit_layer_to_parent(layer)
        else:
            self.reset_layer_style(layer)
            layer.highlight_state = "default"
            if is_branch:
                self.branches.remove(layer)
            else:
                layer.stashed_submobjects = list(layer.submobjects)
                layer.set_submobjects([])
        layer.is_visible = visible

    def fit_layer_to_parent(self, layer):
        parent = self.layer_by_prefix[layer.prefix[:-1]]
        bar = parent.bars[self.char_alphabet.index(layer.prefix[-1])]
        layer.stretch(bar.get_width() / layer.bars.get_width(), 0)
        layer.shift((bar.get_left()[0] - layer.bars.get_left()[0]) * RIGHT)
        layer.reposition_labels()
        self.update_bar_strokes(layer)
        return layer

    def update_bar_strokes(self, layer, min_width=0.05, sliver_stroke_width=1.0):
        stroke_color, stroke_width, stroke_opacity = layer.default_stroke_style
        for bar in layer.bars:
            alpha = clip(bar.get_width() / min_width, 0, 1)
            bar.set_stroke(
                color=interpolate_color(bar.get_fill_color(), stroke_color, alpha),
                width=interpolate(sliver_stroke_width, stroke_width, alpha),
                opacity=interpolate(bar.get_fill_opacity(), stroke_opacity, alpha),
            )
        return layer

    def get_sweep_range(self, mob, buff=0.01):
        view = self.target if getattr(self, "target", None) is not None else self
        view_mob = view.get_family()[self.get_family().index(mob)]
        low = view.unit_interval.p2n(view_mob.get_left() + buff * RIGHT)
        high = view.unit_interval.p2n(view_mob.get_right() + buff * LEFT)
        return low, high

    def get_letter_bar(self, char, layer_index=-1):
        index = self.char_alphabet.index(char)
        return self.layers[layer_index].bars[index]

    def get_letter_label(self, char, layer_index=-1):
        index = self.char_alphabet.index(char)
        return self.layers[layer_index].labels[index]

    def populate_intervals(self, x_min, x_max):
        log_val = np.log(x_max - x_min) / np.log(self.interval_subdivisions)
        min_scale = int(np.ceil(np.round(log_val, 1)))

        for scale in range(-1, min_scale - 1, -1):
            step = self.interval_subdivisions**(scale)
            for lower_bound_int in range(int(x_min / step) - 1, int(x_max / step) + 1):
                interval_key = (step, lower_bound_int)
                if interval_key in self.interval_keys:
                    continue
                low = lower_bound_int * step
                high = (lower_bound_int + 1) * step
                interval = DynamicInterval(
                    x_range=(low, high),
                    width=get_norm(self.unit_interval.n2p(high) - self.unit_interval.n2p(low)),
                    subdivisions=self.interval_subdivisions,
                    include_numbers=self.show_decimal_labels,
                    include_endpoint_numbers=False,
                    number_font_size=24 + scale * 2,
                )
                interval.shift(self.unit_interval.n2p(low) - interval.n2p(low))
                self.intervals.add(interval)
                self.interval_keys.add(interval_key)
        return self

    def get_conditional_probability(self, char, layer_index=-1):
        idx = self.char_alphabet.index(char)
        return self.layers[layer_index].distribution[idx]

    def get_absolute_information(self, text):
        result = 0
        for layer, char in zip(self.layers, text):
            result += -math.log2(layer.distribution[self.char_alphabet.index(char)])
        return result

    # Decoding values into words
    def get_layer_chain(self, value):
        x = self.unit_interval.n2p(value)[0]
        chain = []
        prefix = ""
        while prefix in self.layer_by_prefix:
            layer = self.layer_by_prefix[prefix]
            if not getattr(layer, "is_visible", True):
                break  # Its geometry may be stale; get_word_at_value decodes the rest numerically
            index = int(np.clip(layer.x_value_to_index(x), 0, len(layer.bars) - 1))
            chain.append((layer, index))
            prefix += self.char_alphabet[index]
        return chain, prefix

    def decode_value(self, value, low, high, prefix="", n_chars=1):
        result = ""
        for _ in range(n_chars):
            dist = self.get_distribution(prefix + result)
            dist = dist / dist.sum()
            cumulative = np.cumsum(dist)
            alpha = (value - low) / (high - low) if high > low else 0
            index = int(min(np.searchsorted(cumulative, alpha, side="right"), len(dist) - 1))
            low, high = (
                low + (high - low) * (cumulative[index] - dist[index]),
                low + (high - low) * cumulative[index],
            )
            result += self.char_alphabet[index]
        return result

    def get_word_at_value(self, value, n_chars=None):
        if n_chars is None:
            n_chars = len(self.layers)
        chain, prefix = self.get_layer_chain(value)
        prefix = prefix[:n_chars]
        if len(prefix) < n_chars:
            parent, index = chain[-1]
            bar = parent.bars[index]
            low, high = (self.unit_interval.p2n(point) for point in (bar.get_left(), bar.get_right()))
            prefix += self.decode_value(value, low, high, prefix, n_chars - len(prefix))
        return prefix

    def reset_layer_style(self, layer):
        for bar, (color, opacity) in zip(layer.bars, layer.default_bar_style):
            bar.set_fill(color, opacity)

    def highlight_value(self, value, color=None, other_bar_opacity=0.35):
        chain, _ = self.get_layer_chain(value)
        chain_indices = {id(layer): index for layer, index in chain}
        for layer in self.layer_by_prefix.values():
            if not getattr(layer, "is_visible", True):
                continue
            new_state = chain_indices.get(id(layer), "default")
            if new_state == "default" and getattr(layer, "highlight_state", None) == "default":
                continue
            self.reset_layer_style(layer)
            if new_state != "default":
                if color is None:
                    layer.highlight(new_state, other_bar_opacity=other_bar_opacity)
                else:
                    layer.highlight(new_state, color, other_bar_opacity=other_bar_opacity)
                # Keep thin bars' sliver outlines matching their new fill
                self.update_bar_strokes(layer)
            layer.highlight_state = new_state

    # Animations
    def renormalize_animation(
        self,
        x_min,
        x_max,
        run_time=3,
        center=ORIGIN,
        center_curr_text=False,
        stretch_factor=None,
        fade_thin_strokes=False,
        **kwargs
    ):
        big_interval = self.intervals[0]
        x_mid = (x_min + x_max) / 2
        p_left, p_mid, p_right = [big_interval.n2p(x) for x in (x_min, x_mid, x_max)]

        if stretch_factor is None:
            stretch_factor = self.full_width / get_norm(p_right - p_left)
        x_shift = (center - p_mid)[0] * RIGHT

        self.populate_intervals(x_min, x_max)
        for interval in self.intervals:
            interval.update_opacity_from_width()

        self.generate_target()
        for interval in self.target.intervals:
            interval.shift(x_shift)
            interval.stretch(stretch_factor, 0, about_point=ORIGIN)
        for layer in [*self.target.layers, *self.target.branches]:
            if not getattr(layer, "is_visible", True):
                continue  # Emptied-out main layer; it gets refit when shown again
            layer.shift(x_shift)
            layer.stretch(stretch_factor, 0, about_point=ORIGIN)
            layer.reposition_labels()
            if fade_thin_strokes:
                self.update_bar_strokes(layer)
        if center_curr_text:
            for layer, char in zip(self.target.layers, self.curr_text):
                if not getattr(layer, "is_visible", True):
                    continue
                index = self.char_alphabet.index(char)
                bar = layer.bars[index]
                # Only pin labels whose bar actually spans the center. When zooming out,
                # deeper letters in curr_text should sit at their natural positions.
                if bar.get_left()[0] <= center[0] <= bar.get_right()[0]:
                    layer[1][index].match_x(center)

        return RenormalizeAnimation(self, run_time=run_time, **kwargs)

    def highlight_letter(
        self,
        char,
        color=None,
        layer_index=-1,
        other_bar_opacity=0.35,
        add_to_text=False
    ):
        if color is None:
            color = next(self.highlight_color_iter)
        index = self.char_alphabet.index(char)
        animation = self.layers[layer_index].animate.highlight(
            index,
            color,
            other_bar_opacity=other_bar_opacity
        )

        if add_to_text:
            self.curr_text += char

        return animation

    def zoom_in_on_letter(self, char, layer_index=-1, add_to_text=True, **kwargs):
        if add_to_text:
            idx = layer_index % len(self.layers)
            # Re-zooming on a letter already in the path leaves deeper letters alone
            if idx >= len(self.curr_text) or self.curr_text[idx] != char:
                self.curr_text = self.curr_text[:idx] + char
        return self.zoom_in_on_letter_range((char, char), layer_index=layer_index, **kwargs)

    def zoom_in_on_letter_range(self, letter_range, layer_index=-1, **kwargs):
        char1, char2 = letter_range
        bar1 = self.get_letter_bar(char1, layer_index)
        bar2 = self.get_letter_bar(char2, layer_index)
        x_min = self.unit_interval.p2n(bar1.get_left())
        x_max = self.unit_interval.p2n(bar2.get_right())
        if x_min > x_max:
            raise ValueError("Second letter in range must be alphabetically after first letter")
        return self.renormalize_animation(x_min, x_max, center_curr_text=True, **kwargs)

    def fade_in_new_layer(self, char=None, buff=0):
        layer = self.get_new_layer()
        self.layers.add(layer)
        return FadeIn(layer)


class IntroduceCharacterModel(InteractiveScene):

    def construct(self):
        # Show a few example distributions
        frame = self.frame
        input_phrase = "compression is "
        n_initial_letters = 1
        char_labels = CHAR_ALPHABET.replace(" ", "_")
        distribution = get_next_char_distribution(input_phrase[:n_initial_letters])
        bar_chart = self.get_bar_chart(distribution, char_labels)

        out_arrow = Line(3 * UP, 3 * RIGHT, path_arc=-90 * DEG, stroke_width=8, buff=0)
        out_arrow.add_tip(width=0.5, length=0.5)
        out_arrow.set_color(GREY_B)
        out_arrow.shift(bar_chart.get_bottom() - out_arrow.get_end() + 5 * UP)
        model = ImageMobject(Path(
            self.file_writer.get_output_file_rootname().parent.parent,
            "Paul Assets", "BigModel.png"
        ))
        model.set_height(5)
        model.rotate(-2 * DEG)
        model.next_to(out_arrow.get_start(), LEFT)
        in_arrow = Vector(RIGHT, thickness=5)
        in_arrow.next_to(model, LEFT)
        in_arrow.scale(1.5, about_edge=LEFT)

        def get_in_text(s, font_size=72):
            result = Text(f"“{s}”", font_size=font_size)
            result.next_to(in_arrow, LEFT, buff=0.15)
            result.shift(0.05 * UP)
            return result

        def get_bar_chart(in_text):
            return self.get_bar_chart(
                distribution=get_next_char_distribution(in_text),
                labels=char_labels
            )

        in_text_mob = get_in_text(input_phrase[:n_initial_letters])

        frame.reorient(0, 0, 0, (-4.50, 2.56, 0.00), 12.89)
        self.add(model, in_text_mob, in_arrow, out_arrow, bar_chart)
        self.wait(0.5)
        for n in range(n_initial_letters + 1, len(input_phrase) + 1):
            in_text_mob.set_submobjects(get_in_text(input_phrase[:n]))
            new_chart = get_bar_chart(input_phrase[:n])
            self.play(ReplacementTransform(bar_chart, new_chart), run_time=0.25)
            bar_chart = new_chart
            self.wait(0.5)

        # Highlight distribution and limited vocabulary
        wide_char_rect = SurroundingRectangle(bar_chart.labels, buff=0.05)
        wide_char_rect.set_stroke(YELLOW, 2)
        char_rects = VGroup(
            wide_char_rect.copy().set_width(label.get_width() + 0.1, stretch=True).match_x(label)
            for label in bar_chart.labels
        )
        alphabet_rects = char_rects[:26]
        punc_rects = char_rects[26:]

        in_rect = SurroundingRectangle(in_text_mob)
        out_rect = SurroundingRectangle(bar_chart)
        in_rect.set_stroke(TEAL, 3)
        out_rect.set_stroke(TEAL, 3)
        out_arrow.set_z_index(1)

        self.play(ShowCreation(in_rect))
        self.wait()
        self.play(
            frame.animate(time_span=(0.5, 2.5)).to_default_state().set_y(-1),
            ReplacementTransform(in_rect, out_rect, run_time=1)
        )
        self.wait()
        self.play(
            FadeOut(out_rect),
            ShowCreation(alphabet_rects, lag_ratio=0.05, run_time=2),
        )
        self.wait()
        self.play(
            FadeOut(alphabet_rects, lag_ratio=0.01),
            ShowCreation(punc_rects, lag_ratio=0.1),
        )
        self.wait()
        self.play(
            frame.animate(run_time=3).reorient(0, 0, 0, (-4.50, 2.56, 0.00), 12.89),
            FadeOut(punc_rects, time_span=(1, 2)),
        )

        # Show blank space input
        for n in range(len(input_phrase), -1, -1):
            in_text_mob.set_submobjects(get_in_text(input_phrase[:n]))
            new_chart = get_bar_chart(input_phrase[:n] or " ")
            self.play(ReplacementTransform(bar_chart, new_chart), run_time=0.1)
            bar_chart = new_chart
            self.wait(0.1)
        self.wait()

        self.play(
            frame.animate.reorient(0, 0, 0, (-1.69, 1.39, 0.00), 9.99),
            LaggedStart(*(
                bar.animate(rate_func=there_and_back).set_fill(YELLOW)
                for bar in bar_chart.bars
            ), lag_ratio=0.25),
            LaggedStart(*(
                FadeIn(rect, rate_func=there_and_back)
                for rect in char_rects
            ), lag_ratio=0.25),
            run_time=7
        )

        # Transition to horizontal stack
        diagram = ArithmeticCodingDiagram()
        layer = diagram.layers[0]
        new_dec_labels = self.get_stacked_distribution_dec_labels(layer)

        for bar in bar_chart.bars:
            og = bar.copy()
            bar.rotate(90 * DEG)
            bar.replace(og, stretch=True)

        kw = dict(run_time=3, lag_ratio=0.05)
        self.play(
            LaggedStart(
                (FadeTransform(dec1, dec2)
                 for dec1, dec2 in zip(bar_chart.dec_labels, new_dec_labels)),
                group_type=Group,
                **kw
            ),
            ReplacementTransform(bar_chart.bars, layer.bars, **kw),
            ReplacementTransform(bar_chart.labels, layer.labels, **kw),
            LaggedStartMap(FadeOut, Group(in_text_mob, in_arrow, model, out_arrow), shift=UP, time_span=(1, 3)),
            frame.animate(run_time=3).to_default_state().set_y(-1),
        )
        self.add(layer)
        self.wait()

    def get_bar_chart(
        self,
        distribution,
        labels,
        bar_colors=(BLUE_E, TEAL),
        spacing=0.15,
        bar_width=0.25,
        unit_height=15,
        max_height=5,
        label_font_size=36,
        dec_font_size=16,
        bottom=2 * DOWN
    ):
        bars = VGroup(
            Rectangle(width=bar_width, height=prob * unit_height)
            for prob in distribution
        )
        bars.arrange(RIGHT, buff=spacing, aligned_edge=DOWN)
        bars.set_fill(bar_colors, 1, gradient_direction=RIGHT)
        bars.set_stroke(WHITE, 1)
        bars.set_max_height(max_height, stretch=True)
        bars.center()

        dec_labels = VGroup(
            DecimalNumber(100 * prob, font_size=dec_font_size, unit="%", num_decimal_places=1)
            for prob in distribution
        )
        dec_labels.set_fill(GREY_B)
        char_labels = Text(labels, font_size=label_font_size)
        char_labels.next_to(bars, DOWN, SMALL_BUFF)

        for bar, char, dec in zip(bars, char_labels, dec_labels):
            char.match_x(bar)
            dec.next_to(bar, UP, SMALL_BUFF)

        result = VGroup(bars, char_labels, dec_labels)
        result.labels = char_labels
        result.dec_labels = dec_labels
        result.bars = bars
        result.move_to(bottom, DOWN)
        return result

    def get_stacked_distribution_dec_labels(self, layer, font_size=12, num_decimal_places=2):
        dec_labels = VGroup(
            DecimalNumber(x, font_size=font_size, num_decimal_places=num_decimal_places)
            for x in layer.distribution
        )
        dec_labels.set_fill(GREY_B)
        for dec, bar in zip(dec_labels, layer.bars):
            dec.next_to(bar, DOWN, buff=SMALL_BUFF)
            if dec.get_width() > bar.get_width():
                dec.set_opacity(0)
        return dec_labels

    def get_stacked_distribution_pct_labels(self, layer, font_size=12, num_decimal_places=2):
        pct_labels = VGroup(
            DecimalNumber(x * 100, font_size=font_size, num_decimal_places=num_decimal_places, unit=R"\%")
            for x in layer.distribution
        )
        pct_labels.set_fill(GREY_B)
        for pct, bar in zip(pct_labels, layer.bars):
            pct.next_to(bar, DOWN, buff=SMALL_BUFF)
            if pct.get_width() > bar.get_width():
                pct.set_opacity(0)
        return pct_labels

    def old_animations(self):
        for group in bar_chart:
            for mob in group:
                mob.save_state()
                mob.scale(0)
                mob.set_opacity(0)
                mob.move_to(model.get_right())

        frame.reorient(0, 0, 0, (-3.64, 2.97, 0.00), 11.64)
        self.add(model, in_text, in_arrow, out_arrow)
        kw = dict(lag_ratio=0.02, path_arc=-45 * DEG, run_time=2)
        self.play(*(
            LaggedStartMap(Restore, group, **kw)
            for group in bar_chart
        ))
        self.wait()


class ProbabilityOfAWord(IntroduceCharacterModel):
    interval_width = 12

    def construct(self):
        # Add diagram
        frame = self.frame
        diagram = ArithmeticCodingDiagram()
        layer = diagram.layers[0]
        dec_labels = self.get_stacked_distribution_dec_labels(layer)

        frame.set_y(-1)
        self.add(layer, dec_labels)

        # Show full width
        over_brace = Brace(layer, UP)
        over_brace.refresh_bounding_box()
        over_brace.save_state()
        over_brace.stretch(1e-4, 0, about_edge=LEFT)

        width_label = DecimalNumber(0.00)

        def update_width_label(label):
            label.set_value(over_brace.get_width() / layer.get_width())
            label.next_to(over_brace, UP, buff=0.35)
            label.set_opacity(clip(over_brace.get_width() / 5, 0, 1))

        new_dec_rects = VGroup(
            SurroundingRectangle(dec, buff=0.05).set_stroke(YELLOW, 1, opacity=dec.get_opacity())
            for dec in dec_labels
        )

        self.play(
            Restore(over_brace),
            UpdateFromFunc(width_label, update_width_label),
            run_time=2
        )
        self.wait()
        self.add(layer.bars, Point(), layer.labels)
        self.play(
            layer.bars.animate.set_fill(YELLOW, 0.7).set_anim_args(rate_func=there_and_back, lag_ratio=0.05, run_time=3),
            FadeIn(new_dec_rects, rate_func=there_and_back, lag_ratio=0.05, run_time=3),
        )
        self.wait()

        # Show unit interval
        brace_group = VGroup(over_brace, width_label)
        unit_interval = diagram.unit_interval
        self.play(
            Write(unit_interval, lag_ratio=0.01),
            brace_group.animate.next_to(unit_interval[0], UP, MED_LARGE_BUFF),
            frame.animate.set_width(13).set_y(0),
        )
        unit_interval.numbers.set_backstroke(BLACK, 3)
        self.play(FadeOut(brace_group))
        self.wait()

        # Show a value over this interval
        x_tracker = ValueTracker()
        get_x = x_tracker.get_value
        x_arrow = Vector(DOWN, thickness=5)
        x_arrow.add_updater(lambda m: m.move_to(unit_interval.n2p(get_x()), DOWN))
        x_arrow.set_z_index(-1)
        x_dec = DecimalNumber(0, num_decimal_places=3)
        x_dec.f_always.set_value(get_x)
        x_dec.always.next_to(x_arrow, UP, SMALL_BUFF)
        layer.add_updater(lambda m: m.highlight(m.float_to_index(get_x())))

        self.add(layer)
        self.play(
            VFadeIn(x_arrow, time_span=(0, 1)),
            VFadeIn(x_dec, time_span=(0, 1)),
            x_tracker.animate.set_value(1),
            run_time=6
        )

        # Highlight "t"
        t_bar, p_bar, q_bar = VGroup(
            diagram.get_letter_bar(char)
            for char in "tpq"
        )

        t_brace = Brace(t_bar, DOWN)
        p_brace = Brace(p_bar, DOWN)
        t_brace_label = DecimalNumber(diagram.get_conditional_probability("t"), font_size=24)
        t_brace_label.next_to(t_brace, DOWN, SMALL_BUFF)
        p_brace_label = DecimalNumber(diagram.get_conditional_probability("p"), font_size=24)
        p_brace_label.next_to(p_brace, DOWN, SMALL_BUFF)

        pre_dec_label = dec_labels[ord("t") - ord("a")]
        dec_labels.remove(pre_dec_label)

        self.play(
            VFadeOut(x_dec),
            x_tracker.animate.set_value(unit_interval.p2n(layer.bars[19].get_center())),
            run_time=2
        )
        self.play(
            x_tracker.animate(rate_func=wiggle, run_time=4).set_value(unit_interval.p2n(layer.bars[19].get_left() + 0.2 * LEFT)),
            GrowFromCenter(t_brace),
            TransformFromCopy(pre_dec_label, t_brace_label),
            FadeOut(dec_labels)
        )
        layer.clear_updaters()
        self.play(FadeOut(x_arrow))
        self.wait()

        # Highlight "p"
        self.add(diagram)
        self.play(
            diagram.highlight_letter("p", TEAL, other_bar_opacity=0.25),
            ReplacementTransform(t_brace, p_brace),
            ReplacementTransform(t_brace_label, p_brace_label),
        )
        self.wait()

        # Show "q"
        self.play(
            diagram.zoom_in_on_letter_range(("p", "q"), stretch_factor=18),
            UpdateFromFunc(p_brace, lambda m: m.become(Brace(p_bar, DOWN))),
            UpdateFromFunc(p_brace_label, lambda m: m.next_to(p_brace, DOWN, SMALL_BUFF))
        )
        self.wait()

        q_brace = Brace(q_bar, DOWN)
        q_brace_label = DecimalNumber(
            diagram.get_conditional_probability("q"),
            num_decimal_places=3,
            font_size=24,
        )
        q_brace_label.next_to(q_brace, DOWN)

        self.play(
            TransformFromCopy(p_brace, q_brace),
            FadeTransform(p_brace_label.copy(), q_brace_label),
            diagram.highlight_letter("q", TEAL),
        )
        self.wait()
        self.add(layer.bars, Point(), layer.labels)
        self.play(
            FadeOut(VGroup(p_brace, q_brace, p_brace_label, q_brace_label)),
            layer.bars.animate.set_fill(opacity=1).set_submobject_colors_by_gradient(BLUE_E, TEAL_E).set_stroke(WHITE, 1),
        )
        self.wait()
        self.play(diagram.renormalize_animation(0, 1), run_time=2)
        self.wait()

        # To do, let the x_tracker range over the full bar and add functionality to populate the relevant
        # stack of letters underneath it.

        # Cycle through some letters, ask about P("math")
        def get_letter_prob_label(char):
            brace = Brace(diagram.get_letter_bar(char), DOWN, buff=SMALL_BUFF)
            label = brace.get_tex(f"P(``{char}\")", font_size=36, buff=SMALL_BUFF)
            return VGroup(brace, label)

        prob_label = get_letter_prob_label("a")
        self.play(
            GrowFromCenter(prob_label[0]),
            Write(prob_label[1]),
        )
        for idx in range(1, 13):
            char = diagram.char_alphabet[idx]
            new_label = get_letter_prob_label(char)
            self.play(
                ReplacementTransform(prob_label[0], new_label[0]),
                FadeTransformPieces(prob_label[1], new_label[1]),
            )
            prob_label = new_label
        self.wait()

        p_math = Tex("P(``math\")?")
        p_math.to_edge(UP, buff=1)
        self.play(FadeIn(p_math, UP))
        self.wait()

        # Zoom in on the "m"
        self.play(diagram.highlight_letter("m"))
        self.play(FadeOut(prob_label))
        self.play(
            diagram.zoom_in_on_letter("m"),
            p_math.animate(path_arc=PI * 0.3).set_opacity(0.5).to_corner(DL, buff=0.5).fix_in_frame(),
        )
        self.play(diagram.fade_in_new_layer(), self.camera.frame.animate.match_y(diagram))
        self.wait()

        # Show the domination of the vowels
        pct_labels = self.get_stacked_distribution_pct_labels(diagram.layers[1], font_size=25)

        def get_letter_pct_label(char):
            brace = Brace(diagram.get_letter_bar(char), DOWN, buff=SMALL_BUFF)
            label = pct_labels[diagram.char_alphabet.index(char)].next_to(brace, DOWN, buff=SMALL_BUFF)
            return VGroup(brace, label)

        pct_label = get_letter_pct_label("a")
        self.play(
            GrowFromCenter(pct_label[0]),
            Write(pct_label[1]),
        )
        for letter in "eiou":
            self.wait(0.5)
            new_label = get_letter_pct_label(letter)
            self.play(
                ReplacementTransform(pct_label[0], new_label[0]),
                FadeTransformPieces(pct_label[1], new_label[1]),
            )
            pct_label = new_label
        self.wait(0.5)
        self.play(FadeOut(pct_label))
        self.wait(1)

        # Zoom out to show the full width of the diagram
        self.play(diagram.renormalize_animation(0, 1))
        brace = Brace(diagram.layers[0], DOWN)
        self.play(GrowFromEdge(brace, UP), FadeOut(diagram.layers[1]))

        # Show the width of just the "m"
        new_brace = Brace(diagram.get_letter_bar("m", layer_index=0))
        label = new_brace.get_tex("P(``m\")", font_size=35)
        self.play(AnimationGroup(brace.animate.become(new_brace), FadeIn(label), lag_ratio=0.6), run_time=2.5)

        # Bring back the second layer
        self.play(
            AnimationGroup(
                VGroup(brace, label).animate.align_to(diagram.layers[1].get_bottom() + DOWN * 0.1, UP),
                FadeIn(diagram.layers[1]),
                lag_ratio=0.3
            )
        )

        # Renormalize around the "m" again
        renormalize_anim = diagram.zoom_in_on_letter("m", layer_index=0)
        new_brace = Brace(diagram.target.get_letter_bar("m", layer_index=0)).align_to(diagram.layers[1].get_bottom() + DOWN * 0.1, UP)
        new_label = new_brace.get_tex("P(``m\")", font_size=35)
        self.play(
            renormalize_anim,
            brace.animate(run_time=3).become(new_brace),
            label.animate(run_time=3).become(new_label)
        )

        # Show the chain rule
        new_brace = Brace(diagram.get_letter_bar("a"), DOWN, buff=SMALL_BUFF)
        new_label = new_brace.get_tex(f"P(``m\") \\cdot P(``a\" | ``m\")", font_size=36, buff=SMALL_BUFF)
        self.play(
            ReplacementTransform(brace, new_brace),
            TransformMatchingShapes(label, new_label),
            run_time=1.7
        )
        brace, label = new_brace, new_label
        self.wait(1)

        # Show the two letter probabilities
        def get_two_letter_prob_label(char):
            brace = Brace(diagram.get_letter_bar(char), DOWN, buff=SMALL_BUFF)
            label = brace.get_tex(f"P(``m{char}\")", font_size=36, buff=SMALL_BUFF)
            return VGroup(brace, label)
        two_letter_prob_label = get_two_letter_prob_label("a")
        self.play(FadeOut(VGroup(brace, label)), FadeIn(two_letter_prob_label))
        self.wait(1)
        for letter in "eiou":
            self.wait(0.5)
            new_label = get_two_letter_prob_label(letter)
            self.play(
                ReplacementTransform(two_letter_prob_label[0], new_label[0]),
                FadeTransformPieces(two_letter_prob_label[1], new_label[1]),
            )
            two_letter_prob_label = new_label
        self.wait(0.5)
        self.play(FadeOut(two_letter_prob_label))
        self.wait(1)

        # Zoom in on the "a"
        self.play(diagram.highlight_letter("a"))
        self.play(diagram.zoom_in_on_letter("a"))
        self.play(diagram.fade_in_new_layer(), self.camera.frame.animate.match_y(diagram))

        # Show the probabilities for the third layer
        def get_three_letter_prob_label(char):
            brace = Brace(diagram.get_letter_bar(char), DOWN, buff=SMALL_BUFF)
            label = brace.get_tex(f"P(``ma{char}\")", font_size=36, buff=SMALL_BUFF)
            return VGroup(brace, label)
        three_letter_prob_label = get_three_letter_prob_label("d")
        self.play(FadeIn(three_letter_prob_label))
        for letter in "lnt":
            self.wait(0.5)
            new_label = get_three_letter_prob_label(letter)
            self.play(
                ReplacementTransform(three_letter_prob_label[0], new_label[0]),
                FadeTransformPieces(three_letter_prob_label[1], new_label[1]),
            )
            three_letter_prob_label = new_label
        self.wait(1)

        # Zoom in on the "t"
        self.play(FadeOut(three_letter_prob_label), diagram.highlight_letter("t"))
        self.play(diagram.zoom_in_on_letter("t"))
        self.play(diagram.fade_in_new_layer(), self.camera.frame.animate.match_y(diagram))

        # Zoom in on the "h"
        self.play(diagram.highlight_letter("h"))
        self.play(diagram.zoom_in_on_letter("h"))

        # Attach the probability label
        brace = Brace(diagram.get_letter_bar("h"), DOWN, buff=SMALL_BUFF)
        label = brace.get_tex(f"P(``math\")", font_size=40, buff=SMALL_BUFF)
        self.play(GrowFromEdge(brace, UP, run_time=2), TransformMatchingShapes(p_math, label, run_time=2))
        self.wait(1)
        self.play(FadeOut(VGroup(brace, label)))

        # Show the slider going over the range again
        h_bar = diagram.get_letter_bar("h")
        x_tracker = ValueTracker(unit_interval.p2n(h_bar.get_left() + RIGHT * 0.01))
        get_x = x_tracker.get_value
        x_arrow = Vector(DOWN, thickness=5)
        x_arrow.add_updater(lambda m: m.move_to(unit_interval.n2p(get_x()), DOWN))
        x_arrow.set_z_index(-1)
        x_dec = DecimalNumber(x_tracker.get_value(), num_decimal_places=7, font_size=17)
        x_dec.f_always.set_value(get_x)
        x_dec.always.next_to(x_arrow, UP, SMALL_BUFF)
        for layer in diagram.layers:
            layer.add_updater(lambda m: m.highlight(m.x_value_to_index(x_arrow.get_x())))

        self.play(
            VFadeIn(x_arrow, time_span=(0, 1)),
            VFadeIn(x_dec, time_span=(0, 1)),
            x_tracker.animate.set_value(unit_interval.p2n(h_bar.get_right())),
            run_time=6
        )
        self.play(x_tracker.animate.set_value(unit_interval.p2n(h_bar.get_left() + RIGHT * 0.01)), run_time=6)

        # Track the word as the x value changes
        def get_word_mob(word):
            mob = Text(f"|{word.replace(" ", "_")}|")
            mob.to_edge(UP, buff=1.3)
            mob.remove(mob[0], mob[-1])
            return mob

        def get_word():
            word = ""
            for layer in diagram.layers:
                word += diagram.char_alphabet[layer.x_value_to_index(x_arrow.get_x())]
            return get_word_mob(word)
        word_tracker = always_redraw(get_word)
        word_tracker.suspend_updating()
        self.play(self.camera.frame.animate.shift(UP), FadeIn(word_tracker, shift=DOWN), run_time=2)
        word_tracker.resume_updating()

        t_zoom = diagram.zoom_in_on_letter("t", layer_index=2, run_time=2)
        t_min, t_max = diagram.get_sweep_range(diagram.get_letter_bar("t", layer_index=2))
        self.play(t_zoom, x_tracker.animate(run_time=9).set_value(t_min))
        self.play(x_tracker.animate(run_time=5).set_value(t_max))

        # Zoom out to the "ma" range
        for layer in diagram.layers:
            layer.clear_updaters()

        def update_diagram_from_tracker(mob):
            diagram.update_visible_path(get_x())
            diagram.highlight_value(get_x())

        highlighter = Mobject()
        highlighter.add_updater(update_diagram_from_tracker)
        self.remove(word_tracker)
        word_tracker = always_redraw(
            lambda: get_word_mob(diagram.get_word_at_value(get_x()).replace(" ", "_"))
        )
        self.add(highlighter, word_tracker)

        math_value = unit_interval.p2n(h_bar.get_center())
        a_zoom = diagram.zoom_in_on_letter(
            "a", layer_index=1,
            add_to_text=False,
            fade_thin_strokes=True,
            run_time=3,
        )
        a_min, a_max = diagram.get_sweep_range(diagram.get_letter_bar("a", layer_index=1))
        self.play(a_zoom, x_tracker.animate(run_time=6).set_value(a_min))

        # Sweep across every four letter word starting with "ma"
        self.play(x_tracker.animate.set_value(a_max), run_time=12, rate_func=linear)
        self.play(x_tracker.animate.set_value(math_value), run_time=6)
        self.wait()

        # Zoom all the way out to the unit interval
        full_zoom = diagram.renormalize_animation(0, 1, fade_thin_strokes=True, run_time=2)
        full_min, full_max = diagram.get_sweep_range(diagram.layers[0].bars)
        self.play(full_zoom, x_tracker.animate(run_time=8).set_value(full_min))

        # Sweep across every possible four letter word
        self.play(x_tracker.animate.set_value(full_max), run_time=8, rate_func=linear)
        self.play(x_tracker.animate.set_value(math_value), run_time=2)
        self.wait()


class SimpleZoom2(InteractiveScene):
    def construct(self):
        # Test
        diagram = ArithmeticCodingDiagram()
        word = "compress"
        self.add(diagram)
        for letter in word:
            self.play(diagram.highlight_letter(letter, color=BLUE_E))
            self.play(
                diagram.zoom_in_on_letter(letter),
                run_time=1
            )
            self.play(
                diagram.fade_in_new_layer(),
                self.frame.animate.shift(0.5 * diagram.layers[0].get_height() * DOWN)
            )

        # Calculate