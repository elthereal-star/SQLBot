"""Tests for parsing structured responses from the language model."""

import ast
import json
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture
def parse_sql_answer():
    source = BACKEND_DIR / "apps/chat/task/llm_response.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "parse_sql_answer"
    )
    namespace = {
        "extract_nested_json": lambda value: value if value.startswith("{") else None,
        "orjson": type("Json", (), {
            "loads": staticmethod(json.loads),
            "dumps": staticmethod(lambda value: json.dumps(value).encode()),
        }),
        "SingleMessageError": ValueError,
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec"), namespace)
    return namespace["parse_sql_answer"]


def test_parses_sql_and_optional_table_hints(parse_sql_answer):
    assert parse_sql_answer('{"success":true,"sql":"SELECT 1","tables":["orders"]}') == (
        "SELECT 1",
        ["orders"],
    )


def test_parses_sql_without_table_hints(parse_sql_answer):
    assert parse_sql_answer('{"success":true,"sql":"SELECT 1"}') == ("SELECT 1", None)


def test_rejects_unsuccessful_response(parse_sql_answer):
    with pytest.raises(ValueError, match="model rejected request"):
        parse_sql_answer('{"success":false,"message":"model rejected request"}')


def test_rejects_invalid_or_empty_sql(parse_sql_answer):
    with pytest.raises(ValueError, match="not a valid json object"):
        parse_sql_answer("not json")
    with pytest.raises(ValueError, match="SQL query is empty"):
        parse_sql_answer('{"success":true,"sql":"   "}')
