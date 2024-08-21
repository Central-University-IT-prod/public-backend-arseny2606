from sqlalchemy import Column, Integer, Text, BigInteger
from sqlalchemy.orm import relationship

from database.database_connector import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(Text(), nullable=True)
    age = Column(Integer, nullable=True)
    city = Column(Text(), nullable=True)
    country = Column(Text(), nullable=True)
    bio = Column(Text(), nullable=True)

    created_travels = relationship("Travel", back_populates="owner")
    access_travels = relationship("Travel", secondary="travel_access", back_populates="access_users")

    def __repr__(self) -> str:
        return str(self.id)
