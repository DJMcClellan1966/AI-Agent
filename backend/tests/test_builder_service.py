"""
Tests for builder_service: JSON extraction, default spec, code parsing, summary, suggest_questions.
"""
import json
from unittest.mock import patch, MagicMock

import pytest

from app.services.builder_service import (
    _extract_json_object,
    _extract_json_array,
    _default_spec,
    _parse_code_blocks,
    build_conversation_summary,
    suggest_questions,
    spec_to_code,
    conversation_to_spec,
)


# --- _extract_json_object (completeness + edge cases) ---

def test_extract_json_object_simple():
    raw = '  {"a": 1}  '
    assert _extract_json_object(raw) == '{"a": 1}'


def test_extract_json_object_nested():
    raw = 'prefix {"x": {"y": [1,2]}} suffix'
    out = _extract_json_object(raw)
    assert out.startswith("{") and out.endswith("}")
    data = json.loads(out)
    assert data["x"]["y"] == [1, 2]


def test_extract_json_object_no_brace():
    assert _extract_json_object("no json here") == ""


def test_extract_json_object_markdown_wrapped():
    raw = '```json\n{"key": "value"}\n```'
    out = _extract_json_object(raw)
    assert json.loads(out)["key"] == "value"


def test_extract_json_object_balanced_braces():
    raw = '{"a": 1, "b": {"c": 2}} rest'
    out = _extract_json_object(raw)
    data = json.loads(out)
    assert data["b"]["c"] == 2


# --- _extract_json_array ---

def test_extract_json_array_simple():
    raw = '  ["a", "b"]  '
    out = _extract_json_array(raw)
    assert json.loads(out) == ["a", "b"]


def test_extract_json_array_nested():
    raw = 'before [1, [2, 3]] after'
    out = _extract_json_array(raw)
    assert json.loads(out) == [1, [2, 3]]


def test_extract_json_array_no_bracket():
    assert _extract_json_array("no array") == ""


# --- _default_spec (real-world keyword detection) ---

def test_default_spec_empty_messages():
    spec = _default_spec([])
    assert spec["name"] == "MyApp"
    assert spec["type"] == "app"
    assert "list management" in spec["features"] or "tracking" in spec["features"]


def test_default_spec_tracker_keywords():
    messages = [{"role": "user", "content": "I want a habit tracker with streaks"}]
    spec = _default_spec(messages)
    assert spec["type"] == "tracker"
    assert "tracking" in spec["features"] or "streaks" in spec["features"]


def test_default_spec_notes_keywords():
    messages = [{"role": "user", "content": "A notes app with tagging"}]
    spec = _default_spec(messages)
    assert spec["type"] == "notes"
    assert "categorization" in spec["features"] or "list management" in spec["features"]


def test_default_spec_name_from_first_message():
    messages = [{"role": "user", "content": "Build me a Reading Log app"}]
    spec = _default_spec(messages)
    assert "Reading" in spec["name"] or "Log" in spec["name"] or spec["name"] != "MyApp"


def test_default_spec_theme_light():
    messages = [{"role": "user", "content": "I want light mode"}]
    spec = _default_spec(messages)
    assert spec["theme"] == "light"


# --- _parse_code_blocks ---

def test_parse_code_blocks_empty():
    assert _parse_code_blocks("") == {}
    assert _parse_code_blocks("no blocks") == {}


def test_parse_code_blocks_all_three():
    raw = """===INDEX.HTML===
<!DOCTYPE html>
<html></html>
===STYLES.CSS===
body { margin: 0; }
===APP.JS===
console.log('hi');
===END==="""
    files = _parse_code_blocks(raw)
    assert "index.html" in files
    assert "styles.css" in files
    assert "app.js" in files
    assert "html" in files["index.html"]
    assert "margin" in files["styles.css"]
    assert "console" in files["app.js"]


# --- build_conversation_summary ---

def test_build_conversation_summary_empty():
    assert build_conversation_summary([]) == ""


def test_build_conversation_summary_truncates():
    messages = [{"role": "user", "content": "a" * 300}] * 10
    summary = build_conversation_summary(messages, max_len=100)
    assert len(summary) <= 100


def test_build_conversation_summary_includes_content():
    messages = [{"role": "user", "content": "Hello world"}]
    assert "Hello" in build_conversation_summary(messages)


# --- suggest_questions (template fallback when no LLM) ---

def test_suggest_questions_empty_messages():
    qs = suggest_questions([], max_questions=2)
    assert len(qs) <= 2
    assert all(isinstance(q, str) for q in qs)


def test_suggest_questions_template_tracker():
    messages = [{"role": "user", "content": "I want a habit tracker"}]
    with patch("app.services.builder_service._get_llm") as mock_llm:
        mock_llm.return_value = (None, None)
        qs = suggest_questions(messages, max_questions=2)
    assert len(qs) <= 2
    assert any("problem" in q.lower() or "who" in q.lower() or "session" in q.lower() for q in qs)


def test_suggest_questions_respects_max():
    messages = [{"role": "user", "content": "todo app"}]
    with patch("app.services.builder_service._get_llm") as mock_llm:
        mock_llm.return_value = (None, None)
        qs = suggest_questions(messages, max_questions=1)
    assert len(qs) == 1


# --- spec_to_code (template path when no LLM) ---

def test_spec_to_code_returns_three_files():
    spec = {"name": "TestApp", "type": "app", "features": ["tracking"], "persistence": "localStorage", "theme": "dark", "ui_complexity": "minimal"}
    with patch("app.services.builder_service._get_llm") as mock_llm:
        mock_llm.return_value = (None, None)
        files = spec_to_code(spec)
    assert "index.html" in files
    assert "styles.css" in files
    assert "app.js" in files
    assert "TestApp" in files["index.html"]
    assert "localStorage" in files["app.js"] or "APP_KEY" in files["app.js"]


# --- conversation_to_spec (default path when no LLM) ---

def test_conversation_to_spec_fallback_without_llm():
    messages = [{"role": "user", "content": "A dashboard for my day"}]
    with patch("app.services.builder_service._get_llm") as mock_llm:
        mock_llm.return_value = (None, None)
        spec = conversation_to_spec(messages)
    assert spec["type"] == "dashboard"
    assert "name" in spec and "features" in spec
