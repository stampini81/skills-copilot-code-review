"""
Announcements endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


@router.get("")
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get all active announcements (visible announcements)"""
    now = datetime.utcnow()
    
    # Find announcements that are currently active:
    # - start_date is None or before now
    # - expiration_date is after now
    query = {
        "$and": [
            {"$or": [
                {"start_date": None},
                {"start_date": {"$lte": now}}
            ]},
            {"expiration_date": {"$gt": now}}
        ]
    }
    
    announcements = list(announcements_collection.find(query).sort("expiration_date", 1))
    
    # Convert ObjectId to string for JSON serialization
    for announcement in announcements:
        announcement["_id"] = str(announcement["_id"])
        if announcement.get("start_date"):
            announcement["start_date"] = announcement["start_date"].isoformat()
        announcement["expiration_date"] = announcement["expiration_date"].isoformat()
    
    return announcements


@router.get("/all")
def get_all_announcements(username: str) -> List[Dict[str, Any]]:
    """Get all announcements (admin only)"""
    # Verify user is authenticated and is a teacher/admin
    teacher = teachers_collection.find_one({"_id": username})
    
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    announcements = list(announcements_collection.find().sort("expiration_date", -1))
    
    # Convert ObjectId to string for JSON serialization
    for announcement in announcements:
        announcement["_id"] = str(announcement["_id"])
        if announcement.get("start_date"):
            announcement["start_date"] = announcement["start_date"].isoformat()
        announcement["expiration_date"] = announcement["expiration_date"].isoformat()
    
    return announcements


@router.post("")
def create_announcement(
    username: str,
    message: str,
    expiration_date: str,
    start_date: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new announcement (admin only)"""
    # Verify user is authenticated
    teacher = teachers_collection.find_one({"_id": username})
    
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Parse dates
    try:
        exp_date = datetime.fromisoformat(expiration_date.replace("Z", "+00:00"))
        start_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO 8601 format.")
    
    # Validate dates
    if start_dt and start_dt >= exp_date:
        raise HTTPException(status_code=400, detail="Start date must be before expiration date.")
    
    # Create announcement
    announcement = {
        "message": message,
        "start_date": start_dt,
        "expiration_date": exp_date,
        "created_by": username,
        "created_at": datetime.utcnow()
    }
    
    result = announcements_collection.insert_one(announcement)
    
    # Return created announcement
    announcement["_id"] = str(result.inserted_id)
    announcement["start_date"] = announcement["start_date"].isoformat() if announcement["start_date"] else None
    announcement["expiration_date"] = announcement["expiration_date"].isoformat()
    announcement["created_at"] = announcement["created_at"].isoformat()
    
    return announcement


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: str,
    username: str,
    message: str,
    expiration_date: str,
    start_date: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing announcement (admin only)"""
    # Verify user is authenticated
    teacher = teachers_collection.find_one({"_id": username})
    
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Validate ObjectId
    try:
        obj_id = ObjectId(announcement_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid announcement ID")
    
    # Parse dates
    try:
        exp_date = datetime.fromisoformat(expiration_date.replace("Z", "+00:00"))
        start_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO 8601 format.")
    
    # Validate dates
    if start_dt and start_dt >= exp_date:
        raise HTTPException(status_code=400, detail="Start date must be before expiration date.")
    
    # Find and update announcement
    announcement = announcements_collection.find_one({"_id": obj_id})
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Update fields
    update_data = {
        "message": message,
        "start_date": start_dt,
        "expiration_date": exp_date,
        "updated_by": username,
        "updated_at": datetime.utcnow()
    }
    
    announcements_collection.update_one({"_id": obj_id}, {"$set": update_data})
    
    # Return updated announcement
    updated_announcement = announcements_collection.find_one({"_id": obj_id})
    updated_announcement["_id"] = str(updated_announcement["_id"])
    updated_announcement["start_date"] = updated_announcement["start_date"].isoformat() if updated_announcement.get("start_date") else None
    updated_announcement["expiration_date"] = updated_announcement["expiration_date"].isoformat()
    updated_announcement["created_at"] = updated_announcement["created_at"].isoformat()
    if updated_announcement.get("updated_at"):
        updated_announcement["updated_at"] = updated_announcement["updated_at"].isoformat()
    
    return updated_announcement


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str, username: str) -> Dict[str, str]:
    """Delete an announcement (admin only)"""
    # Verify user is authenticated
    teacher = teachers_collection.find_one({"_id": username})
    
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Validate ObjectId
    try:
        obj_id = ObjectId(announcement_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid announcement ID")
    
    # Delete announcement
    result = announcements_collection.delete_one({"_id": obj_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    return {"status": "success", "message": "Announcement deleted"}
