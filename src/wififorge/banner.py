"""ASCII banner rendering.

The original WifiForge logo (router + wordmark + "By BHIS" credit) is stored
cleanly here: instead of literal ANSI escape sequences, the parts that used to
be red are wrapped in ``{`` ``}`` markers, which are stripped at import time and
turned into colour at render time. That way the art adapts to the terminal's
real colour support and the column math is never thrown off by invisible
escape bytes.

The full logo is 27 rows tall. On terminals too short for it, the menu falls
back to the compact form (just the wordmark and credit) or hides the banner.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blessed import Terminal

    from .theme import Theme

_HL_OPEN, _HL_CLOSE = "{", "}"

# The router / antenna. Text inside {braces} is drawn in red.
_ROUTER = [
    "                                  ██████████",
    "                             ████████████████████",
    "                          ██████████████████████████",
    "                       ████████████████████████████████",
    "                     ███████████████████████████████████",
    "                    █████████████████████████████████████",
    "                    00 ███████                 ███████ 00",
    "                    11 0 ██    ███████████████    ██ 0 11",
    "                    00 1  0 █████████████████████ 0  1 00",
    "                    11 0  1 █████████████████████ 1  0 11",
    "                    00 1  0 0 ██████     ██████ 0 0  1 00",
    "                    11 0      1 0 1  {███}  1 0 1      0 11",
    "                       1      0 1 0 {█████} 0 1 0      1",
    "                       0      1 0   {1███1}   0 1      0",
    "                                1   {0 1 0}   1",
    "                                    {1 0 1}",
    "                                    {0 1 0}",
    "                                    {1 0 1}",
    "                                      {1}",
]

# The original "WifiForge" wordmark. Solid blocks take the theme accent and the
# drop-shadow glyphs are dimmed.
_WORDMARK = [
    "    ██╗       ██╗██╗███████╗██╗  ███████╗ █████╗ ██████╗  ██████╗ ███████╗",
    "    ██║  ██╗  ██║██║██╔════╝██║  ██╔════╝██╔══██╗██╔══██╗██╔════╝ ██╔════╝",
    "    ╚██╗████╗██╔╝██║█████╗  ██║  █████╗  ██║  ██║██████╔╝██║  ██╗ █████╗",
    "     ████╔═████║ ██║██╔══╝  ██║  ██╔══╝  ██║  ██║██╔══██╗██║  ╚██╗██╔══╝",
    "      ██╔╝ ╚██╔╝ ██║██║     ██║  ██║     ╚█████╔╝██║  ██║╚██████╔╝███████╗",
    "      ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝      ╚════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝",
]

_BYLINE = "            {By BHIS}"

_SOURCE = [*_ROUTER, "", *_WORDMARK, _BYLINE]
_WORDMARK_ROWS = range(len(_ROUTER) + 1, len(_ROUTER) + 1 + len(_WORDMARK))

_SHADOW_CHARS = set("╔╗╚╝═║╠╣╦╩╬")


def _parse(src: list[str]) -> tuple[list[str], list[list[tuple[int, int]]]]:
    """Strip highlight markers, returning plain lines plus red column spans.

    The common left indent is removed so the logo can be centred as one block.
    """
    lines: list[str] = []
    spans: list[list[tuple[int, int]]] = []
    for raw in src:
        plain: list[str] = []
        row_spans: list[tuple[int, int]] = []
        start = 0
        for ch in raw:
            if ch == _HL_OPEN:
                start = len(plain)
            elif ch == _HL_CLOSE:
                row_spans.append((start, len(plain)))
            else:
                plain.append(ch)
        lines.append("".join(plain).rstrip())
        spans.append(row_spans)

    indent = min((len(ln) - len(ln.lstrip()) for ln in lines if ln.strip()), default=0)
    lines = [ln[indent:] for ln in lines]
    spans = [[(a - indent, b - indent) for a, b in row] for row in spans]
    return lines, spans


_LINES, _SPANS = _parse(_SOURCE)


# Row indices (into _LINES) for the compact form: wordmark + credit only.
_COMPACT_ROWS = [*_WORDMARK_ROWS, len(_LINES) - 1]


def _rows(compact: bool) -> list[int]:
    return _COMPACT_ROWS if compact else list(range(len(_LINES)))


def banner_lines(compact: bool = False) -> list[str]:
    """Return the banner as plain (uncoloured) lines."""
    return [_LINES[i] for i in _rows(compact)]


def banner_height(compact: bool = False) -> int:
    return len(_rows(compact))


def banner_width(compact: bool = False) -> int:
    return max(len(line) for line in banner_lines(compact))


def render_banner(
    term: Terminal, theme: Theme, top: int = 0, compact: bool = False
) -> list[str]:
    """Produce absolute-positioned, coloured banner rows centred in the terminal.

    The logo is centred as a single block (not line by line) so the router art
    keeps its shape.
    """
    width = term.width or 80
    col = max((width - banner_width(compact)) // 2, 0)
    return [
        term.move_xy(col, top + row) + _colour_line(term, theme, i, _LINES[i])
        for row, i in enumerate(_rows(compact))
    ]


def _colour_line(term: Terminal, theme: Theme, index: int, line: str) -> str:
    spans = _SPANS[index]
    in_wordmark = index in _WORDMARK_ROWS
    out: list[str] = []
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
        elif any(a <= x < b for a, b in spans):
            # blessed returns an empty formatter on colourless terminals,
            # so this degrades to plain text automatically.
            out.append(term.red(ch))
        elif in_wordmark and ch == "█":
            out.append(theme.accent(ch))
        elif in_wordmark and ch in _SHADOW_CHARS:
            out.append(theme.dim(ch))
        else:
            out.append(ch)
    return "".join(out)
