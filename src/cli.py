import click, json
from pathlib import Path
from src.ast_parser import PythonSQLParser
from src.validator import SQLValidator

@click.group()
def cli():
    pass

@cli.command(name="check")
@click.argument("target", type=str)
@click.option("--json-output", is_flag=True)
def check_command(target, json_output):

    validator = SQLValidator("schema.json")
    path = Path(target)

    if not path.exists():
        msg = f"❌ Target not found: {target}"
        print(json.dumps({"error": msg}) if json_output else msg)
        return

    files = [str(path)] if path.is_file() else [str(p) for p in path.rglob("*.py")]
    all_errors = []

    for file_path in files:
        parser = PythonSQLParser(file_path)
        queries = parser.parse_file()

        for q in queries:
            result = validator.validate(q["query"], file_path, q["line"])
            if result:
                all_errors.extend(result)

    if json_output:
        print(json.dumps({"errors": all_errors}))
        return

    if not all_errors:
        print("✅ No SQL issues found.")
    else:
        for e in all_errors:
            print(f"{e['file']}:{e['line']} → {e['message']} (suggest: {e['suggestion']})")

if __name__ == "__main__":
    cli()
