# src/sql_analyzer.py

import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML


class SQLAnalyzer:
    def __init__(self, query: str):
        self.query = query

    def analyze(self):
        tables = []
        columns = []

        parsed = sqlparse.parse(self.query)
        if not parsed:
            return {"tables": [], "columns": []}

        stmt = parsed[0]

        from_seen = False

        for token in stmt.tokens:
            # SELECT columns
            if token.ttype is DML and token.value.upper() == "SELECT":
                continue

            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    name = identifier.get_real_name()
                    if name:
                        columns.append(name)

            elif isinstance(token, Identifier):
                name = token.get_real_name()
                if name:
                    if from_seen:
                        tables.append(name)
                    else:
                        columns.append(name)

            elif token.ttype is Keyword:
                if token.value.upper() in ("FROM", "JOIN"):
                    from_seen = True
                else:
                    from_seen = False

        return {
            "tables": list(set(tables)),
            "columns": list(set(columns)),
        }
