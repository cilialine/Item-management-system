from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    type: str
    details: Optional[str]


class CreateItem(ItemBase):
    pass


class ItemUpdate(ItemBase):
    __pydantic_fields_set__

class SItem(ItemBase):
    id: int
    status: bool
    
    current_borrower_id: Optional[int] = None
    borrowed_time: Optional[datetime] = None  
    
    previous_borrower_id: Optional[int]= None
    returned_time: Optional[datetime] = None
    
    
    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    department: str

class CreateUser(UserBase):
    pass

class SUser(UserBase):
    id: int
    borrowed_items: List[SItem] = None  
    returned_items: List[SItem] = None 

    class Config:
        orm_mode = True



# list[item]还未解决
# 未加入id