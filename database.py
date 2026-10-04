import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "employee_db1"),
    "port": 3306,
    "charset": "utf8mb4"
}


def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


# Test database connection
if __name__ == "__main__":
    connection = None

    try:
        connection = get_db_connection()
        print("Database connected successfully!")

    except pymysql.MySQLError as e:
        print("Database error:", e)

    finally:
        if connection:
            connection.close()