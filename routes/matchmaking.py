import json
from fastapi import APIRouter, HTTPException, Depends
from models.users import User
from routes.auth import get_current_user

matchmaking_router = APIRouter(tags=["Matchmaking"])

def load_users_data():
    with open("data/users_data.json", "r") as file:
        return json.load(file)

def find_matchmaking_opponents(user_id, users_data):
    # Print debug information
    print("User ID:", user_id)
    print("Users Data:", users_data)

    # Find the user requesting matchmaking
    requesting_user = next((user for user in users_data if user.get("user_id") == user_id), None)

    if requesting_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Initialize matchmaking opponents
    matchmaking_opponents = []

    # Iterate through users to find suitable matchmaking opponents
    for user in users_data:
        try:
            # Try to access necessary keys, handle gracefully if missing
            user_id_match = user.get("user_id") is not None and user["user_id"] != requesting_user["user_id"]
            map_id_match = user.get("map_id") == requesting_user.get("map_id")
            gamemode_id_match = user.get("gamemode_id") == requesting_user.get("gamemode_id")

            if user_id_match and map_id_match and gamemode_id_match:
                # Calculate the rating difference between the requesting user and potential opponent
                rating_difference = abs(requesting_user["rating"] - user["rating"])

                # Ensure that the rating difference is within a specified range (200 points)
                if rating_difference <= 200:
                    matchmaking_opponents.append(user)

                    # Break when there are 5 suitable opponents
                    if len(matchmaking_opponents) == 5:
                        break
        except KeyError:
            # Handle KeyError (missing key) gracefully
            continue

    if len(matchmaking_opponents) < 1:
        raise HTTPException(status_code=404, detail="Insufficient suitable opponents for matchmaking")

    return matchmaking_opponents


@matchmaking_router.post("/", response_model=list[dict])
def matchmaking(current_user: User = Depends(get_current_user), users_data=Depends(load_users_data)):
    matchmaking_opponents = find_matchmaking_opponents(current_user.user_id, users_data)
    return matchmaking_opponents
