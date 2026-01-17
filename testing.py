# Invalid table name (typo)
TC_01 = "SELECT employee_nme FROM employes"

# Invalid table in DELETE
TC_02 = "DELETE FROM departmnts"

# Invalid table in DROP
TC_03 = "DROP TABLE employes"

# Invalid table in TRUNCATE
TC_04 = "TRUNCATE TABLE departmnts"


# Another column typo
TC_05 = "SELECT emp_naame FROM employees"


# 'location' exists in departments, not employees
TC_06 = "SELECT location FROM employees"


# Generic partial identifier
TC_07 = "SELECT employe FROM employees"

# Correct query
TC_08 = "SELECT employee_name FROM employees"


# Column typo in UPDATE
TC_09 = "UPDATE employees SET employee_nam = 'John'"

# Correct UPDATE
TC_10 = "UPDATE employees SET employee_name = 'John'"


# Assigning string to integer column
TC_11 = "UPDATE employees SET employee_id = 'hi'"

# Assigning number to string column
TC_12 = "UPDATE employees SET employee_name = 123"


# Column typo in INSERT
TC_13 = "INSERT INTO employees (employee_id, emp_naame) VALUES (1, 'John')"

# Datatype mismatch in INSERT
TC_14 = "INSERT INTO employees (employee_id, employee_name) VALUES ('1', 'John')"

# department_id exists in both tables
TC_15 = "SELECT departmet_id FROM employees"

TC_16 = "SELECT employee_name employees"

TC_17 = "UPDATE employees employee_name = 'John'"

TC_18 = "INSERT employees (employee_id) VALUES (1)"

TC_19 = "SELECT e.employee_name FROM employees e"

TC_20 = "SELECT employee_name FROM employees e WHERE EXISTS (SELECT 1 FROM departments d WHERE d.department_id=e.department_id)"