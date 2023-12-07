from pydantic import BaseModel

class MatchmakingRequest(BaseModel):
    user_id : int