"""
Pytest fixtures for rigorous and real-world tests.
"""
import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_workspace():
    """Real temp directory as workspace_root with a few files (real-world layout)."""
    with tempfile.TemporaryDirectory(prefix="agent_test_") as d:
        root = Path(d)
        # Realistic layout
        (root / "README.md").write_text("# Test Project\n\nA habit tracker.", encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "main.py").write_text(
            "def hello():\n    print('hello')\n    # TODO: add tests\n",
            encoding="utf-8",
        )
        (root / "src" / "utils.py").write_text(
            "def add(a, b):\n    return a + b\n",
            encoding="utf-8",
        )
        (root / "package.json").write_text('{"name": "test-app"}\n', encoding="utf-8")
        sub = root / "sub"
        sub.mkdir()
        (sub / "deep.txt").write_text("deep file\n", encoding="utf-8")
        yield str(root)


@pytest.fixture
def agent_context(tmp_workspace):
    """Context dict with workspace_root set to tmp_workspace."""
    return {"workspace_root": tmp_workspace}
