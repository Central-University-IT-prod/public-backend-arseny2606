from sqlalchemy import Column, Integer, Text, ForeignKey, Date
from sqlalchemy.orm import relationship

from database.database_connector import SqlAlchemyBase


class TravelLocation(SqlAlchemyBase):
    __tablename__ = "travel_locations"

    id = Column(Integer, primary_key=True)
    city = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    latitude = Column(Text)
    longitude = Column(Text)
    travel_id = Column(Integer, ForeignKey("travels.id"))

    travel = relationship("Travel", back_populates="locations")

    def __repr__(self) -> str:
        return str(self.to_dict())
