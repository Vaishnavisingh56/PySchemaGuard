# Simple Fake Database Object
class FakeDB:
    def execute(self, query):
        print("Executing SQL:")
        print(query)
        return []


def fetch_employee_report(db):
    """
    This function runs two SQL queries:
    - One correct query (should pass validation)
    - One incorrect query (should show errors)
    """

    # Correct query
    correct_query = """
    SELECT employee_id, employee_name, department_id
    FROM employees
    """

    # Incorrect query with typos

    incorrect_query = """SELECT emp_naame, departmant_name
    FROM employes
    JOIN departments
    ON employees.department_id = departments.department_id"""
    db.execute("SELECT emp_naame FROM employes")


    # Execute queries (our validator will flag the wrong one)
    db.execute(correct_query)
    db.execute(incorrect_query)


def main():
    db = FakeDB()
    fetch_employee_report(db)


if __name__ == "__main__":
    main()
