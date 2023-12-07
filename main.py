from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import matchmaking, gamemode, map, users, auth, rollcall

app = FastAPI()

app.include_router(matchmaking.matchmaking_router, prefix="/matchmaking")
app.include_router(gamemode.gamemode_router)
app.include_router(map.map_router, prefix="/map")
app.include_router(users.user_router, prefix="/user")
app.include_router(auth.auth_router)
app.include_router(rollcall.rollcall_router, prefix="/rollcall")

