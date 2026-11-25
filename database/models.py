from sqlalchemy import Boolean, Column, Date, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(254), nullable=False, unique=True, index=True)
    mobile_number = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    gender = Column(String(20), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    address = Column(String(500), nullable=False)
    country = Column(String(80), nullable=False)
    state = Column(String(80), nullable=False)
    city = Column(String(80), nullable=False)
    postal_code = Column(String(20), nullable=False)
    terms_accepted = Column(Boolean, nullable=False, default=False)
