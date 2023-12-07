import json
from fastapi import APIRouter, HTTPException, status, Depends
from models.matchmaking import MatchmakingRequest
from models.users import User
from routes.auth import get_current_user

matchmaking_router = APIRouter(tags=["Matchmaking"])

with(open("data/users_data.json", "r")) as file:

    users_data = json.load(file)

def find_matchmaking_opponents(user_id, users_data):
    # Find the user requesting matchmaking
    requesting_user = None
    for user in users_data:
        if user["user_id"] == user_id:
            requesting_user = user
            break

    if requesting_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Initialize matchmaking opponents
    matchmaking_opponents = []

    # Iterate through users to find suitable matchmaking opponents
    for user in users_data:
        if (
            user["user_id"] != requesting_user["user_id"] and
            user["map_id"] == requesting_user["map_id"] and
            user["gamemode_id"] == requesting_user["gamemode_id"]
        ):
            # Calculate the rating difference between the requesting user and potential opponent
            rating_difference = abs(requesting_user["rating"] - user["rating"])

            # Ensure that the rating difference is within a specified range (200 points)
            if rating_difference <= 200:
                matchmaking_opponents.append(user)

                # Break when there are 5 suitable opponents
                if len(matchmaking_opponents) == 5:
                    break

    if len(matchmaking_opponents) < 1:
        raise HTTPException(status_code=404, detail="Insufficient suitable opponents for matchmaking")

    return matchmaking_opponents

@matchmaking_router.post("/", response_model=list[dict])
def matchmaking(current_user: User = Depends(get_current_user)):
    matchmaking_opponents = find_matchmaking_opponents(current_user.user_id, users_data)
    return matchmaking_opponents
