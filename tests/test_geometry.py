"""Layout geometry tests — these lock in the small-terminal safety the original lacked."""

from __future__ import annotations

from wififorge.tui import geometry

BANNER_H = 10


def test_tiny_terminal_flagged_too_small():
    layout = geometry.compute(20, 6, BANNER_H)
    assert layout.too_small


def test_normal_terminal_is_two_column_with_banner():
    layout = geometry.compute(100, 40, BANNER_H)
    assert not layout.too_small
    assert layout.show_banner
    # Two boxes side by side, not overlapping.
    assert layout.detail_box.x >= layout.list_box.right


def test_narrow_terminal_drops_to_single_column():
    layout = geometry.compute(60, 30, BANNER_H)
    assert not layout.too_small
    # Detail sits below the list (single column), sharing the x origin.
    assert layout.detail_box.y >= layout.list_box.bottom
    assert layout.list_box.x == layout.detail_box.x


def test_short_terminal_hides_banner():
    layout = geometry.compute(100, 18, BANNER_H)
    assert not layout.show_banner


def test_narrow_terminal_hides_banner_even_if_tall():
    layout = geometry.compute(50, 40, BANNER_H)
    assert not layout.show_banner


def test_no_negative_dimensions_across_a_sweep():
    for w in range(10, 160, 7):
        for h in range(4, 60, 5):
            layout = geometry.compute(w, h, BANNER_H)
            for rect in (layout.list_box, layout.detail_box):
                assert rect.w >= 0 and rect.h >= 0
                assert rect.inner_w >= 0 and rect.inner_h >= 0
