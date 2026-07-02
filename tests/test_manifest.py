"""Manifest contract tests for the standalone plugin-interview repo.

These run without Luna core installed — they only parse the TOML and the package
tree, asserting the published shape stays in sync.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "plugin_interview"
MANIFEST = tomllib.loads((PKG / "luna-plugin.toml").read_text())


def test_identity():
    assert MANIFEST["name"] == "plugin-interview"
    assert MANIFEST["entry"] == "plugin_interview"
    assert MANIFEST["sdk_version"] == "0"
    assert MANIFEST["license"] == "MIT"
    assert MANIFEST["category"] == "global"


def test_tool_and_table_counts():
    assert MANIFEST["requires"]["tools"] == 9
    assert len(MANIFEST["tools"]) == 9
    assert MANIFEST["requires"]["tables"] == 4
    assert len(MANIFEST["db_tables"]) == 4


def test_db_table_names():
    assert set(MANIFEST["db_tables"]) == {
        "plugin_interview_sessions",
        "plugin_interview_topics",
        "plugin_interview_turns",
        "plugin_interview_meta",
    }


def test_no_core_imports():
    offenders = []
    for py in PKG.rglob("*.py"):
        for line in py.read_text().splitlines():
            s = line.strip()
            if s.startswith(("import luna", "from luna")) and "luna_sdk" not in s:
                offenders.append(f"{py.name}: {s}")
    assert not offenders, offenders


def test_ships_sidebar_pane():
    assert (PKG / "ui" / "index.html").exists()
    assert (PKG / "ui" / "app.js").exists()
    assert (PKG / "ui" / "style.css").exists()
    # The old in-tree settings tab must be gone.
    assert not (PKG / "interface" / "webui" / "SettingsTab.tsx").exists()
