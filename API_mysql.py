from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Date, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("MYSQL_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

app = FastAPI()

class Employee(Base):
    __tablename__ = "employee"

    empid = Column("EMPID", Integer, primary_key=True, index=True)
    empname = Column("EMPNAME", String(45))
    empage = Column("EMPAGE", Integer)
    empdate_of_joining = Column("EMPDATE OF JOINING", Date)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/employees/")
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@app.get("/employees/id/{emp_id}")
def get_employee_by_id(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.empid == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp



@app.get("/employees/name/{emp_name}")
def get_employee_by_name(emp_name: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(
        func.lower(Employee.empname) == emp_name.lower().strip()
    ).all()

    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@app.post("/employees/")
def create_employee(empname: str, empage: int, empdate_of_joining: date, db: Session = Depends(get_db)):
    new_emp = Employee(
        empname=empname.strip(),   # 🔥 removes spaces
        empage=empage,
        empdate_of_joining=empdate_of_joining
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

@app.put("/employees/{emp_id}")
def update_employee(emp_id: int, empname: str, empage: int, empdate_of_joining: date, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.empid == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    emp.empname = empname
    emp.empage = empage
    emp.empdate_of_joining = empdate_of_joining

    db.commit()
    db.refresh(emp)
    return emp

@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.empid == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(emp)
    db.commit()
    return {"message": "Employee deleted"}