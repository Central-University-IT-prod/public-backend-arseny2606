from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint, BigInteger
from sqlalchemy.orm import relationship

from database.database_connector import SqlAlchemyBase


class Travel(SqlAlchemyBase):
    __tablename__ = "travels"

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    description = Column(Text, nullable=True)
    owner_id = Column(BigInteger, ForeignKey("users.id"))

    owner = relationship("User", back_populates="created_travels")
    locations = relationship("TravelLocation", back_populates="travel", cascade="all,delete")
    access_users = relationship("User", secondary="travel_access", back_populates="access_travels")
    notes = relationship("TravelNote", back_populates="travel", cascade="all,delete")

    __table_args__ = (UniqueConstraint('title', 'owner_id', name='_travel_uc'),)

    def __repr__(self) -> str:
        return str(self.to_dict())
