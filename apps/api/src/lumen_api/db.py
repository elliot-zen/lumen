from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from lumen_api.config import Settings, get_settings


class Base(DeclarativeBase):
    pass


def build_engine(settings: Settings | None = None):
    active_settings = settings or get_settings()
    return create_engine(active_settings.database_url, future=True)


def build_session_factory(settings: Settings | None = None):
    engine = build_engine(settings)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)


def init_database(settings: Settings | None = None) -> None:
    engine = build_engine(settings)
    Base.metadata.create_all(engine)


SessionLocal = build_session_factory()


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
