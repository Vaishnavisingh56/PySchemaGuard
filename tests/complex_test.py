db.execute("""
SELECT employee_id, employee_nam
FROM employeess
""")

db.execute("""
SELECT e.employee_name, d.departmnt_name
FROM employees e
JOIN department d
ON e.department_id = d.dept_id
""")

table = "employees"
db.execute(f"SELECT * FROM {table}")

db.execute("""
SELECT * FROM employees
JOIN departments ON employees.department_id = departments.department_id
""")

db.execute("""
SELECT salary FROM employees
""")
