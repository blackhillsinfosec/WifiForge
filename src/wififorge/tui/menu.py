"""The WifiForge main menu.

A categorised, searchable, scrolling lab browser with a live detail card. The
drawing is a pure function of ``(state, width, height)`` so it can be rendered to
a string and tested headlessly; only :meth:`Menu.run` touches the live terminal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .. import __version__
from ..banner import banner_height, render_banner
from ..labs.loader import Lab
from ..theme import Theme
from . import geometry
from .widgets import Cell, badge, box, difficulty_meter, truncate, wrap


@dataclass
class _Row:
    kind: str                 # "header" | "lab"
    text: str                 # header label (for headers)
    lab: Lab | None = None
    lab_index: int = -1       # index into the visible-labs list


@dataclass
class Menu:
    term: Any
    labs: list[Lab]
    theme: Theme = field(init=False)
    selected: int = 0
    scroll: int = 0
    searching: bool = False
    query: str = ""

    def __post_init__(self) -> None:
        self.theme = Theme(self.term)

    # -- state ----------------------------------------------------------------
    def visible_labs(self) -> list[Lab]:
        if not self.query:
            return self.labs
        q = self.query.lower()
        out = []
        for lab in self.labs:
            haystack = " ".join(
                [lab.meta.title, lab.meta.category.value, lab.meta.summary, *lab.meta.tools]
            ).lower()
            if q in haystack:
                out.append(lab)
        return out

    def _rows(self, labs: list[Lab]) -> list[_Row]:
        rows: list[_Row] = []
        last_cat = None
        for i, lab in enumerate(labs):
            cat = lab.meta.category.value
            if cat != last_cat:
                rows.append(_Row(kind="header", text=cat))
                last_cat = cat
            rows.append(_Row(kind="lab", text=lab.meta.title, lab=lab, lab_index=i))
        return rows

    def _clamp_selection(self) -> None:
        n = len(self.visible_labs())
        if n == 0:
            self.selected = 0
        else:
            self.selected = max(0, min(self.selected, n - 1))

    # -- rendering (pure) -----------------------------------------------------
    def render(self, width: int | None = None, height: int | None = None) -> str:
        term, theme = self.term, self.theme
        width = width if width is not None else (term.width or 80)
        height = height if height is not None else (term.height or 24)

        layout = geometry.compute(width, height, banner_height())
        parts: list[str] = [term.home + term.clear]

        if layout.too_small:
            msg = truncate("Terminal too small — enlarge the window.", width)
            parts.append(term.move_xy(0, max(height // 2, 0)) + theme.accent(msg))
            return "".join(parts)

        if layout.show_banner:
            parts.extend(render_banner(term, theme, top=layout.banner_top))

        labs = self.visible_labs()
        self._clamp_selection()

        parts.extend(self._emit_cells(self._render_list(layout, labs)))
        parts.extend(self._emit_cells(self._render_detail(layout, labs)))
        parts.append(self._render_footer(width, layout, labs))
        return "".join(parts)

    def _emit_cells(self, cells: list[Cell]) -> list[str]:
        return [self.term.move_xy(x, y) + text for (y, x, text) in cells]

    def _render_list(self, layout: geometry.Layout, labs: list[Lab]) -> list[Cell]:
        theme = self.theme
        rect = layout.list_box
        cells = box(self.term, theme, rect, "Labs", focused=not self.searching)
        inner_w = rect.inner_w
        inner_h = rect.inner_h
        if inner_w <= 0 or inner_h <= 0:
            return cells

        rows = self._rows(labs)
        if not rows:
            cells.append((rect.y + 1, rect.x + 2, theme.dim(truncate("No matching labs", inner_w))))
            return cells

        sel_row = next((i for i, r in enumerate(rows) if r.lab_index == self.selected and r.kind == "lab"), 0)
        self.scroll = _scroll_to(self.scroll, sel_row, inner_h, len(rows))

        visible = rows[self.scroll : self.scroll + inner_h]
        for i, row in enumerate(visible):
            y = rect.y + 1 + i
            x = rect.x + 1
            if row.kind == "header":
                label = truncate(row.text.upper(), inner_w - 1)
                cells.append((y, x, " " + theme.dim(theme.bold(label))))
                continue

            is_sel = row.lab_index == self.selected
            lab = row.lab
            assert lab is not None
            marker = "›" if is_sel else " "
            dots = lab.meta.difficulty.dots
            title_room = inner_w - 4 - len(dots) - 1
            title = truncate(lab.meta.title, max(title_room, 1))
            left = f" {marker} {title}"
            pad = inner_w - len(left) - len(dots) - 1
            line_plain = left + " " * max(pad, 1) + dots + " "

            if is_sel:
                cells.append((y, x, theme.selected(line_plain)))
            else:
                styled = (
                    theme.accent(f" {marker} ")
                    + (theme.muted if not lab.available else theme.primary)(title)
                    + " " * max(pad, 1)
                    + difficulty_meter(theme, dots)
                    + " "
                )
                cells.append((y, x, styled))

        # Scroll hint.
        if len(rows) > inner_h:
            pct = (self.scroll) / max(len(rows) - inner_h, 1)
            knob_y = rect.y + 1 + int(pct * (inner_h - 1))
            cells.append((knob_y, rect.right - 1, theme.accent("│")))
        return cells

    def _render_detail(self, layout: geometry.Layout, labs: list[Lab]) -> list[Cell]:
        theme = self.theme
        rect = layout.detail_box
        if not labs:
            cells = box(self.term, theme, rect, "Details", focused=False)
            return cells

        lab = labs[self.selected]
        cells = box(self.term, theme, rect, lab.meta.title, focused=False)
        inner_w = rect.inner_w
        inner_h = rect.inner_h
        if inner_w <= 0 or inner_h <= 0:
            return cells

        x = rect.x + 2
        y = rect.y + 1

        # Meta line: Category · ●●○ Difficulty
        meta = lab.meta
        meta_line = (
            theme.secondary(meta.category.value)
            + theme.dim(" · ")
            + difficulty_meter(theme, meta.difficulty.dots)
            + " "
            + theme.dim(meta.difficulty.value)
        )
        cells.append((y, x, meta_line))
        y += 2

        if lab.error:
            for ln in wrap(f"Failed to load: {lab.error}", inner_w - 2):
                if y >= rect.bottom - 1:
                    break
                cells.append((y, x, theme.accent(truncate(ln, inner_w - 2))))
                y += 1
            return cells

        # Summary.
        for ln in wrap(meta.summary, inner_w - 2):
            if y >= rect.bottom - 3:
                break
            cells.append((y, x, theme.primary(ln)))
            y += 1

        # Tools as badges.
        if meta.tools and y < rect.bottom - 2:
            y += 1
            cells.append((y, x, theme.dim(theme.bold("TOOLS"))))
            y += 1
            line = ""
            plain_len = 0
            for tool in meta.tools:
                chunk_plain = f" {tool} "
                if plain_len + len(chunk_plain) + 1 > inner_w - 2 and line:
                    cells.append((y, x, line))
                    y += 1
                    line, plain_len = "", 0
                    if y >= rect.bottom - 1:
                        break
                line += badge(theme, tool) + " "
                plain_len += len(chunk_plain) + 1
            if line and y < rect.bottom - 1:
                cells.append((y, x, line))
        return cells

    def _render_footer(self, width: int, layout: geometry.Layout, labs: list[Lab]) -> str:
        theme = self.theme
        y = layout.footer_y

        def key(k: str, label: str) -> str:
            return theme.accent(k) + theme.dim(" " + label)

        if self.searching:
            cursor = theme.accent("▏")
            left = theme.dim("search ") + theme.primary("/" + self.query) + cursor + "   " + key("esc", "clear")
            left_plain_len = len("search /" + self.query) + 1 + 3 + len("esc clear")
        else:
            hints = [key("↑↓", "navigate"), key("↵", "launch"), key("/", "search"), key("q", "quit")]
            left = theme.dim("   ").join(hints)
            left_plain_len = sum(len(h) for h in ("↑↓ navigate", "↵ launch", "/ search", "q quit")) + 3 * 3

        right_plain = f"{len(labs)} labs · v{__version__}"
        right = theme.dim(right_plain)
        gap = max(width - left_plain_len - len(right_plain) - 4, 1)
        return self.term.move_xy(2, y) + left + " " * gap + right

    # -- interaction ----------------------------------------------------------
    def run(self, on_launch: Callable[[Lab], None]) -> None:
        """Interactive loop. Calls ``on_launch(lab)`` when the user hits Enter."""
        term = self.term
        with term.cbreak(), term.fullscreen(), term.hidden_cursor():
            while True:
                print(self.render(), end="", flush=True)
                key = term.inkey()
                if self._handle_key(key, on_launch):
                    return

    def _handle_key(self, key: Any, on_launch: Callable[[Lab], None]) -> bool:
        """Process one keypress. Returns True to quit."""
        term = self.term
        labs = self.visible_labs()

        # Navigation shared by both modes.
        if key.code == term.KEY_UP or key == "k":
            self.selected -= 1
        elif key.code == term.KEY_DOWN or key == "j":
            self.selected += 1
        elif key.code == term.KEY_PGUP:
            self.selected -= 5
        elif key.code == term.KEY_PGDOWN:
            self.selected += 5
        elif key.code == term.KEY_HOME:
            self.selected = 0
        elif key.code == term.KEY_END:
            self.selected = len(labs) - 1
        elif key.code in (term.KEY_ENTER,) or key in ("\n", "\r"):
            if labs:
                lab = labs[self.selected]
                if lab.available:
                    on_launch(lab)
        elif self.searching:
            if key.code == term.KEY_ESCAPE:
                self.searching = False
                self.query = ""
            elif key.code == term.KEY_BACKSPACE:
                self.query = self.query[:-1]
            elif not key.is_sequence and key.isprintable():
                self.query += str(key)
                self.selected = 0
        else:
            if key == "/":
                self.searching = True
                self.query = ""
            elif key in ("q", "Q") or key.code == term.KEY_ESCAPE:
                return True

        self._clamp_selection()
        return False


def _scroll_to(current: int, target_row: int, viewport: int, total: int) -> int:
    """Keep ``target_row`` within the viewport, returning the new scroll offset."""
    if total <= viewport:
        return 0
    top = current
    if target_row < top:
        top = target_row
    elif target_row >= top + viewport:
        top = target_row - viewport + 1
    return max(0, min(top, total - viewport))
