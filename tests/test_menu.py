"""Menu rendering and interaction tests.

The menu's :meth:`render` is a pure function of state + size, so we can assert on
its output without a real terminal. A forced-styling blessed Terminal gives us
positioning codes without needing a TTY.
"""

from __future__ import annotations

import re

import pytest
from blessed import Terminal

from wififorge.labs.loader import discover
from wififorge.tui import Menu

SGR = re.compile(r"\x1b\[[0-9;]*m")
CSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


@pytest.fixture
def menu():
    return Menu(term=Terminal(force_styling=True), labs=discover())


def plain(text: str) -> str:
    """Strip all escape sequences to get the visible characters."""
    return CSI.sub("", SGR.sub("", text))


@pytest.mark.parametrize("w,h", [(100, 40), (80, 30), (72, 24), (60, 20), (45, 12), (30, 8)])
def test_render_never_crashes(menu, w, h):
    out = menu.render(w, h)
    assert isinstance(out, str)


def test_render_shows_labs_and_footer(menu):
    text = plain(menu.render(100, 40))
    assert "Evil Twin" in text
    assert "ATTACK" in text          # category header
    assert "navigate" in text        # footer hint
    assert "v" in text and "labs" in text


def test_tiny_terminal_shows_message(menu):
    text = plain(menu.render(20, 6))
    assert "too small" in text.lower()


def test_search_filters_labs(menu):
    menu.searching = True
    menu.query = "wpa"
    titles = {lab.meta.title for lab in menu.visible_labs()}
    assert titles  # non-empty
    assert all(
        "wpa" in " ".join([lab.meta.title, lab.meta.summary, *lab.meta.tools]).lower()
        for lab in menu.visible_labs()
    )


def test_search_with_no_match_is_empty(menu):
    menu.query = "zzzznotathing"
    assert menu.visible_labs() == []
    # And rendering an empty result must not crash.
    assert isinstance(menu.render(100, 40), str)


def test_selection_clamps_within_bounds(menu):
    menu.selected = 999
    menu._clamp_selection()
    assert menu.selected == len(menu.visible_labs()) - 1
    menu.selected = -5
    menu._clamp_selection()
    assert menu.selected == 0


class _FakeKey(str):
    """Mimic blessed's keystroke: a str subclass carrying a .code / .is_sequence."""

    def __new__(cls, value="", code=None, is_sequence=False):
        obj = super().__new__(cls, value)
        obj.code = code
        obj.is_sequence = is_sequence
        return obj


def test_arrow_navigation(menu):
    term = menu.term
    start = menu.selected
    menu._handle_key(_FakeKey(code=term.KEY_DOWN, is_sequence=True), on_launch=lambda lab: None)
    assert menu.selected == start + 1
    menu._handle_key(_FakeKey(code=term.KEY_UP, is_sequence=True), on_launch=lambda lab: None)
    assert menu.selected == start


def test_slash_enters_search_and_q_quits(menu):
    term = menu.term
    menu._handle_key(_FakeKey("/"), on_launch=lambda lab: None)
    assert menu.searching
    # Typing narrows; Esc clears.
    menu._handle_key(_FakeKey("e"), on_launch=lambda lab: None)
    assert menu.query == "e"
    menu._handle_key(_FakeKey(code=term.KEY_ESCAPE, is_sequence=True), on_launch=lambda lab: None)
    assert not menu.searching and menu.query == ""
    # q quits.
    assert menu._handle_key(_FakeKey("q"), on_launch=lambda lab: None) is True


def test_enter_launches_selected_lab(menu):
    launched = []
    key = _FakeKey("\n")
    menu._handle_key(key, on_launch=launched.append)
    assert len(launched) == 1
    assert launched[0] is menu.visible_labs()[menu.selected]
