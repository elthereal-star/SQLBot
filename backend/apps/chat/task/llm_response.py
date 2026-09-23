"""Parsing helpers for structured LLM responses."""

import orjson

from common.error import SingleMessageError
from common.utils.utils import extract_nested_json


def parse_sql_answer(response: str) -> tuple[str, list | None]:
    """Extract SQL and optional table hints from the model's SQL response."""
    json_str = extract_nested_json(response)
    if json_str is None:
        raise SingleMessageError(
            orjson.dumps(
                {
                    "message": "SQL answer is not a valid json object",
                    "traceback": "SQL answer is not a valid json object:\n" + response,
                }
            ).decode()
        )

    try:
        data = orjson.loads(json_str)
        if data["success"]:
            sql = data["sql"]
        else:
            raise SingleMessageError(data["message"])
    except SingleMessageError:
        raise
    except Exception:
        raise SingleMessageError(
            orjson.dumps(
                {
                    "message": "Cannot parse sql from answer",
                    "traceback": "Cannot parse sql from answer:\n" + response,
                }
            ).decode()
        )

    if sql.strip() == "":
        raise SingleMessageError("SQL query is empty")
    return sql, data.get("tables")
