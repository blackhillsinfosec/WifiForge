"""Layout arithmetic for the menu, kept separate so it can be unit-tested.

The original drew everything with raw coordinate math and no bounds checks, so a
narrow terminal produced negative widths and corrupted output. Everything here
clamps to safe minimums and degrades predictably.
"""

from __future__ import annotations

from dataclasses import dataclass

# Below these sizes we stop drawing chrome and show a plain message instead.
MIN_WIDTH = 40
MIN_HEIGHT = 10

# Thresholds at which we drop features to fit.
BANNER_MIN_HEIGHT = 22
BANNER_MIN_WIDTH = 72
# Rows the lab list must keep below the banner; otherwise the banner is dropped.
MIN_LIST_ROWS = 12
TWO_COLUMN_MIN_WIDTH = 72


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h

    @property
    def inner_w(self) -> int:
        """Width available inside a 1-char border."""
        return max(self.w - 2, 0)

    @property
    def inner_h(self) -> int:
        return max(self.h - 2, 0)


@dataclass(frozen=True)
class Layout:
    too_small: bool
    show_banner: bool
    banner_top: int
    list_box: Rect
    detail_box: Rect
    footer_y: int


def compute(width: int, height: int, banner_height: int) -> Layout:
    """Produce a :class:`Layout` for a terminal of the given size."""
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return Layout(
            too_small=True,
            show_banner=False,
            banner_top=0,
            list_box=Rect(0, 0, 0, 0),
            detail_box=Rect(0, 0, 0, 0),
            footer_y=max(height - 1, 0),
        )

    # Hide the banner when it wouldn't fit cleanly (too short or too narrow),
    # giving the lab list the reclaimed rows instead.
    show_banner = (
        width >= BANNER_MIN_WIDTH
        and height >= max(BANNER_MIN_HEIGHT, banner_height + MIN_LIST_ROWS + 2)
    )
    top = (banner_height + 1) if show_banner else 1

    footer_y = height - 1
    body_top = top
    body_h = max(footer_y - body_top - 1, MIN_HEIGHT - 2)

    two_col = width >= TWO_COLUMN_MIN_WIDTH
    outer_margin = 2
    usable_w = width - outer_margin * 2

    if two_col:
        gap = 2
        list_w = max(min(34, usable_w // 2), 24)
        detail_w = usable_w - list_w - gap
        list_box = Rect(outer_margin, body_top, list_w, body_h)
        detail_box = Rect(outer_margin + list_w + gap, body_top, detail_w, body_h)
    else:
        # Single column: list on top, a short detail strip beneath.
        detail_h = min(7, max(body_h // 3, 4))
        list_h = body_h - detail_h
        list_box = Rect(outer_margin, body_top, usable_w, list_h)
        detail_box = Rect(outer_margin, body_top + list_h, usable_w, detail_h)

    return Layout(
        too_small=False,
        show_banner=show_banner,
        banner_top=0,
        list_box=list_box,
        detail_box=detail_box,
        footer_y=footer_y,
    )
