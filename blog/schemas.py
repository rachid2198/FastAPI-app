from pydantic import BaseModel
from typing import Optional

class Blog(BaseModel):
    title:str
    body:Optional[str]

class ShowBlog(BaseModel):
    title:str
    body:Optional[str]
    
    class Config():
        orm_mode=True