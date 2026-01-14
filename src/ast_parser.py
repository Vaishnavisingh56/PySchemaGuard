import ast

class PythonSQLParser:
    """Parses Python files to find embedded SQL queries"""

    def __init__(self, file_path):
        self.file_path = file_path
        self.sql_queries = []

    def parse_file(self):
        """Extracts SQL-like strings from a Python file"""
        try:
            with open(self.file_path, "r") as f:
                source_code = f.read()
        except FileNotFoundError:
            return []

        try:
            tree = ast.parse(source_code, filename=self.file_path)
        except SyntaxError:
            return []

        for node in ast.walk(tree):
            # Handle regular string literals
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                self.check_if_sql(node.value, node.lineno)
            # Handle older Python versions using ast.Str
            elif isinstance(node, ast.Str):
                self.check_if_sql(node.s, node.lineno)

        return self.sql_queries

    def check_if_sql(self, string_value, line_number):
        """Check if a string is likely to be SQL"""
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP"]
        upper_string = string_value.upper().strip()

        if any(upper_string.startswith(keyword) for keyword in sql_keywords):
            self.sql_queries.append({
                "query": string_value,
                "line": line_number,
                "file": self.file_path
            })
