# src/validator.py

import json
import yaml
from src.sql_analyzer import SQLAnalyzer
from src.fuzzy import suggest
import re

SIMPLE_COMPARISON = re.compile(
    r"(\w+)\s*(=|<|>)\s*('[^']*'|\d+|true|false)",
    re.IGNORECASE,
)

INSERT_VALUES = re.compile(
    r"insert\s+into\s+\w+\s*\(([^)]+)\)\s*values\s*\(([^)]+)\)",
    re.IGNORECASE,
)

SQL_TYPE_GROUPS = {
    "numeric": {"integer", "bigint", "smallint", "decimal", "numeric", "real", "double"},
    "string": {"varchar", "text", "char"},
    "boolean": {"boolean"},
}



class SQLValidator:

    @staticmethod
    def infer_literal_type(value: str):
        value = value.strip()

        if value.startswith("'") and   value.endswith("'"):
            return "string"

        if value.isdigit():
            return "numeric"

        if value.lower() in ("true", "false"):
            return "boolean"

        return None  # Unknown → skip validation

    @staticmethod
    def is_compatible(column_type: str, literal_group: str):
        column_type = column_type.lower()

        # Normalize common PostgreSQL types
        if column_type.startswith("character"):
            column_type = "varchar"
        elif column_type.startswith("varchar"):
            column_type = "varchar"
        elif column_type.startswith("int"):
            column_type = "integer"
        elif column_type.startswith("bool"):
            column_type = "boolean"
        elif column_type.startswith("double"):
            column_type = "double"

        for group, types in SQL_TYPE_GROUPS.items():
            if column_type in types:
                return group == literal_group

        return True  # Unknown DB type → do not warn

    def __init__(self, schema_path="schema.json", config_path="default_config.yaml"):
        with open(schema_path, "r") as f:
            self.schema = json.load(f)

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)["fuzzy"]

    # ---------------- TABLE VALIDATION ----------------
    def check_tables(self, tables):
        errors = []
        known_tables = list(self.schema.keys())

        for table in tables:
            if table not in     known_tables:
                suggestion = suggest(table, known_tables)
                errors.append({
                "message": f"Table '{table}' not found",
                "suggestion": suggestion[0] if suggestion else None,
                "offending": table,
                "line": None,
                "start_col": None,
                "end_col": None,
            })
        return errors


    # ---------------- COLUMN VALIDATION ----------------
    def check_columns(self, tables, columns):
        errors = []

        # Map column -> list of tables it exists in
        column_to_tables = {}
        for table, meta in self.schema.items():
            for c in meta["columns"]:
                column_to_tables.setdefault(c["name"], []).append(table)

        # ONLY columns from referenced tables
        table_cols = []
        for t in tables:
            if t in self.schema:
                table_cols.extend([c["name"] for c in self.schema[t]["columns"]])

        all_cols = []
        for t in self.schema:
            all_cols.extend([c["name"] for c in self.schema[t]["columns"]])

        for col in columns:
            if col not in table_cols:
                raw_suggestion = suggest(col, table_cols) or suggest(col, all_cols)

                suggestion = None
                if raw_suggestion:
                    # CASE 1: Specific column typo (structured name)
                    if "_" in col:
                        suggestion = raw_suggestion[0]

                    # CASE 2: Generic root token (no underscore AND short-ish)
                    elif "_" not in col and len(col) <= 8:
                        suggestion = ", ".join(raw_suggestion)

                    # CASE 3: Fallback → single best suggestion
                    else:
                        suggestion = raw_suggestion[0]


                # Avoid useless self-suggestion
                if suggestion == col:
                    suggestion = None



                origin_tables = column_to_tables.get(col, [])
                origin_hint = None
                if len(origin_tables) == 1 and origin_tables[0] not in tables:
                    origin_hint = origin_tables[0]

                errors.append({
                    "message": (
                        f"Column '{col}' not found"
                        + (f" (exists in table '{origin_hint}')" if origin_hint else "")
                    ),
                    "suggestion": suggestion,
                    "offending": col,
                    "line": None,
                    "start_col": None,
                    "end_col": None,
                })

        return errors



    # ---------------- MAIN ENTRY ----------------
    def validate(self, query, file=None, line=None):
        analyzer = SQLAnalyzer(query)
        parts = analyzer.analyze()

        tables = parts.get("tables", [])
        columns = parts.get("columns", [])

        issues = []

    # 1️⃣ Validate tables first
        table_errors = self.check_tables(tables)
        issues.extend(table_errors)

    # 2️⃣ Only validate columns if at least ONE valid table exists
        valid_tables = [t for t in tables if t in self.schema]

        if valid_tables:
            column_errors = self.check_columns(valid_tables, columns)
            issues.extend(column_errors)

                # 2.5️⃣ Datatype-aware validation (warnings only)
            for match in SIMPLE_COMPARISON.finditer(query):
                column, operator, literal = match.groups()

            # Only validate if column exists in schema
                for table in valid_tables:
                    for col in self.schema[table]["columns"]:
                        if col["name"] == column:
                            column_type = col["type"]
                            literal_type = SQLValidator.infer_literal_type(literal)

                            if not literal_type:
                                continue  # Too complex → skip

                            if not SQLValidator.is_compatible(column_type, literal_type):
                                issues.append({
                                "message": (
                                    f"Possible type mismatch: column '{column}' "
                                    f"expects {column_type}, but literal looks like {literal_type}"
                                ),
                                "offending": column,
                                "severity": "warning",
                                "line": None,
                                "start_col": None,
                                "end_col": None,
                            })
                    # 2.6️⃣ INSERT datatype-aware validation
            insert_match = INSERT_VALUES.search(query)
            if insert_match and valid_tables:
                col_list = [c.strip() for c in insert_match.group(1).split(",")]
                val_list = [v.strip() for v in insert_match.group(2).split(",")]

                if len(col_list) == len(val_list):
                    table = valid_tables[0]

                    schema_cols = {
                        c["name"]: c["type"]
                        for c in self.schema[table]["columns"]
                    }

                    for col, val in zip(col_list, val_list):
                        if col not in schema_cols:
                            continue

                        literal_type = SQLValidator.infer_literal_type(val)
                        if not literal_type:
                            continue

                        column_type = schema_cols[col]

                        if not SQLValidator.is_compatible(column_type, literal_type):
                            issues.append({
                            "message": (
                                f"Possible type mismatch: column '{col}' "
                                f"expects {column_type}, but literal looks like {literal_type}"
                            ),
                            "offending": col,
                            "severity": "warning",
                            "line": None,
                            "start_col": None,
                            "end_col": None,
                        })

    # 3️⃣ Final structured output
        output = []
        for e in issues:
            output.append({
                "file": file,
                "line": line,
                "offending": e.get("offending"),
                "start_col": e.get("start_col"),
                "end_col": e.get("end_col"),
                "message": e["message"],
                "suggestion": e.get("suggestion"),
                "severity": e.get("severity","error"),
            })

        return output


