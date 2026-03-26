"""Apache Superset engine spec for the Pathling FHIR server.

Auto-discovered by Superset via the 'superset.db_engine_specs' entry point.
"""

from __future__ import annotations

from typing import Any

from superset.db_engine_specs.base import BaseEngineSpec


class PathlingEngineSpec(BaseEngineSpec):
    """Engine spec for querying FHIR data via Pathling's $sqlquery-run operation."""

    engine = "pathling"
    engine_name = "FHIR Pathling"
    engine_aliases: set[str] = set()
    drivers = {"rest": "Pathling REST API"}
    default_driver = "rest"

    sqlalchemy_uri_placeholder = "pathling://host:port/fhir"

    # Capabilities
    allows_joins = True
    allows_subqueries = True
    allows_alias_in_select = True
    allows_alias_in_orderby = True
    allows_sql_comments = False
    supports_file_upload = False
    disable_ssh_tunneling = True

    # Time grain expressions (Pathling uses Spark SQL syntax)
    _time_grain_expressions: dict[str | None, str] = {
        None: "{col}",
    }

    @classmethod
    def get_dbapi_exception_mapping(cls) -> dict[type[Exception], type[Exception]]:
        from pathling.dbapi.exceptions import (
            DatabaseError,
            OperationalError,
            ProgrammingError,
        )
        from superset.db_engine_specs.exceptions import (
            SupersetDBAPIDatabaseError,
            SupersetDBAPIOperationalError,
            SupersetDBAPIProgrammingError,
        )

        return {
            DatabaseError: SupersetDBAPIDatabaseError,
            OperationalError: SupersetDBAPIOperationalError,
            ProgrammingError: SupersetDBAPIProgrammingError,
        }

    @classmethod
    def get_allow_cost_estimate(cls, extra: dict[str, Any]) -> bool:
        return False

    @classmethod
    def get_schema_names(cls, inspector: Any) -> set[str]:
        return {"default"}
