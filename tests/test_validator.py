from src.validator import SQLValidator

validator = SQLValidator("schema.json")

# Intentionally misspelled column
query = "SELECT username, emial FROM users"
validator.validate(query)
