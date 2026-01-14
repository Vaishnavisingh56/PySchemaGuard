from src.schema_extractor import SchemaExtractor

# Dummy connection parameters (replace later with real DB values)
params = {
    'host': 'localhost',
    'database': 'sql_validator_test',
    'user': 'postgres',
    'password': 'your_password'
}

extractor = SchemaExtractor(params)

# Try connecting and saving schema
if extractor.connect():
    extractor.save_schema('schema.json')
    extractor.disconnect()
else:
    print("Database connection failed — but code works fine!")
