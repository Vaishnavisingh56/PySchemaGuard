import pg8000

def main():
    try:
        conn = pg8000.connect(
            host="localhost",
            port=5432,
            database="sql_validator_db",  # your DB name
            user="postgres",              # your postgres username
            password="HiimV973@" # your postgres password
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees;")
        row = cursor.fetchone()
        print("✅ Connected! employees rows =", row[0])
        cursor.close()
        conn.close()
    except Exception as e:
        print("❌ Connection failed:", e)

if __name__ == "__main__":
    main()
