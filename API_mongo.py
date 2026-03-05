from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from datetime import date
import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

app = FastAPI()

client = MongoClient(MONGO_URL)
db = client["Employee_DB"]
employee_collection = db["Employee"]

def employee_serializer(employee) -> dict:
    return {
        "emp_id": str(employee["_id"]),
        "emp_name": employee["emp_name"],
        "emp_age": employee["emp_age"],
        "emp_date_of_joining": employee["emp_date_of_joining"]
    }
@app.post("/employees/")
def create_employee(emp_name: str, emp_age: int, emp_date_of_joining: date):

    employee = {
        "emp_name": emp_name,
        "emp_age": emp_age,
        "emp_date_of_joining": str(emp_date_of_joining)
    }

    result = employee_collection.insert_one(employee)

    new_employee = employee_collection.find_one({"_id": result.inserted_id})

    return {
        "message": "Employee created successfully",
        "employee": employee_serializer(new_employee)
    }

@app.get("/employees/")
def get_all_employees():
    employees = employee_collection.find()
    return [employee_serializer(emp) for emp in employees]


@app.get("/employees/id/{emp_id}")
def get_employee_by_id(emp_id: str):
    try:
        emp = employee_collection.find_one({"_id": ObjectId(emp_id)})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid employee id format")

    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee_serializer(emp)


@app.get("/employees/name/{emp_name}")
def get_employee_by_name(emp_name: str):
    emp = employee_collection.find({"emp_name": emp_name})
    result = [employee_serializer(e) for e in emp]

    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")

    return result


@app.put("/employees/{emp_id}")
def update_employee(emp_id: str, emp_name: str, emp_age: int, emp_date_of_joining: date):

    try:
        obj_id = ObjectId(emp_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid employee id format")

    updated = employee_collection.update_one(
        {"_id": obj_id},
        {
            "$set": {
                "emp_name": emp_name,
                "emp_age": emp_age,
                "emp_date_of_joining": str(emp_date_of_joining)
            }
        }
    )

    if updated.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")

    emp = employee_collection.find_one({"_id": obj_id})

    return {
        "message": "Employee updated successfully",
        "employee": employee_serializer(emp)
    }

@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: str):

    try:
        obj_id = ObjectId(emp_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid employee id format")

    deleted = employee_collection.delete_one({"_id": obj_id})

    if deleted.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {"message": "Employee deleted successfully"}