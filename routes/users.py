import json, requests
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, status, Depends, Request
from routes.auth import get_current_user
from routes.rollcall import get_user_list
from models.users import User
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

url = 'https://ca-sereneapp.braveisland-f409e30d.southeastasia.azurecontainerapps.io/'

users_data = []

user_router = APIRouter(tags=["User"])

def get_token():
	token_url = url+'auth/token'
	token_response = requests.post(token_url, data={'username': 'johndoe', 'password': 'password123'})
	token = token_response.json().get('access_token')
	return token

def get_psychologist_list():
    headers = {'Authorization': f'Bearer {get_token()}'}
    psychologist = requests.get(url+'psychologist/', headers=headers)
    return psychologist.json()

def get_user_list():
    headers = {'Authorization': f'Bearer {get_token()}'}
    user = requests.get(url+'user/', headers=headers)
    return user.json()

with open("data/users_data.json", "r") as file:
    users_data = json.load(file)

@user_router.get("/")
def get_all_users(current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        return users_data
    else:
        # If not admin, only return the current user's profile
        return [user for user in users_data if user["user_id"] == current_user.user_id]

@user_router.get("/{user_id}")
def get_user_by_id(user_id: int, current_user: User = Depends(get_current_user)):
    for user in users_data:
        if user["user_id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@user_router.post("/")
def create_user(user: User, current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        users_data.append(user.dict())
        with open("data/users_data.json", "w") as file:
            json.dump(users_data, file)
        return {"message": "User created successfully"}
    else:
        raise HTTPException(status_code=403, detail="Forbidden. Only admin can create users.")

@user_router.put("/")
def update_user(user: User, current_user: User = Depends(get_current_user)):
    if current_user.is_admin or user.user_id == current_user.user_id:
        for i, existing_user in enumerate(users_data):
            if existing_user["user_id"] == user.user_id:
                existing_user.update(user.dict())
                with open("data/users_data.json", "w") as file:
                    json.dump(users_data, file)
                return {"message": "User data updated successfully"}
        raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=403, detail="Forbidden. You can only update your own profile or as an admin.")

@user_router.delete("/{user_id}")
def delete_user_by_id(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_admin or user_id == current_user.user_id:
        for user in users_data:
            if user["user_id"] == user_id:
                users_data.remove(user)
                with open("data/users_data.json", "w") as file:
                    json.dump(users_data, file)
                return {"message": "User deleted successfully"}
        raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=403, detail="Forbidden. You can only delete your own profile or as an admin.")

templates = Jinja2Templates(directory="frontend")
@user_router.get("/user-dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden. Only admin can access the user dashboard.")
    
    user_list = get_user_list()  # Assuming you have a function to get the user list in your controller
    return templates.TemplateResponse("user_dashboard.html", {"request": request, "user_list": user_list})