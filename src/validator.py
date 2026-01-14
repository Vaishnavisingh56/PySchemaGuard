# src/validator.py

import json
import yaml
from src.sql_analyzer import SQLAnalyzer
from src.fuzzy import suggest


class SQLValidator:
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

    # ONLY columns from referenced tables
        table_cols = []
        for t in tables:
            if t in self.schema:
                table_cols.extend([c["name"] for c in self.schema[t]["columns"]])

        all_cols = []
        for t in self.schema:
            all_cols.extend(
                [c["name"] for c in self.schema[t]["columns"]]
            )

        for col in columns:
            if col not in table_cols:
                suggestion = suggest(col, all_cols)

                errors.append({
                "message": f"Column '{col}' not found",
                "suggestion": suggestion[0] if suggestion else None,
                "offending" : col,
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
            })

        return output


