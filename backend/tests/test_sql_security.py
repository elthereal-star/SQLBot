"""Tests for SQL table authorization helpers."""

from pathlib import Path

import pytest

from apps.chat.task.sql_security import (
    extract_tables_from_sql,
    validate_authorized_tables,
)

BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_extract_tables_excludes_cte_aliases():
    sql = "WITH recent AS (SELECT * FROM orders) SELECT * FROM recent"

    assert extract_tables_from_sql(sql, "mysql") == {"orders"}


def test_authorized_tables_accepts_allowed_physical_tables():
    sql = "SELECT * FROM analytics.orders JOIN customers ON orders.customer_id = customers.id"

    assert validate_authorized_tables(sql, "mysql", {"orders", "customers"}) == {
        "orders",
        "customers",
    }


def test_authorized_tables_rejects_unknown_table():
    with pytest.raises(ValueError, match="unauthorized tables: secrets"):
        validate_authorized_tables("SELECT * FROM secrets", "mysql", {"orders"})


def test_authorized_tables_rejects_unparseable_sql():
    with pytest.raises(ValueError, match="unable to extract table names"):
        validate_authorized_tables("not sql", "mysql", {"orders"})
