from sqlalchemy import create_engine, NullPool
from sqlalchemy.orm import sessionmaker, declarative_base

import config


engine = create_engine(config.database_url, poolclass=NullPool, echo=False)
SqlAlchemyBase = declarative_base()
session_maker = sessionmaker(engine, expire_on_commit=False)


def load_models():
    from database.models import User # noqa: unused
    from database.models import TravelLocation  # noqa: unused
    from database.models import Travel # noqa: unused
    from database.models import travel_access # noqa: unused
    from database.models import TravelNote # noqa: unused


def get_session():
    """
    Create session for work with database
    :return: Session
    """
    with session_maker() as session:
        return session


def init_models() -> None:
    load_models()
    with engine.begin() as conn:
        SqlAlchemyBase.metadata.create_all(conn)
