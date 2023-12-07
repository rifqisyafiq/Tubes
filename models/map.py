from pydantic import BaseModel

class Map(BaseModel):
    mapid: int
    name: str