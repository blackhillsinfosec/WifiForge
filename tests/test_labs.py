"""Lab discovery and metadata tests.

These run without mininet-wifi installed, which is the whole point of the lazy
``mn_wifi`` imports: the menu and tooling must work on any machine.
"""

from __future__ import annotations

from wififorge.labs import loader
from wififorge.labs._schema import Category, Difficulty, humanize, infer_category

EXPECTED_LABS = 12


def test_discovers_all_labs():
    labs = loader.discover()
    assert len(labs) == EXPECTED_LABS


def test_all_bundled_labs_load_cleanly():
    labs = loader.discover()
    broken = [(lab.key, lab.error) for lab in labs if not lab.available]
    assert broken == [], f"labs failed to import: {broken}"


def test_helper_modules_are_not_labs():
    # materials.py / loader.py / _schema.py must not be mistaken for labs.
    keys = {lab.key for lab in loader.discover()}
    assert "materials" not in keys
    assert "loader" not in keys
    assert "_schema" not in keys


def test_labs_sorted_by_category_then_title():
    labs = loader.discover()
    order = [(lab.meta.category.order, lab.meta.title.lower()) for lab in labs]
    assert order == sorted(order)


def test_every_lab_has_metadata():
    for lab in loader.discover():
        assert lab.meta.title
        assert lab.meta.summary
        assert isinstance(lab.meta.category, Category)
        assert isinstance(lab.meta.difficulty, Difficulty)


def test_difficulty_dots():
    assert Difficulty.BEGINNER.dots == "●○○"
    assert Difficulty.INTERMEDIATE.dots == "●●○"
    assert Difficulty.ADVANCED.dots == "●●●"


def test_humanize_preserves_acronyms():
    # The original .title() mangled these into "Wpa", "Hccapx", etc.
    assert humanize("cracking_WPA_with_aircrack") == "Cracking WPA With Aircrack"
    assert humanize("packet_capture_to_hccapx") == "Packet Capture To HCCAPX"
    assert humanize("ntlm_john_crack") == "NTLM John Crack"


def test_infer_category():
    assert infer_category("bettercap_recon") is Category.RECON
    assert infer_category("cracking_wpa") is Category.CRACKING
    assert infer_category("wifiphisher") is Category.PHISHING
    assert infer_category("something_unknown") is Category.MISC


def test_extra_labs_dir(tmp_path):
    # A user-supplied lab in an external directory should be discovered.
    lab_file = tmp_path / "my_custom_lab.py"
    lab_file.write_text(
        "from wififorge.labs._schema import LabMeta, Category, Difficulty\n"
        "LAB = LabMeta(title='Custom', summary='x', category=Category.MISC,\n"
        "              difficulty=Difficulty.BEGINNER)\n"
        "def run():\n    pass\n"
    )
    labs = loader.discover(extra_dir=tmp_path)
    assert any(lab.meta.title == "Custom" for lab in labs)


def test_broken_lab_is_isolated(tmp_path):
    # A lab with a bad import must not blow up discovery; it loads disabled.
    (tmp_path / "broken_lab.py").write_text("import nonexistent_module_xyz\n")
    labs = loader.discover(extra_dir=tmp_path)
    broken = [lab for lab in labs if lab.key == "broken_lab"]
    assert len(broken) == 1
    assert not broken[0].available
    assert broken[0].error
