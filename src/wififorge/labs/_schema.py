"""Declarative metadata that each lab module exposes.

A lab module should define a module-level ``LAB`` and a ``run`` callable::

    from wififorge.labs._schema import LabMeta, Category, Difficulty

    LAB = LabMeta(
        title="Evil Twin",
        category=Category.ATTACK,
        difficulty=Difficulty.INTERMEDIATE,
        tools=("hostapd", "mininet-wifi"),
        summary="Stand up a rogue AP impersonating a real network...",
    )

    def run() -> None:
        ...

Declaring ``LAB``/``run`` removes the original "import every file and grab the
first function" guesswork. The loader still degrades gracefully (see
``loader.py``) for modules that only provide the legacy ``description`` string.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Category(str, Enum):
    RECON = "Recon"
    CAPTURE = "Capture"
    CRACKING = "Cracking"
    ATTACK = "Attack"
    PHISHING = "Phishing"
    MISC = "Misc"

    @property
    def order(self) -> int:
        return list(Category).index(self)


class Difficulty(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

    @property
    def dots(self) -> str:
        """A compact ``●●○`` difficulty meter."""
        level = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}[self.value]
        return "●" * level + "○" * (3 - level)


@dataclass(frozen=True)
class LabMeta:
    title: str
    summary: str
    category: Category = Category.MISC
    difficulty: Difficulty = Difficulty.INTERMEDIATE
    tools: tuple[str, ...] = field(default_factory=tuple)


# Keyword -> category inference, used only when a lab doesn't declare its own.
_CATEGORY_HINTS: tuple[tuple[str, Category], ...] = (
    ("recon", Category.RECON),
    ("capture", Category.CAPTURE),
    ("crack", Category.CRACKING),
    ("hashcat", Category.CRACKING),
    ("john", Category.CRACKING),
    ("phish", Category.PHISHING),
    ("evil", Category.ATTACK),
    ("dos", Category.ATTACK),
    ("attack", Category.ATTACK),
    ("pixie", Category.ATTACK),
    ("wep", Category.ATTACK),
    ("drone", Category.MISC),
)


def humanize(stem: str) -> str:
    """Turn ``packet_capture_to_HCCAPX_hashcat_cracking`` into a readable title.

    Fixes the original's ``.title()`` which mangled acronyms into ``Hccapx`` and
    ``Wpa``. Known acronyms are upper-cased; everything else is title-cased.
    """
    acronyms = {
        "wpa", "wpa2", "wep", "wps", "ntlm", "dos", "ap", "hccapx",
        "hcx", "pmkid", "ssid", "mac", "wifi",
    }
    words = stem.replace("-", "_").split("_")
    out = []
    for w in words:
        out.append(w.upper() if w.lower() in acronyms else w.capitalize())
    return " ".join(out)


def infer_category(stem: str) -> Category:
    low = stem.lower()
    for needle, cat in _CATEGORY_HINTS:
        if needle in low:
            return cat
    return Category.MISC
