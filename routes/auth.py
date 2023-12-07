from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from passlib.context import CryptContext
import jwt
import json
import requests
from models.users import Token, UserIn, User

url = 'https://tubes-tst-18221066-rollcall.azurewebsites.net/'

def get_admin_token(admin_username: str, admin_password: str, token_url: str):
    data = {
        "username": admin_username,
        "password": admin_password
    }
    response = requests.post(token_url, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get token: {response.content}")
    
    token = response.json().get("access_token")
    return token

auth_router = APIRouter(tags=["Authentication"])
JWT_SECRET = 'myjwtsecret'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# Load user data from JSON file
with open("data/users_data.json", "r") as json_file:
    users_data = json.load(json_file)

# Function to write user data to JSON file
def write_users_to_json():
    with open("data/users_data.json", "w") as json_file:
        json.dump(users_data, json_file, indent=4)

# Function to authenticate and get user
def authenticate_user(username: str, password: str):
    for user in users_data:
        if user['username'] == username and bcrypt.verify(password, user['hashed_password']):
            return user
    return None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# Route to generate token
@auth_router.post('/token', response_model=Token)
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )

    token_data = {"sub": user['username'], "user_id": user['user_id']}
    token = jwt.encode(token_data, JWT_SECRET)

    return {'access_token': token, 'token_type': 'bearer'}

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload.get('user_id')
        user = next((u for u in users_data if u['user_id'] == user_id), None)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid user'
            )
        return User(**user)  # Convert user dictionary to User Pydantic model
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token'
        )

# Route to get current user
@auth_router.get('/users/me', response_model=User)
async def get_user(user: User = Depends(get_current_user)):
    return user

async def get_admin_token_async():
    return get_admin_token("afton", "1987", url + "/token")

# Route to register a new user
@auth_router.post('/register-friends', response_model=User)
async def register_user_and_friends(user: UserIn):
    user_id = len(users_data) + 30
    password_hash = bcrypt.hash(user.password)

    is_admin = user.username == "admin"
    admin_token = await get_admin_token_async()
    print("Admin Token:", admin_token)  # Add this line to check the token

    
    headers = {'Authorization': f'Bearer {admin_token}'}
    newuser ={
        "id": user_id,
        "username": user.username,
        "password": user.password,
        "boardgame": user.boardgame,
        "city": user.city,
        "role": "admin" if is_admin else "user",
    }
    response = requests.post(
    "https://tubes-tst-18221066-rollcall.azurewebsites.net/user",
    headers=headers,
    json=newuser)

    print("Response Status Code:", response.status_code)
    print("Response Content:", response.content)

    
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error registering user with your friend's API."
        )

    new_user = {
        "id": user_id,
        "username": user.username,
        "password_hash": password_hash,
        "is_admin": is_admin,
        "rating": user.rating,
        "map_id": user.map_id,
        "gamemode_id": user.gamemode_id,
    }
    users_data.append(new_user)
    write_users_to_json()

    return new_user
