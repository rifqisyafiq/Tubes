from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from passlib.context import CryptContext
import jwt
import json
import requests
from models.users import Token, UserIn, User
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


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

templates = Jinja2Templates(directory="Frontend")

@auth_router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@auth_router.get("/register-friends", response_class=HTMLResponse)
async def show_registration_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


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


# Route to register a new user
@auth_router.post('/register', response_model=User)
async def register_user_and_friends(user: UserIn):
    user_id = len(users_data) + 30
    password_hash = bcrypt.hash(user.password)

    is_admin = user.username == "admin"

    newuser ={
        "id": user_id,
        "username": user.username,
        "password": user.password,
        "boardgame": user.boardgame,
        "city": user.city,
        "role": "admin" if is_admin else "user",
        "friend" : [],
        "reservation": []
    }
    print(newuser)
    response = requests.post(
    "https://tubes-tst-18221066-rollcall.azurewebsites.net/register/",
    json=newuser
    )

    if response.status_code == 200:
        print("User registered successfully")
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, 
            detail="Error registering user with your friend's API."
        )

    new_user = {
        "user_id": user_id,
        "username": user.username,
        "hashed_password": password_hash,
        "is_admin": is_admin,
        "rating": user.rating,
        "bgrating": user.bgrating,
        "map_id": user.map_id,
        "gamemode_id": user.gamemode_id,
    }
    users_data.append(new_user)
    write_users_to_json()

    return new_user

@auth_router.get("/welcome", response_class=HTMLResponse)
async def welcome(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})