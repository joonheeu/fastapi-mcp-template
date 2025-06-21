"""
Users management router.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ...core.models import User, APIResponse
from ...core.database import db

router = APIRouter()


@router.get("/users", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    active_only: bool = Query(False, description="Show only active users")
):
    """
    Get all users with optional filtering and pagination.
    """
    users = db.find_all("users", skip=skip, limit=limit)
    
    # Apply filters
    if active_only:
        users = [user for user in users if user.get("is_active", True)]
    
    return users


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """
    Get a specific user by ID.
    """
    user = db.find_by_id("users", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/search/by-username/{username}", response_model=User)
async def get_user_by_username(username: str):
    """
    Get a user by username.
    """
    users = db.find_by_field("users", "username", username)
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[0]  # Username should be unique


@router.get("/users/search/by-email/{email}", response_model=User)
async def get_user_by_email(email: str):
    """
    Get a user by email.
    """
    users = db.find_by_field("users", "email", email)
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[0]  # Email should be unique


@router.post("/users", response_model=User, status_code=201)
async def create_user(user_data: dict):
    """
    Create a new user.
    
    Example request body:
    {
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "role": "user"
    }
    """
    # Check if username already exists
    existing_users = db.find_by_field("users", "username", user_data.get("username"))
    if existing_users:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    existing_emails = db.find_by_field("users", "email", user_data.get("email"))
    if existing_emails:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Set default values
    user_data.setdefault("is_active", True)
    user_data.setdefault("role", "user")
    
    # Insert into database
    created_user = db.insert("users", user_data)
    
    return created_user


@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: dict):
    """
    Update an existing user.
    """
    # Check if user exists
    existing_user = db.find_by_id("users", user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If updating username, check for conflicts
    if "username" in user_update:
        existing_usernames = db.find_by_field("users", "username", user_update["username"])
        # Allow if it's the same user or no conflict
        if existing_usernames and existing_usernames[0]["id"] != user_id:
            raise HTTPException(status_code=400, detail="Username already exists")
    
    # If updating email, check for conflicts
    if "email" in user_update:
        existing_emails = db.find_by_field("users", "email", user_update["email"])
        # Allow if it's the same user or no conflict
        if existing_emails and existing_emails[0]["id"] != user_id:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Update user
    updated_user = db.update("users", user_id, user_update)
    
    return updated_user


@router.delete("/users/{user_id}", response_model=APIResponse)
async def delete_user(user_id: int):
    """
    Delete a user.
    """
    # Check if user exists
    existing_user = db.find_by_id("users", user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete user
    success = db.delete("users", user_id)
    
    if success:
        return APIResponse(
            success=True,
            message=f"User '{existing_user['username']}' deleted successfully",
            data={"deleted_user_id": user_id}
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to delete user")


@router.post("/users/{user_id}/deactivate", response_model=User)
async def deactivate_user(user_id: int):
    """
    Deactivate a user (soft delete).
    """
    existing_user = db.find_by_id("users", user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = db.update("users", user_id, {"is_active": False})
    return updated_user


@router.post("/users/{user_id}/activate", response_model=User)
async def activate_user(user_id: int):
    """
    Activate a user.
    """
    existing_user = db.find_by_id("users", user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = db.update("users", user_id, {"is_active": True})
    return updated_user


@router.get("/users/stats/summary")
async def get_users_stats():
    """
    Get summary statistics about users.
    """
    all_users = db.find_all("users")
    
    total_users = len(all_users)
    active_users = len([user for user in all_users if user.get("is_active", True)])
    
    # Role distribution
    roles = {}
    for user in all_users:
        role = user.get("role", "unknown")
        roles[role] = roles.get(role, 0) + 1
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "roles": roles,
        "recent_users": all_users[-5:] if all_users else []  # Last 5 users
    } 