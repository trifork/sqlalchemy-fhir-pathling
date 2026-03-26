"""Tests for the Pathling SQLAlchemy dialect."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

from pathling.sqlalchemy.dialect import PathlingDialect, _fhir_type_to_sqla
from tests.conftest import SAMPLE_QUERY_RESPONSE, SAMPLE_VIEW_DEFINITION_BUNDLE, _make_mock_response


def test_dialect_name():
    assert PathlingDialect.name == "pathling"


def test_create_connect_args_basic():
    dialect = PathlingDialect()
    url = make_url("pathling://myhost:9090/fhir")
    args, kwargs = dialect.create_connect_args(url)
    assert args == []
    assert kwargs["host"] == "myhost"
    assert kwargs["port"] == 9090
    assert kwargs["path"] == "/fhir"
    assert kwargs["scheme"] == "http"


def test_create_connect_args_with_auth():
    dialect = PathlingDialect()
    url = make_url("pathling://user:pass@myhost:8080/fhir")
    _, kwargs = dialect.create_connect_args(url)
    assert kwargs["username"] == "user"
    assert kwargs["password"] == "pass"


def test_create_connect_args_https_on_443():
    dialect = PathlingDialect()
    url = make_url("pathling://myhost:443/fhir")
    _, kwargs = dialect.create_connect_args(url)
    assert kwargs["scheme"] == "https"


def test_create_connect_args_default_path():
    dialect = PathlingDialect()
    url = make_url("pathling://myhost:8080")
    _, kwargs = dialect.create_connect_args(url)
    assert kwargs["path"] == "/fhir"


def test_fhir_type_to_sqla_string():
    from sqlalchemy import types as t
    result = _fhir_type_to_sqla("string")
    assert isinstance(result, t.String)


def test_fhir_type_to_sqla_integer():
    from sqlalchemy import types as t
    result = _fhir_type_to_sqla("integer")
    assert isinstance(result, t.Integer)


def test_fhir_type_to_sqla_date():
    from sqlalchemy import types as t
    result = _fhir_type_to_sqla("date")
    assert isinstance(result, t.Date)


def test_fhir_type_to_sqla_unknown():
    from sqlalchemy import types as t
    result = _fhir_type_to_sqla("unknownFhirType")
    assert isinstance(result, t.String)


def test_engine_get_table_names(mock_session):
    """Table names come from ViewDefinition names."""
    with patch("pathling.dbapi.connection.requests.Session", return_value=mock_session):
        engine = create_engine("pathling://localhost:8080/fhir")
        insp = inspect(engine)
        tables = insp.get_table_names()
        assert "conditions" in tables
        assert "patients" in tables


def test_engine_get_columns(mock_session):
    """Column metadata comes from ViewDefinition select columns."""
    with patch("pathling.dbapi.connection.requests.Session", return_value=mock_session):
        engine = create_engine("pathling://localhost:8080/fhir")
        insp = inspect(engine)
        columns = insp.get_columns("patients")
        col_names = [c["name"] for c in columns]
        assert "patient_id" in col_names
        assert "gender" in col_names
        assert "birth_date" in col_names


def test_engine_has_table(mock_session):
    with patch("pathling.dbapi.connection.requests.Session", return_value=mock_session):
        engine = create_engine("pathling://localhost:8080/fhir")
        insp = inspect(engine)
        assert insp.has_table("patients")
        assert not insp.has_table("nonexistent")


def test_engine_execute_query(mock_session):
    """Full query execution through SQLAlchemy."""
    with patch("pathling.dbapi.connection.requests.Session", return_value=mock_session):
        engine = create_engine("pathling://localhost:8080/fhir")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM patients"))
            rows = result.fetchall()
            assert len(rows) == 3
            assert rows[0][0] == "pat-1"
