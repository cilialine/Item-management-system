from sqlalchemy.orm import Session
from datetime import datetime

from . import models
from . import schemas
from typing import Optional

# 增
def create_item(db: Session, item: schemas.CreateItem):
    db_item = models.Item(
        name=item.name, 
        type=item.type,
        details=item.details
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# 删
def delete_item(db: Session, item_id: int) -> Optional[schemas.SItem]:
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db_item_data = schemas.SItem.model_validate(db_item)
        db.delete(db_item)
        db.commit()
        return db_item_data
    return None


# 改
def update_item(db: Session,item_id: int, item : schemas.ItemUpdate) -> Optional[models.Item]:
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db_item.name = item.name
        db_item.type = item.type
        db_item.details = item.details
        db_item.status = item.status
        db.commit()
        db.refresh(db_item)
        return db_item
    return db_item
    
    
def update_borrowed_item(db: Session, item_id: int, user_id: int) -> Optional[models.Item]:
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item and db_item.user_id == user_id and db_item.status == False:
        db_item.status = True
        db_item.borrowed_time = datetime.now() 
        db_item.current_borrower_id = user_id
        db.commit()
        db.refresh(db_item)
        return db_item
    return None


def update_returned_item(db: Session, item_id: int, user_id: int) -> Optional[models.Item]:
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item and db_item.user_id == user_id and db_item.status == True:
        db_item.status = False  
        db_item.returned_time = datetime.now()
        db_item.previous_borrower_id = db_item.current_borrower_id
        db_item.current_borrower_id = None
        db.commit()
        db.refresh(db_item)
        return db_item
    return None


# 查
def get_user(db : Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_item(db : Session,item_id : int ) -> Optional[models.Item]:
    return db.query(models.Item).filter(models.Item.id == item_id).first()
    

def  get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def get_items(db: Session, skip: int = 0, limit: int = 100)-> list[models.Item]:
    return db.query(models.Item).offset(skip).limit(limit).all()


def get_borrowed_items(db: Session, user_id: int) -> list[models.Item]:
    return db.query(models.Item).filter(models.Item.user_id == user_id, models.Item.status == False).all()


def get_returned_items(db: Session, user_id: int) -> list[models.Item]:
    return db.query(models.Item).filter(models.Item.user_id == user_id, models.Item.status == True).all()


def get_all_borrowed_items(db: Session, skip: int = 0, limit: int = 100) -> list[models.Item]:
    return db.query(models.Item).filter(models.Item.status == False).offset(skip).limit(limit).all()


def get_all_returned_items(db: Session, skip: int = 0, limit: int = 100) -> list[models.Item]:
    return db.query(models.Item).filter(models.Item.status == True).offset(skip).limit(limit).all()