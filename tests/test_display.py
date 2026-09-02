import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pihome import display as d


def test_every_shape_is_64_pixels():
    for name in d.SHAPES:
        assert len(d.shape(name)) == 64


def test_unknown_shape_lists_the_known_ones():
    with pytest.raises(KeyError) as excinfo:
        d.shape("banana")
    assert "heart" in str(excinfo.value)


def test_font_has_ten_digits_of_sixteen_pixels():
    assert len(d.DIGITS) == 10
    assert all(len(g) == 16 for g in d.DIGITS)


def test_every_digit_is_distinguishable_except_the_known_pair():
    """4x4 is tight; the archived font draws 8 solid. Everything else differs."""
    seen = {}
    for value, grid in enumerate(d.DIGITS):
        seen.setdefault(tuple(grid), []).append(value)
    collisions = [v for v in seen.values() if len(v) > 1]
    assert collisions == [], "digits render identically: {}".format(collisions)


def test_clock_renders_four_digits():
    assert len(d.clock_pixels(14, 37)) == 64


def test_clock_rejects_impossible_times():
    for hour, minute in ((24, 0), (-1, 0), (0, 60)):
        with pytest.raises(ValueError):
            d.clock_pixels(hour, minute)


def test_clamp_and_scale():
    assert d.clamp(50, 0, 40) == 40
    assert d.clamp(-5, 0, 40) == 0
    assert d.scale(20, 0, 40, 0, 8) == 4
    assert d.scale(5, 5, 5) == 0          # zero-width range must not divide by zero


def test_bars_draw_bottom_up():
    pixels = d.bar_pixels([(0, 2, 3, d.RED)])
    assert pixels[7 * 8] == d.RED         # bottom-left lit
    assert pixels[0] == d.OFF             # top-left dark


def test_bars_clip_rather_than_raise():
    assert len(d.bar_pixels([(6, 4, 99, d.RED)])) == 64


def test_reading_bars_rejects_too_many():
    with pytest.raises(ValueError):
        d.reading_bars([(1, 0, 2, d.RED)] * 4)


def test_rainbow_frame_is_64_distinct_ish_pixels():
    frame = d.rainbow_frame(0.0)
    assert len(frame) == 64
    assert len(set(frame)) > 8
