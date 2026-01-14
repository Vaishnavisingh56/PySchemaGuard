class FakeDB:
    def execute(self, q):
        print(q)

q1 = """
SELECT employe_name
FROM employees
JOIN depart ON employees.department_id = depart.department_id
"""
db = FakeDB()
db.execute(q1)
