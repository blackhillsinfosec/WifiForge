"""Centralised styling.

Every colour and emphasis decision in the UI goes through a :class:`Theme` so the
look is consistent and can degrade gracefully on terminals with few (or no)
colours. Nothing else in the codebase calls ``term.red`` / ``term.bold`` directly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from blessed import Terminal

Style = Callable[[str], str]


def _identity(text: str) -> str:
    return text


class Theme:
    """A palette bound to a live terminal.

    On truecolor/256-colour terminals this uses RGB for a refined BHIS-flavoured
    red/amber scheme; on 8/16-colour terminals it falls back to the nearest named
    attribute; with no colour it falls back to bold/dim/reverse only.
    """

    accent: Style
    primary: Style
    secondary: Style
    good: Style
    muted: Style
    bold: Style
    _dim_rgb: Style
    _sel_bg: Style
    _card_bg: Style

    def __init__(self, term: Terminal) -> None:
        self.term = term
        colours = term.number_of_colors or 0

        if colours >= 256:
            self.accent = self._rgb(0xE6, 0x3A, 0x3A)      # signal red
            self.primary = self._rgb(0xF2, 0xF2, 0xF2)     # near-white
            self.secondary = self._rgb(0xF0, 0x9A, 0x3E)   # amber
            self.good = self._rgb(0x5C, 0xD6, 0x7A)        # green
            self.muted = self._rgb(0x8A, 0x8A, 0x8A)       # grey
            self._dim_rgb = self._rgb(0x5A, 0x5A, 0x5A)
            self._sel_bg = term.on_color_rgb(0x3A, 0x12, 0x12)
            self._card_bg = term.on_color_rgb(0x18, 0x18, 0x1C)
        elif colours >= 8:
            self.accent = term.bright_red
            self.primary = term.bright_white
            self.secondary = term.yellow
            self.good = term.green
            self.muted = term.white
            self._dim_rgb = term.bright_black
            self._sel_bg = term.on_red
            self._card_bg = _identity
        else:
            self.accent = term.bold
            self.primary = term.bold
            self.secondary = _identity
            self.good = _identity
            self.muted = _identity
            self._dim_rgb = term.dim if term.does_styling else _identity
            self._sel_bg = term.reverse
            self._card_bg = _identity

        self.bold = term.bold if term.does_styling else _identity

    # -- compositional helpers -------------------------------------------------
    def _rgb(self, r: int, g: int, b: int) -> Style:
        colour = self.term.color_rgb(r, g, b)
        return lambda text: colour(text)

    def dim(self, text: str) -> str:
        return self._dim_rgb(text)

    def selected(self, text: str) -> str:
        """A full-width highlight bar for the focused row."""
        return self._sel_bg(self.accent(self.bold(text)))

    def card(self, text: str) -> str:
        return self._card_bg(text)

    def title(self, text: str) -> str:
        return self.bold(self.primary(text))
