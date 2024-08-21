from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Table, BigInteger

from database.database_connector import SqlAlchemyBase

travel_access = Table(
    "travel_access",
    SqlAlchemyBase.metadata,
    Column("user_id", BigInteger, ForeignKey("users.id"), primary_key=True),
    Column("travel_id", Integer, ForeignKey("travels.id"), primary_key=True),
    UniqueConstraint("travel_id", "user_id", name="_travel_user_uc"),
)
