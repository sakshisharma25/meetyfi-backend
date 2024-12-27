from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ....models.employee import Employee, EmployeeCreate
from ....db.mongodb import get_database
from ..deps import get_current_user
import requests
from ....config import get_settings

router = APIRouter()
settings = get_settings()

@router.post("/employees")
async def add_employee(
    employee: EmployeeCreate,
    current_user = Depends(get_current_user)
):
    if not current_user["is_manager"]:
        raise HTTPException(status_code=403, detail="Only managers can add employees")
        
    db = await get_database()
    employee_dict = employee.dict()
    employee_dict["manager_id"] = current_user["_id"]
    
    result = await db.employees.insert_one(employee_dict)
    return {"id": str(result.inserted_id)}

@router.get("/employees")
async def get_employees(current_user = Depends(get_current_user)):
    if not current_user["is_manager"]:
        raise HTTPException(status_code=403, detail="Only managers can view employees")
        
    db = await get_database()
    employees = await db.employees.find(
        {"manager_id": current_user["_id"]}
    ).to_list(None)
    return employees

@router.delete("/employees/{employee_id}")
async def delete_employee(
    employee_id: str,
    current_user = Depends(get_current_user)
):
    if not current_user["is_manager"]:
        raise HTTPException(status_code=403, detail="Only managers can delete employees")
        
    db = await get_database()
    result = await db.employees.delete_one(
        {"_id": employee_id, "manager_id": current_user["_id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {"message": "Employee deleted successfully"}

@router.get("/employees/{employee_id}/location")
async def get_employee_location(
    employee_id: str,
    current_user = Depends(get_current_user)
):
    db = await get_database()
    employee = await db.employees.find_one({"_id": employee_id})
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    # Get location details from Google Maps API
    url = f"https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{employee['latitude']},{employee['longitude']}",
        "key": settings.GOOGLE_MAPS_API_KEY
    }
    
    response = requests.get(url, params=params)
    location_data = response.json()
    
    if location_data["status"] == "OK":
        return {
            "address": location_data["results"][0]["formatted_address"],
            "coordinates": {
                "lat": employee["latitude"],
                "lng": employee["longitude"]
            }
        }
    else:
        raise HTTPException(status_code=400, detail="Could not fetch location details")