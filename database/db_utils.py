from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from database.models import Base, User


class DuplicateEmailError(ValueError):
    """Raised when a registration email is already in use."""


def _engine_for(database_url):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, future=True)


def initialize_database(database_url):
    engine = _engine_for(database_url)
    Base.metadata.create_all(engine)
    engine.dispose()


def create_user(database_url, registration):
    engine = _engine_for(database_url)
    session_factory = sessionmaker(bind=engine, future=True)
    values = dict(registration)
    values["email"] = values["email"].strip().lower()
    values["date_of_birth"] = date.fromisoformat(values["date_of_birth"])
    values["password_hash"] = generate_password_hash(values.pop("password"))
    values.pop("confirm_password")
    values["terms_accepted"] = bool(values["terms_accepted"])
    user = User(**values)

    try:
        with session_factory.begin() as session:
            session.add(user)
            session.flush()
            user_id = user.id
    except IntegrityError as error:
        if "email" in str(error).lower() or "users.email" in str(error).lower():
            raise DuplicateEmailError("An account with this email already exists.") from error
        raise
    finally:
        engine.dispose()
    return user_id


def find_user_by_email(database_url, email):
    engine = _engine_for(database_url)
    session_factory = sessionmaker(bind=engine, future=True)
    try:
        with session_factory() as session:
            return session.scalar(select(User).where(User.email == email.strip().lower()))
    finally:
        engine.dispose()


def find_user_by_id(database_url, user_id):
    engine = _engine_for(database_url)
    session_factory = sessionmaker(bind=engine, future=True)
    try:
        with session_factory() as session:
            return session.get(User, user_id)
    finally:
        engine.dispose()
