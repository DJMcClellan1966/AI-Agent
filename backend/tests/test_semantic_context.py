"""
Tests for optional semantic_context: behavior with and without sentence_transformers.
"""
import os
import tempfile
from pathlib import Path

import pytest

from app.services.semantic_context import get_semantic_snippets, format_semantic_block


@pytest.fixture
def small_workspace():
    """Minimal workspace with two text files."""
    with tempfile.TemporaryDirectory(prefix="semantic_test_") as d:
        root = Path(d)
        (root / "readme.md").write_text("This project is about authentication and login flow.", encoding="utf-8")
        (root / "auth.py").write_text("def login(user, password):\n    return verify(user, password)\n", encoding="utf-8")
        yield str(root)


def test_get_semantic_snippets_empty_query(small_workspace):
    out = get_semantic_snippets(small_workspace, "")
    assert out == []


def test_get_semantic_snippets_invalid_root():
    out = get_semantic_snippets("/nonexistent/path/12345", "auth")
    assert out == []


def test_get_semantic_snippets_returns_list(small_workspace):
    # Without sentence_transformers this returns []; with it returns (path, snippet, score)
    out = get_semantic_snippets(small_workspace, "authentication")
    assert isinstance(out, list)
    for item in out:
        assert len(item) == 3
        path, snippet, score = item
        assert isinstance(path, str)
        assert isinstance(snippet, str)
        assert isinstance(score, (int, float))


def test_format_semantic_block_empty_query(small_workspace):
    block = format_semantic_block(small_workspace, "")
    assert block == ""


def test_format_semantic_block_returns_string(small_workspace):
    block = format_semantic_block(small_workspace, "login", max_snippets=2)
    # With sentence_transformers: non-empty block with "Relevant snippets"
    # Without: ""
    assert isinstance(block, str)
    if block:
        assert "Relevant snippets" in block or "semantic" in block.lower()
