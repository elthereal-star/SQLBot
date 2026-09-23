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


def parse_chart_answer(response: str) -> dict:
    """Parse and normalize a chart configuration returned by the model."""
    json_str = extract_nested_json(response)
    if json_str is None:
        raise SingleMessageError(
            orjson.dumps(
                {
                    "message": "Cannot parse chart config from answer",
                    "traceback": "Cannot parse chart config from answer:\n" + response,
                }
            ).decode()
        )

    try:
        data = orjson.loads(json_str)
        if data["type"] and data["type"] != "error":
            chart = data
            for column in chart.get("columns") or []:
                column["value"] = column.get("value").lower()

            axis = chart.get("axis")
            if axis:
                if axis.get("x"):
                    axis["x"]["value"] = axis["x"].get("value").lower()

                y_axis = axis.get("y")
                if isinstance(y_axis, list):
                    for item in y_axis:
                        if item.get("value"):
                            item["value"] = item["value"].lower()
                elif isinstance(y_axis, dict) and y_axis.get("value"):
                    y_axis["value"] = y_axis["value"].lower()

                if axis.get("series"):
                    axis["series"]["value"] = axis["series"].get("value").lower()

                multi_quota = axis.get("multi-quota")
                if multi_quota and multi_quota.get("value"):
                    value = multi_quota["value"]
                    if isinstance(value, list):
                        multi_quota["value"] = [item.lower() if item else item for item in value]
                    elif isinstance(value, str):
                        multi_quota["value"] = value.lower()
            return chart
        if data["type"] == "error":
            raise SingleMessageError(data["reason"])
        raise ValueError("Chart is empty")
    except SingleMessageError:
        raise
    except Exception:
        raise SingleMessageError(
            orjson.dumps(
                {
                    "message": "Cannot parse chart config from answer",
                    "traceback": "Cannot parse chart config from answer:\n" + response,
                }
            ).decode()
        )
