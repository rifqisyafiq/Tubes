import json
import requests
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from models.map import Map
from models.users import User
from routes.auth import get_current_user

url = 'https://tubes-tst-18221066-rollcall.azurewebsites.net/'

rollcall_router = APIRouter(tags=["rollcall"])

current_user = User = Depends(get_current_user)

def get_token():
    token_url = url + '/token'
    token_response = requests.post(token_url, data={'username': 'afton', 'password': '1987'})
    token = token_response.json().get('access_token')
    return token

def get_boardgame_list():
    headers = {'Authorization': f'Bearer {get_token()}'}
    boardgame = requests.get(url + 'boardgame/', headers=headers)
    return boardgame.json()

def get_boardgame_details(boardgame_id: int):
    headers = {'Authorization': f'Bearer {get_token()}'}
    boardgame_details = requests.get(url + f'boardgame/{boardgame_id}', headers=headers)
    return boardgame_details.json()

def get_city_list():
    headers = {'Authorization': f'Bearer {get_token()}'}
    city = requests.get(url + 'city/', headers=headers)
    return city.json()

def get_user_list():
    headers = {'Authorization': f'Bearer {get_token()}'}
    user_response = requests.get(url + 'user/', headers=headers)
    return user_response.json() # Parse the JSON response

def get_user_details(user_id: int):
    headers = {'Authorization': f'Bearer {get_token()}'}
    user_details = requests.get(url + f'user/{user_id}', headers=headers)
    return user_details.json()

@rollcall_router.get('/boardgame/{boardgame_id}')
async def get_boardgame_name(boardgame_id: int):
    for boardgame in get_boardgame_list():
        if boardgame['id'] == boardgame_id:
            return boardgame
    raise HTTPException(status_code=404, detail="Boardgame not found")

from fastapi import HTTPException, status

@rollcall_router.post('/BoardgameMM', response_model=List[dict])
async def boardgame_matchmaking(current_user: User = Depends(get_current_user)):
    user_id = current_user.user_id
    
    user_details = get_user_details(user_id)
    if not user_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User details not found")

    user_boardgame_interest = user_details.get('boardgame', [])
    user_city = user_details.get('city', None)

    local_bgrating = current_user.bgrating

    potential_matches = []
    for user in get_user_list():
        if user['id'] != user_id: 
            user_bgrating = user.get('bgrating')
            
            if (
                set(user.get('boardgame', [])) & set(user_boardgame_interest) and
                user.get('city') == user_city and
                user_bgrating is not None and local_bgrating is not None and
                abs(user_bgrating - local_bgrating) <= 200
            ):
                potential_matches.append(user)

    if not potential_matches:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No potential matches found")

    return potential_matches


