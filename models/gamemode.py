from pydantic import BaseModel

class Gamemode(BaseModel):
    mode_id: int
    name: str