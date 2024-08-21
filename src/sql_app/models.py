from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Boolean, Text, ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase, 
    Mapped,
    mapped_column,
    relationship,
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    department: Mapped[str] = mapped_column(String(32), nullable=False)

    # 当前借用的物品
    borrowed_items: Mapped[List["Item"]] = relationship(
        "Item",
        primaryjoin="and_(User.id == Item.current_borrower_id, Item.status == False)",
        back_populates="borrowed_user",
        foreign_keys="Item.current_borrower_id"
    )

    # 历史归还的物品
    returned_items: Mapped[List["Item"]] = relationship(
        "Item",
        primaryjoin="and_(User.id == Item.previous_borrower_id, Item.status == True)",
        back_populates="returned_user",
        foreign_keys="Item.previous_borrower_id"
    )

class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True, deferred=True)

    # 借出时间
    borrowed_time: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # 归还时间
    returned_time: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # 当前借用用户ID
    current_borrower_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'), nullable=True)

    # 上一个借用用户ID（历史记录）
    previous_borrower_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'), nullable=True)

    # 当前借用用户
    borrowed_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[current_borrower_id],
        back_populates="borrowed_items"
    )

    # 上一个借用用户（历史记录）
    returned_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[previous_borrower_id],
        back_populates="returned_items"
    )
