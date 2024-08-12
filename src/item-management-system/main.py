"""
Main module for the Item Managemen System API.
"""
import os
from typing import Literal,Annotated
from fastapi.middleware.cors import CORSMiddleware
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    BackgroundTasks, 
    Header,
    )

from sql_app import * 


# 创建数据库表 后续优化
Base.metadata.create_all(bind=engine)
PASSWD = os.getenv("PASSWD")

app = FastAPI(
    title="Item Managemen System",
    description="2024 Summer Vacation Item Managemen System Backend Api",
    version="0.1",
)


#CORS 当前未实装
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.get("/")
async def read_root() -> Literal["Hello, World"]:
    """
    Root path of the API. To check if the API is running.
    """
    return "Hello, World"


# 创建新物品
@app.post("/users/{user_id}/items/", response_model=SItem)
def create_a_item(
    item: CreateItem, db: Session = Depends(get_db),
    authorization: Annotated[str | None, Header()] = None,
):
    """
    Create a new item. Requires authentication.
    """
    
    token = authorization
    
    if token != PASSWD:
        raise HTTPException(status_code=403, detail="Invalid Cookie!")
       
    
    return create_item(db=db, item=item)


# 删除物品
@app.delete("/items/{item_id}", status_code=204)
def delete_a_item(
    item_id: int, db: Session = Depends(get_db),
    authorization: Annotated[str | None, Header()] = None,
):
    
    """
    Delete an item by ID. Requires authentication.
    """
    
    token = authorization
    
    if token != PASSWD:
        raise HTTPException(status_code=403, detail="Invalid Cookie!")
    
    db_item = get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    delete_item(db=db, item_id=item_id)
    return {"message": "Item deleted successfully"}


# 获取用户信息
@app.get("/users/{user_id}", response_model=SUser)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a user data.
    """
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# 获取所有用户信息
@app.get("/users/", response_model=list[SUser])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all users data.
    """
    users = get_users(db, skip=skip, limit=limit)
    return users


# 获取单个物品信息
@app.get("/items/{item_id}", response_model=SItem)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """
    Get a item data.
    """
    db_item = get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="item not found")
    return db_item


# 获取所有物品信息
@app.get("/items/", response_model=list[SItem])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all items data.
    """
    items = get_items(db, skip=skip, limit=limit)
    return items


# 获取单个用户所有借出物品信息
@app.get("/users/{user_id}/borrowed_items/", response_model=list[SItem])
def read_borrowed_items(user_id: int, db: Session = Depends(get_db)):
    """
    Get a user's borrowed_items data.
    """
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    items = get_borrowed_items(db, user_id=user_id)
    return items


# 获取单个用户所有归还物品信息
@app.get("/users/{user_id}/returned_items/", response_model=list[SItem])
def read_returned_items(user_id: int, db: Session = Depends(get_db)):
    """
    Get a user's returned_items data.
    """
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    items = get_returned_items(db, user_id=user_id)
    return items


# 获取所有被借出物品信息
@app.get("/items/borrowed/", response_model=list[SItem])
def read_all_borrowed_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all borrowed_items data.
    """
    items = get_all_borrowed_items(db, skip=skip, limit=limit)
    return items


# 获取所有已归还物品信息
@app.get("/items/returned/", response_model=list[SItem])
def read_all_returned_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all returned_items data.
    """
    items = get_all_returned_items(db, skip=skip, limit=limit)
    return items


# 更新物品为借出状态
@app.put("/items/{item_id}/borrow/", response_model=SItem)
def update_borrowed_a_item(item_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Update the item's status to be borrowed(False)
    """
    db_item = update_borrowed_item(db, item_id=item_id, user_id=user_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found or cannot be borrowed")
    return db_item


# 更新物品为归还状态
@app.put("/items/{item_id}/return/", response_model=SItem)
def update_returned_a_item(item_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Update the item's status to be borrowed(True)
    """
    db_item = update_returned_item(db, item_id=item_id, user_id=user_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found or cannot be returned")
    return db_item


# 更新物品信息
@app.put("/items/{item_id}", status_code=200, response_model=SItem)
async def update_item_info(
    item_id: int,
    item_update: ItemUpdate,
    background_tasks: BackgroundTasks,
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Update the details of an item. Requires authentication.
    """
    token = authorization

    if token != PASSWD:
        raise HTTPException(status_code=403, detail="Invalid Cookie!")

    db_item = update_item(db, item_id=item_id, item=item_update)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.commit()
    db.refresh(db_item)

    return db_item


# 登录
@app.post("/login")
async def check_passwd(passwd: str):
    """
    Check the password, and later the same passwd will be used to update the booth status as the token in Cookies

    Args:
        passwd: The password to check, str
    """
    if passwd == PASSWD:
        return {"message": "Login successful!"}
    else:
        raise HTTPException(status_code=403, detail="Invalid Cookie!")