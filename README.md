PySchemaGuard (Backend)

PySchemaGuard is a schema-aware static SQL validation tool for Python projects.
It analyzes SQL queries embedded in Python source code and validates them against a static snapshot of a PostgreSQL database schema, without executing the queries.

The backend provides:

SQL extraction from Python files

Schema-aware semantic validation

Fuzzy typo correction

Datatype mismatch detection

Structured diagnostics for IDE integration

🧠 Key Concept

PySchemaGuard performs semantic validation, not syntax validation.

❌ No SQL execution

❌ No runtime database queries

✅ Static analysis only

✅ Safe and deterministic

The database is accessed only once to generate a schema snapshot (schema.json).

📁 Repository Structure
PySchemaGuard/
├── src/
│   ├── cli.py
│   ├── validator.py
│   ├── sql_analyzer.py
│   ├── ast_parser.py
│   └── fuzzy.py
├── schema_extractor.py
├── schema.json
├── requirements.txt
├── default_config.yaml
└── README.md

✅ Prerequisites

Python 3.8 or later

PostgreSQL (only required for schema extraction)

📦 Installation
Install Python dependencies
Windows
py -m pip install -r requirements.txt

Linux / macOS
python3 -m pip install -r requirements.txt

🗄️ Schema Extraction (One-Time Setup)

Schema extraction is required only when the database structure changes.

1️⃣ Set environment variables
Windows (PowerShell)
$env:PG_HOST="localhost"
$env:PG_PORT="5432"
$env:PG_DATABASE="your_database"
$env:PG_USER="your_user"
$env:PG_PASSWORD="your_password"

Linux / macOS
export PG_HOST=localhost
export PG_PORT=5432
export PG_DATABASE=your_database
export PG_USER=your_user
export PG_PASSWORD=your_password

2️⃣ Run schema extractor
python schema_extractor.py


This generates:

schema.json


This file is used by the validator for all semantic checks.

▶️ Command-Line Usage

Validate a Python file:

python -m src.cli check your_file.py


JSON output mode (used by the VS Code extension):

python -m src.cli check your_file.py --json-output

🧪 Types of Issues Detected

Invalid table names

Invalid column names

Cross-table column misuse

Typographical errors (fuzzy suggestions)

Datatype mismatches in UPDATE / INSERT statements

⚠️ Limitations

Not a full SQL syntax validator

Limited support for deeply nested queries and advanced aliasing

Schema must be regenerated manually when DB changes

🔁 Reproducibility

Results are deterministic provided:

Same schema.json

Same Python version and dependencies

Same source code

📄 License

MIT License