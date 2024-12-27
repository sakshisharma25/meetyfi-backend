from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from ....models.meeting import Meeting, MeetingCreate, MeetingUpdate
from ....db.mongodb import get_database
from app.api.v1.deps import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/meetings")
async def create_meeting(
    meeting: MeetingCreate,
    current_user = Depends(get_current_user)
):
    db = await get_database()
    meeting_dict = meeting.dict()
    meeting_dict["creator_id"] = current_user["_id"]
    meeting_dict["status"] = "pending"
    
    result = await db.meetings.insert_one(meeting_dict)
    return {"id": str(result.inserted_id)}

@router.get("/meetings", response_model=List[Meeting])
async def get_meetings(
    current_user = Depends(get_current_user),
    date: Optional[str] = None,
    client_name: Optional[str] = None,
    location: Optional[str] = None
):
    db = await get_database()
    query = {"creator_id": current_user["_id"]}
    
    if date:
        query["date"] = date
    if client_name:
        query["client_name"] = {"$regex": client_name, "$options": "i"}
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
        
    meetings = await db.meetings.find(query).to_list(None)
    return meetings

@router.post("/meetings/{meeting_id}/cancel")
async def cancel_meeting(
    meeting_id: str,
    current_user = Depends(get_current_user)
):
    db = await get_database()
    result = await db.meetings.update_one(
        {"_id": meeting_id, "creator_id": current_user["_id"]},
        {"$set": {"status": "cancelled"}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {"message": "Meeting cancelled successfully"}