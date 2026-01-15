# src/sql_analyzer.py

import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML, DDL, Name


class SQLAnalyzer:
    def __init__(self, query: str):
        self.query = query

    def _extract_identifiers(self, token):

        names = []

        if isinstance(token, Identifier):
            name = token.get_real_name()
            if name:
                names.append(name)

        elif isinstance(token, IdentifierList):
            for identifier in token.get_identifiers():
                names.extend(self._extract_identifiers(identifier))

        elif token.ttype is Keyword:
            value = token.value
            if value.isidentifier():
                names.append(value)

        elif hasattr(token, "tokens"):
            for subtoken in token.tokens:
                names.extend(self._extract_identifiers(subtoken))

        return names

    def _get_statement_type(self, stmt):
        for token in stmt.tokens:
            if token.ttype in (Keyword, DML, DDL):
                return token.value.upper()
        return None

    def analyze(self):
        parsed = sqlparse.parse(self.query)
        if not parsed:
            return {"tables": [], "columns": []}

        stmt = parsed[0]

        stmt_type = self._get_statement_type(stmt)  # SELECT, UPDATE, INSERT, DELETE, DROP, TRUNCATE

        if stmt_type == "SELECT":
            return self._analyze_select(stmt)

        if stmt_type == "UPDATE":
            return self._analyze_update(stmt)

        if stmt_type == "INSERT":
            return self._analyze_insert(stmt)

        if stmt_type == "DELETE":
            return self._analyze_delete(stmt)

        if stmt_type in ("DROP", "TRUNCATE"):
            return self._analyze_ddl(stmt)

        return {"tables": [], "columns": []}

    # ---------------- SELECT ----------------
    def _analyze_select(self, stmt):
        tables = []
        columns = []
        from_seen = False

        for token in stmt.tokens:
        # Switch context at FROM / JOIN
            if token.ttype is Keyword and token.value.upper() in ("FROM", "JOIN"):
                from_seen = True
                continue

        # Always recurse
            names = self._extract_identifiers(token)

            if not names:
                continue

            if from_seen:
                tables.extend(names)
            else:
                columns.extend(names)

        return {
            "tables": list(set(tables)),
            "columns": list(set(columns)),
        }


    # ---------------- UPDATE ----------------
    def _analyze_update(self, stmt):
        tables = []
        columns = []
        set_seen = False

        for token in stmt.tokens:
            # Table after UPDATE
            if isinstance(token, Identifier) and not tables:
                tables.append(token.get_real_name())

            # SET keyword
            if token.ttype is Keyword and token.value.upper() == "SET":
                set_seen = True
                continue

            # Columns inside SET
            if set_seen:
                columns.extend(self._extract_identifiers(token))

            # Stop at WHERE
            if token.ttype is Keyword and token.value.upper() == "WHERE":
                break

        return {
            "tables": list(set(tables)),
            "columns": list(set(columns)),
        }

    # ---------------- INSERT ----------------
    # ---------------- INSERT ----------------
    def _analyze_insert(self, stmt):
        tables = []
        columns = []

        for token in stmt.tokens:
        # INSERT INTO table(col1, col2)
            if token.__class__.__name__ == "Function":
                table = token.get_name()
                if table:
                    tables.append(table)

            # Columns are function parameters
                for param in token.get_parameters():
                    if isinstance(param, Identifier):
                        col = param.get_real_name()
                        if col:
                            columns.append(col)

        return {
            "tables": list(set(tables)),
            "columns": list(set(columns)),
        }



    # ---------------- DELETE ----------------
    def _analyze_delete(self, stmt):
        tables = []
        from_seen = False

        for token in stmt.tokens:
            if token.ttype is Keyword and token.value.upper() == "FROM":
                from_seen = True
                continue

            if from_seen and isinstance(token, Identifier):
                tables.append(token.get_real_name())
                break

        return {
            "tables": list(set(tables)),
            "columns": [],
        }

    # ---------------- DROP / TRUNCATE ----------------
    def _analyze_ddl(self, stmt):
        tables = []

        for token in stmt.tokens:
            if isinstance(token, Identifier):
                name = token.get_real_name()
                if name:
                    tables.append(name)
                break   # first identifier is the table

        return {
            "tables": list(set(tables)),
            "columns": [],
        }



