"""Reusable drawing primitives: rounded boxes, badges, truncation, wrapping.

Rendering functions return lists of ``(y, x, text)`` cells (already colour-wrapped)
so the menu can blit them in one pass. Width maths is always done on *plain* text;
colour is applied last, so styling never throws the layout off.
"""

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

from .geometry import Rect

if TYPE_CHECKING:
    from blessed import Terminal

    from ..theme import Theme

Cell = tuple[int, int, str]

# Rounded box glyphs.
TL, TR, BL, BR = "╭", "╮", "╰", "╯"
HZ, VT = "─", "│"


def truncate(text: str, width: int) -> str:
    """Hard-truncate ``text`` to ``width`` columns, adding an ellipsis if cut."""
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width == 1:
        return "…"
    return text[: width - 1] + "…"


def wrap(text: str, width: int) -> list[str]:
    if width <= 0:
        return []
    lines: list[str] = []
    for para in text.split("\n"):
        wrapped = textwrap.wrap(para, width=width) or [""]
        lines.extend(wrapped)
    return lines


def box(term: Terminal, theme: Theme, rect: Rect, title: str = "", *, focused: bool = False) -> list[Cell]:
    """Draw a rounded border with an optional embedded title."""
    cells: list[Cell] = []
    if rect.w < 2 or rect.h < 2:
        return cells

    border = theme.accent if focused else theme.dim
    inner = rect.w - 2

    # Top border with embedded title: ╭─ Title ─────╮
    if title:
        label = f" {truncate(title, max(inner - 4, 0))} "
        fill = max(inner - len(label) - 1, 0)
        top = border(TL + HZ) + theme.title(label) + border(HZ * fill + TR)
    else:
        top = border(TL + HZ * inner + TR)
    cells.append((rect.y, rect.x, top))

    for i in range(1, rect.h - 1):
        cells.append((rect.y + i, rect.x, border(VT)))
        cells.append((rect.y + i, rect.right - 1, border(VT)))

    cells.append((rect.bottom - 1, rect.x, border(BL + HZ * inner + BR)))
    return cells


def badge(theme: Theme, text: str) -> str:
    """A pill-style badge, e.g. ``hostapd``."""
    return theme.card(theme.secondary(f" {text} "))


def difficulty_meter(theme: Theme, dots: str) -> str:
    """Colour the filled dots accent, the empty dots dim."""
    out = []
    for ch in dots:
        out.append(theme.accent(ch) if ch == "●" else theme.dim(ch))
    return "".join(out)
