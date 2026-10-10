import os
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from database import get_db, init_db, DB_FILE

class Student(BaseModel):
    name: str
    roll_no: str
    course: str
    email: str

class StudentResponse(Student):
    id: int

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Student Management API", lifespan=lifespan)

app.add_middleware(
    
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Website Home Page
@app.get("/", include_in_schema=False)
def home():
    index_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    static_index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")
    if os.path.exists(static_index):
        return FileResponse(static_index)
    return {"message": "Server running! Please place index.html in the folder."}

# Status Check (Database connection verify karta hai)
@app.get("/api/status")
@app.get("/status")
def check_status():
    if not os.path.exists(DB_FILE):
        return {"status": "error", "connected": False, "message": "Database file 'students.accdb' nahi mili!"}
    try:
        init_db()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Students")
        cur.fetchone()
        cur.close()
        conn.close()
        return {"status": "ok", "connected": True, "message": "Database kamiyabi se connect ho gaya!"}
    except Exception as e:
        return {"status": "error", "connected": False, "message": str(e)}

# 1. GET (Read all students)
@app.get("/api/students", response_model=List[StudentResponse])
@app.get("/students", response_model=List[StudentResponse])
def get_students():
    try:
        init_db()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT ID, [Name], [RollNo], [Course], [Email] FROM Students ORDER BY ID DESC")
        rows = cur.fetchall()
        data = [
            {"id": int(r[0]), "name": str(r[1] or ""), "roll_no": str(r[2] or ""), "course": str(r[3] or ""), "email": str(r[4] or "")}
            for r in rows
        ]
        cur.close()
        conn.close()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. POST (Add new student)
@app.post("/api/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def add_student(s: Student):
    try:
        init_db()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Students ([Name], [RollNo], [Course], [Email]) VALUES (?, ?, ?, ?)",
            (s.name, s.roll_no, s.course, s.email)
        )
        conn.commit()
        cur.execute("SELECT @@IDENTITY")
        new_id = int(cur.fetchone()[0])
        cur.close()
        conn.close()
        return {"id": new_id, **s.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. PUT (Update student)
@app.put("/api/students/{id}")
@app.put("/students/{id}")
def update_student(id: int, s: Student):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT ID FROM Students WHERE ID = ?", (id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Student nahi mila!")

        cur.execute(
            "UPDATE Students SET [Name]=?, [RollNo]=?, [Course]=?, [Email]=? WHERE ID=?",
            (s.name, s.roll_no, s.course, s.email, id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "Updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. DELETE (Delete student)
@app.delete("/api/students/{id}")
@app.delete("/students/{id}")
def delete_student(id: int):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT ID FROM Students WHERE ID = ?", (id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Student nahi mila!")

        cur.execute("DELETE FROM Students WHERE ID = ?", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "Deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)