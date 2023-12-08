import json
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, status, Depends
from models.gamemode import Gamemode
from models.users import User
from routes.auth import get_current_user
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

gamemodes_data = []

gamemode_router = APIRouter(tags=["Gamemode"])

with open("data/gamemodes_data.json", "r") as file:
    gamemodes_data = json.load(file)

@gamemode_router.get("/gamemode/")
def get_all_gamemodes(current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        return gamemodes_data
    else:
        raise HTTPException(status_code=403, detail="Forbidden. Only admin can view all gamemodes.")

@gamemode_router.get("/gamemode/{mode_id}")
def get_gamemode_by_id(mode_id: int, current_user: User = Depends(get_current_user)):
    for gamemode in gamemodes_data:
        if gamemode["mode_id"] == mode_id:
            return gamemode
    raise HTTPException(status_code=404, detail="Gamemode not found")

@gamemode_router.post("/gamemode/")
def create_gamemode(gamemode: Gamemode, current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        gamemodes_data.append(gamemode.dict())
        with open("data/gamemodes_data.json", "w") as file:
            json.dump(gamemodes_data, file)
        return {"message": "Gamemode created successfully"}
    else:
        raise HTTPException(status_code=403, detail="Forbidden. Only admin can create gamemodes.")

@gamemode_router.put("/gamemode/")
def update_gamemode(gamemode: Gamemode, current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        for i, existing_gamemode in enumerate(gamemodes_data):
            if existing_gamemode["mode_id"] == gamemode.mode_id:
                existing_gamemode.update(gamemode.dict())
                with open("data/gamemodes_data.json", "w") as file:
                    json.dump(gamemodes_data, file)
                return {"message": "Gamemode data updated successfully"}
        raise HTTPException(status_code=404, detail="Gamemode not found")
    else:
        raise HTTPException(status_code=403, detail="Forbidden. Only admin can update gamemodes.")

@gamemode_router.delete("/gamemode/{mode_id}")
def delete_gamemode_by_id(mode_id: int, current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        for gamemode in gamemodes_data:
            if gamemode["mode_id"] == mode_id:
                gamemodes_data.remove(gamemode)
                with open("data/gamemodes_data.json", "w") as file:
                    json.dump(gamemodes_data, file)
                return {"message": "Gamemode deleted successfully"}
        raise HTTPException(status_code=404, detail="Gamemode not found")
    else:
        raise HTTPException(status_code=403, detail="Forbidden. Only admin can delete gamemodes.")

templates = Jinja2Templates(directory="templates")  # Assuming templates are in a "templates" folder

@gamemode_router.get("/dashboard", response_class=HTMLResponse)
def gamemode_dashboard(current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        return templates.TemplateResponse("dashboard.html", {"request": current_user, "gamemodes": gamemodes_data, "is_admin": current_user.is_admin})
    else:
        raise HTTPException(status_code=403, detail="Forbidden. Only admin can access the dashboard.")