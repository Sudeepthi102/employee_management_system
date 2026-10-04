from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

app = Flask(__name__)

# Secret key for flash messages
app.secret_key = os.getenv("SECRET_KEY", "default-secret-key")


# --------------------------------------------------
# MYSQL CONFIGURATION
# --------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "employee_db1"),
    "port": 3306,
    "charset": "utf8mb4"
}


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/")
def index():

    connection = None
    cursor = None

    try:
        connection = get_db_connection()

        cursor = connection.cursor(
            pymysql.cursors.DictCursor
        )

        # Total employees
        cursor.execute(
            "SELECT COUNT(*) AS total FROM employees"
        )

        total = cursor.fetchone()["total"]

        # Department count
        cursor.execute("""
            SELECT department, COUNT(*) AS count
            FROM employees
            GROUP BY department
            ORDER BY count DESC
        """)

        department_counts = cursor.fetchall()

        # Recent employees
        cursor.execute("""
            SELECT id, name, email, department, salary
            FROM employees
            ORDER BY id DESC
            LIMIT 5
        """)

        recent_employees = cursor.fetchall()

        return render_template(
            "index.html",
            total=total,
            department_counts=department_counts,
            recent_employees=recent_employees
        )

    except pymysql.MySQLError as e:

        flash(f"Database error: {e}", "error")

        return render_template(
            "index.html",
            total=0,
            department_counts=[],
            recent_employees=[]
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# VIEW EMPLOYEES
# --------------------------------------------------

@app.route("/employees")
def employees():

    connection = None
    cursor = None

    try:

        search = request.args.get(
            "search", ""
        ).strip()

        connection = get_db_connection()

        cursor = connection.cursor(
            pymysql.cursors.DictCursor
        )

        if search:

            query = """
                SELECT *
                FROM employees
                WHERE name LIKE %s
                OR email LIKE %s
                OR department LIKE %s
                ORDER BY id DESC
            """

            search_value = f"%{search}%"

            cursor.execute(
                query,
                (
                    search_value,
                    search_value,
                    search_value
                )
            )

        else:

            cursor.execute("""
                SELECT *
                FROM employees
                ORDER BY id DESC
            """)

        employee_list = cursor.fetchall()

        return render_template(
            "employees.html",
            employees=employee_list,
            search=search
        )

    except pymysql.MySQLError as e:

        flash(
            f"Database error: {e}",
            "error"
        )

        return render_template(
            "employees.html",
            employees=[],
            search=""
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# ADD EMPLOYEE
# --------------------------------------------------

@app.route("/add", methods=["GET", "POST"])
def add_employee():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        department = request.form["department"].strip()
        salary = request.form["salary"].strip()

        if not name or not email or not department or not salary:

            flash(
                "Please fill in all required fields.",
                "error"
            )

            return render_template(
                "add_employee.html"
            )

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            query = """
                INSERT INTO employees
                (name, email, phone, department, salary)
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    name,
                    email,
                    phone,
                    department,
                    salary
                )
            )

            connection.commit()

            flash(
                "Employee added successfully!",
                "success"
            )

            return redirect(
                url_for("employees")
            )

        except pymysql.IntegrityError:

            flash(
                "This email already exists.",
                "error"
            )

            return render_template(
                "add_employee.html"
            )

        except pymysql.MySQLError as e:

            flash(
                f"Database error: {e}",
                "error"
            )

            return render_template(
                "add_employee.html"
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template(
        "add_employee.html"
    )


# --------------------------------------------------
# EDIT EMPLOYEE
# --------------------------------------------------

@app.route(
    "/edit/<int:employee_id>",
    methods=["GET", "POST"]
)
def edit_employee(employee_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            pymysql.cursors.DictCursor
        )

        if request.method == "POST":

            name = request.form["name"].strip()
            email = request.form["email"].strip()
            phone = request.form["phone"].strip()
            department = request.form["department"].strip()
            salary = request.form["salary"].strip()

            if not name or not email or not department or not salary:

                flash(
                    "Please fill in all required fields.",
                    "error"
                )

                return redirect(
                    url_for(
                        "edit_employee",
                        employee_id=employee_id
                    )
                )

            cursor.execute("""
                UPDATE employees
                SET
                    name=%s,
                    email=%s,
                    phone=%s,
                    department=%s,
                    salary=%s
                WHERE id=%s
            """, (
                name,
                email,
                phone,
                department,
                salary,
                employee_id
            ))

            connection.commit()

            flash(
                "Employee updated successfully!",
                "success"
            )

            return redirect(
                url_for("employees")
            )

        # Get employee
        cursor.execute(
            "SELECT * FROM employees WHERE id=%s",
            (employee_id,)
        )

        employee = cursor.fetchone()

        if not employee:

            flash(
                "Employee not found.",
                "error"
            )

            return redirect(
                url_for("employees")
            )

        return render_template(
            "edit_employee.html",
            employee=employee
        )

    except pymysql.IntegrityError:

        flash(
            "This email already belongs to another employee.",
            "error"
        )

        return redirect(
            url_for(
                "edit_employee",
                employee_id=employee_id
            )
        )

    except pymysql.MySQLError as e:

        flash(
            f"Database error: {e}",
            "error"
        )

        return redirect(
            url_for("employees")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# --------------------------------------------------
# DELETE EMPLOYEE
# --------------------------------------------------

@app.post("/delete/<int:employee_id>")
def delete_employee(employee_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM employees WHERE id=%s",
            (employee_id,)
        )

        connection.commit()

        if cursor.rowcount:

            flash(
                "Employee deleted successfully.",
                "success"
            )

        else:

            flash(
                "Employee not found.",
                "error"
            )

    except pymysql.MySQLError as e:

        flash(
            f"Database error: {e}",
            "error"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(
        url_for("employees")
    )


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)