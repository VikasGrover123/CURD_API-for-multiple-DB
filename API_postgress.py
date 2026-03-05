from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import date
from sqlalchemy import func
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

app = FastAPI()

class Employee(Base):
    __tablename__ = "Employee"   # case-sensitive table name

    empid = Column("Emp_ID", Integer, primary_key=True, index=True)
    empname = Column("Emp_Name", String)
    empage = Column("Emp_Age", Integer)
    empdate_of_joining = Column("Emp_Date_Of_Joining", Date)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/pg/employees/")
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@app.get("/pg/employees/id/{emp_id}")
def get_employee_by_id(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.empid == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@app.get("/pg/employees/name/{emp_name}")
def get_employee_by_name(emp_name: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(
        func.lower(Employee.empname) == emp_name.lower().strip()
    ).all()

    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@app.post("/pg/employees/")
def create_employee(empname: str, empage: int, empdate_of_joining: date, db: Session = Depends(get_db)):
    new_emp = Employee(
        empname=empname.strip(),
        empage=empage,
        empdate_of_joining=empdate_of_joining
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

@app.put("/pg/employees/{emp_id}")
def update_employee(emp_id: int, empname: str, empage: int, empdate_of_joining: date, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.empid == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    emp.empname = empname.strip()
    emp.empage = empage
    emp.empdate_of_joining = empdate_of_joining

    db.commit()
    db.refresh(emp)
    return emp

@app.delete("/pg/employees/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.empid == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(emp)
    db.commit()
    return {"message": "Employee deleted"}