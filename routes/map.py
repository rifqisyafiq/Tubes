import json
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, status, Depends
from models.map import Map
from models.users import User
from routes.auth import get_current_user

maps_data = []

map_router = APIRouter(tags=["Map"])

with open("data/maps_data.json", "r") as file:
    maps_data = json.load(file)

@map_router.get("/")
def get_all_maps(current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        return maps_data
    else:
        raise HTTPException(status_code=403, detail="Forbidden. Only admin can view all maps.")

@map_router.get("/{map_id}")
def get_map_by_id(map_id: int, current_user: User = Depends(get_current_user)):
    for map in maps_data:
        if map["mapid"] == map_id:
            return map
    raise HTTPException(status_code=404, detail="Map not found")

@map_router.post("/")
def create_map(map: Map, current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        maps_data.append(map.dict())
        with open("data/maps_data.json", "w") as file:
            json.dump(maps_data, file)
        return {"message": "Map created successfully"}
    else:
        raise HTTPException(status_code=403, detail="Forbidden. Only admin can create maps.")

@map_router.put("/")
def update_map(map: Map, current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        for i, existing_map in enumerate(maps_data):
            if existing_map["mapid"] == map.mapid:
                existing_map.update(map.dict())
                with open("data/maps_data.json", "w") as file:
                    json.dump(maps_data, file)
                return {"message": "Map data updated successfully"}
        raise HTTPException(status_code=404, detail="Map not found")
    else:
        raise HTTPException(status_code=403, detail="Forbidden. Only admin can update maps.")
