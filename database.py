import os
import pyodbc

# Yeh khud aapke StudentProject folder ka path nikalega
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "students.accdb")

CONN_STR = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={DB_FILE};"

def get_db():
    if not os.path.exists(DB_FILE):
        raise FileNotFoundError(
            f"Database file nahi mili! Barah-e-karam 'students.accdb' ko apne 'StudentProject' folder me rakhein:\n{DB_FILE}"
        )
    return pyodbc.connect(CONN_STR)

def init_db():
    if not os.path.exists(DB_FILE):
        return

    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if Students table exists
        tables = [t.table_name.lower() for t in cursor.tables(tableType='TABLE')]
        if 'students' not in tables:
            cursor.execute("""
                CREATE TABLE Students (
                    ID AUTOINCREMENT PRIMARY KEY,
                    [Name] TEXT(100),
                    [RollNo] TEXT(50),
                    [Course] TEXT(100),
                    [Email] TEXT(100)
                )
            """)
            conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")