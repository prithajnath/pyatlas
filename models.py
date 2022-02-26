from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

user_subscription = Table(
    "user_subscriptions",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("subscription_id", Integer, ForeignKey("subscriptions.id")),
)


class Status(Base):
    __tablename__ = "statuses"
    id = Column(Integer, primary_key=True)
    twitter_id = Column(String)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    subscriptions = relationship(
        "Subscription", secondary=user_subscription, back_populates="users"
    )


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    users = relationship(
        "User", secondary=user_subscription, back_populates="subscriptions"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
