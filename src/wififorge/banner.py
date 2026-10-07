"""ASCII banner rendering.

The logo is stored cleanly (no literal escape sequences like the original) and
coloured at render time through the active :class:`~wififorge.theme.Theme`, so it
adapts to the terminal's real colour support. The compact wordmark keeps the
banner short enough to coexist with the menu on an ordinary 80x24 terminal.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blessed import Terminal

    from .theme import Theme

# A small signal-strength flourish shown above the wordmark.
_WAVE = "▁ ▃ ▅ ▇ █ ▇ ▅ ▃ ▁"

# Clean "WifiForge" wordmark (figlet "ANSI Shadow"). Block glyphs are drawn in the
# accent colour and the shadow glyphs dimmed, at render time.
_WORDMARK = [
    '██╗    ██╗██╗███████╗██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗',
    '██║    ██║██║██╔════╝██║██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝',
    '██║ █╗ ██║██║█████╗  ██║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗  ',
    '██║███╗██║██║██╔══╝  ██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  ',
    '╚███╔███╔╝██║██║     ██║██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗',
    ' ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝'
]

_TAGLINE = "forge wireless attacks in a safe, legal sandbox"

_SHADOW_CHARS = set("╔╗╚╝═║╠╣╦╩╬")


def banner_lines() -> list[str]:
    """Return the full banner (wave + wordmark + tagline) as plain lines."""
    return [_WAVE, "", *_WORDMARK, "", _TAGLINE]


def banner_height() -> int:
    return len(banner_lines())


def banner_width() -> int:
    return max(len(line) for line in banner_lines())


def render_banner(term: Terminal, theme: Theme, top: int = 0) -> list[str]:
    """Produce absolute-positioned, coloured banner rows centred in the terminal."""
    out: list[str] = []
    width = term.width or 80
    lines = banner_lines()
    tagline_index = len(lines) - 1
    for i, line in enumerate(lines):
        col = max((width - len(line)) // 2, 0)
        out.append(term.move_xy(col, top + i) + _colour_line(theme, line, i, tagline_index))
    return out


def _colour_line(theme: Theme, line: str, index: int, tagline_index: int) -> str:
    if index == 0:  # the signal wave
        return theme.accent(line)
    if index == tagline_index:
        return theme.dim(line)
    # Wordmark: accent the solid blocks, dim the drop-shadow glyphs.
    out = []
    for ch in line:
        if ch == "█":
            out.append(theme.accent(ch))
        elif ch in _SHADOW_CHARS:
            out.append(theme.dim(ch))
        else:
            out.append(ch)
    return "".join(out)
