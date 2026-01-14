import json
import pg8000


class SchemaExtractor:
    def __init__(
        self,
        host="localhost",
        port=5432,
        database="sql_validator_db",  # change if your DB name is different
        user="postgres",
        password="HiimV973@",  # <-- put your actual password
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        try:
            self.conn = pg8000.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            print("✅ Connected to PostgreSQL for schema extraction")
        except Exception as e:
            print("❌ Failed to connect to PostgreSQL:", e)
            self.conn = None

    def close(self):
        if self.conn:
            self.conn.close()

    def extract_tables(self):
        """
        Return list of table names from 'public' schema.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE';
            """
        )
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def extract_columns(self, table_name):
        """
        Return list of column dicts: {name, data_type, is_nullable}
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
            ORDER BY ordinal_position;
            """,
            (table_name,),
        )
        columns = []
        for name, data_type, is_nullable in cursor.fetchall():
            columns.append(
                {
                    "name": name,
                    "type": data_type,
                    "nullable": (is_nullable == "YES"),
                }
            )
        cursor.close()
        return columns

    def extract_schema(self):
        """
        Return full schema as:
        {
          "departments": { "columns": [ ... ] },
          "employees":   { "columns": [ ... ] }
        }
        """
        schema = {}
        tables = self.extract_tables()
        for table in tables:
            schema[table] = {
                "columns": self.extract_columns(table),
            }
        return schema

    def save_to_file(self, output_file="schema.json"):
        if not self.conn:
            print("❌ No DB connection. Call connect() first.")
            return

        schema = self.extract_schema()
        with open(output_file, "w") as f:
            json.dump(schema, f, indent=2)

        print(f"✅ Schema saved to {output_file}")


if __name__ == "__main__":
    extractor = SchemaExtractor(
        host="localhost",
        port=5432,
        database="sql_validator_db",  # change if needed
        user="postgres",
        password="HiimV973@",  # same as in test_db_connection.py
    )
    extractor.connect()
    extractor.save_to_file("schema.json")
    extractor.close()
