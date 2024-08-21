from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship

from database.database_connector import SqlAlchemyBase


class TravelNote(SqlAlchemyBase):
    __tablename__ = "travel_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Text, primary_key=True)
    file_name = Column(Text)
    is_public = Column(Boolean)
    travel_id = Column(Integer, ForeignKey("travels.id"), primary_key=True)

    travel = relationship("Travel", back_populates="notes")

    __table_args__ = (
        UniqueConstraint("file_id", "travel_id", name="_note_travel_uc"),
    )

    def __repr__(self) -> str:
        return str(self.to_dict())
