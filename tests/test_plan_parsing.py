"""plan.extract_roadmap_json: LLM 응답에서 로드맵 JSON 추출 방어 로직 회귀 테스트."""
import json

import pytest

from app.api.plan import extract_roadmap_json


def test_plain_json():
    assert extract_roadmap_json('{"a": 1}') == {"a": 1}


def test_strips_markdown_json_fence():
    text = '```json\n{"project_title": "X"}\n```'
    assert extract_roadmap_json(text)["project_title"] == "X"


def test_strips_surrounding_prose():
    text = '여기 계획입니다:\n{"a": 1, "b": [1, 2]}\n도움이 되길 바랍니다!'
    assert extract_roadmap_json(text) == {"a": 1, "b": [1, 2]}


def test_nested_braces_preserved():
    text = '{"outer": {"inner": 2}, "list": [{"k": "v"}]}'
    assert extract_roadmap_json(text) == {"outer": {"inner": 2}, "list": [{"k": "v"}]}


def test_invalid_raises_json_decode_error():
    with pytest.raises(json.JSONDecodeError):
        extract_roadmap_json("여기에는 JSON이 없습니다")
