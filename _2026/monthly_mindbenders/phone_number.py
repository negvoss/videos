from manim_imports_ext import *


class PhoneNumberScene(InteractiveScene):
    n = 123456789
    k = 10

    def construct(self):
        # Set up a multiplcation
        phone_number = Integer(self.n, group_with_commas=False).set_color(BLUE_D)
        multiple_value = ValueTracker(2)
        multiple = Integer(0, group_with_commas=False).set_color(BLUE_B)
        multiple.add_updater(lambda m: m.set_value(int(multiple_value.get_value())).next_to(phone_number, DOWN).align_to(phone_number, RIGHT))
        times_symbol = Tex(R"\times").next_to(phone_number, LEFT, buff=0.3).match_y(multiple)
        equals_symbol = Line().set_width(VGroup(times_symbol, multiple).get_width() * 1.1).next_to(VGroup(times_symbol, multiple), DOWN)
        result = Integer(0, group_with_commas=False).next_to(equals_symbol, DOWN).set_color(YELLOW)
        result.add_updater(lambda r: r.set_value(self.n * int(multiple_value.get_value())).align_to(phone_number, RIGHT))
        multiplication_group = VGroup(phone_number, times_symbol, multiple, equals_symbol, result)
        multiplication_group.scale(1.1).center()

        digit_positions = [d.get_x() for d in phone_number]
        phone_number.set_opacity(0)
        self.add(phone_number)
        for i in range(1, len(phone_number) + 1):
            for j, d in enumerate(phone_number[:i][::-1]):
                d.set_x(digit_positions[-(j + 1)])
                d.set_opacity(1)
            self.wait(0.1)
        self.wait(0.7)

        self.play(
            AnimationGroup(
                GrowFromCenter(times_symbol),
                FadeIn(multiple),
                ShowCreation(equals_symbol),
                FadeIn(result, run_time=0.7),
                lag_ratio=0.4
            )
        )

        # Set the multiple to its target value
        self.play(multiple_value.animate(rate_func=linear).set_value(self.k), run_time=5)

        self.wait(2)


class Example1(PhoneNumberScene):
    n = 7299270073
    k = 10

    def construct(self):
        super().construct()


class Example2(PhoneNumberScene):
    n = 7299270073
    k = 137

    def construct(self):
        super().construct()


class Example3(PhoneNumberScene):
    n = 2849002849
    k = 39

    def construct(self):
        super().construct()
