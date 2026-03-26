# sqlalchemy-fhir-pathling

SQLAlchemy dialect and Apache Superset engine spec for querying FHIR data via the
[Pathling](https://pathling.csiro.au/) server's `$sqlquery-run` operation.

## Installation

```bash
pip install sqlalchemy-fhir-pathling
```

## Usage

### SQLAlchemy

```python
from sqlalchemy import create_engine, text

engine = create_engine("pathling://localhost:8080/fhir")
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM patients LIMIT 10"))
    for row in result:
        print(row)
```

### Apache Superset

After installing the package, restart Superset. The "FHIR Pathling" database type
will appear in the database connection dialog. Use a connection string like:

```
pathling://your-pathling-server:8080/fhir
```

Tables in Superset correspond to ViewDefinitions registered on the Pathling server.

### Standalone DBAPI

```python
from pathling.dbapi import connect

conn = connect(host="localhost", port=8080)
cursor = conn.cursor()
cursor.execute("SELECT patient_id, gender FROM patients")
for row in cursor.fetchall():
    print(row)
```
