"""SQL parsing helpers used by the chat flow's authorization checks."""

import sqlglot
from sqlglot import exp
from apps.db.db import get_sqlglot_dialect


def _extract_tables_from_sql(sql: str, ds_type: str = None) -> set:
    """Return physical table names from SQL, excluding CTE aliases."""
    tables = set()
    dialect = get_sqlglot_dialect(ds_type)
    try:
        statements = sqlglot.parse(sql, dialect=dialect)
        for stmt in statements:
            if stmt:
                cte_names = {
                    cte.alias for cte in stmt.find_all(exp.CTE) if cte.alias
                }
                for table in stmt.find_all(exp.Table):
                    if table.name and table.name not in cte_names:
                        tables.add(table.name)
    except Exception:
        pass
    return tables


def extract_tables_from_sql(sql: str, ds_type: str = None) -> set:
    """Compatibility entry point for callers that only need table names."""
    return _extract_tables_from_sql(sql, ds_type)


def validate_authorized_tables(sql: str, ds_type: str, allowed_tables: set) -> set:
    """Extract SQL table names and reject unparseable or unauthorized queries."""
    from common.error import SingleMessageError

    actual_tables = _extract_tables_from_sql(sql, ds_type=ds_type)
    if not actual_tables:
        raise SingleMessageError(
            "SQL parsing failed: unable to extract table names. "
            "This may indicate an unsupported SQL syntax or a security issue."
        )

    unauthorized_tables = actual_tables - allowed_tables
    if unauthorized_tables:
        raise SingleMessageError(
            f"SQL contains unauthorized tables: {', '.join(unauthorized_tables)}. "
            f"Allowed tables: {', '.join(allowed_tables)}"
        )
    return actual_tables
