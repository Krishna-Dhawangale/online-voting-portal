import os

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    func,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///online_voting.sqlite"

engine: Engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()

voters = Table(
    "voters",
    metadata,
    Column("voter_id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("aadhaar", String(12), nullable=False, unique=True),
    Column("mobile", String(10), nullable=False),
    Column("password", String(255), nullable=False),
    Column("otp", String(6), nullable=True),
    Column("has_voted", Boolean, nullable=False, server_default="0"),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

candidates = Table(
    "candidates",
    metadata,
    Column("candidate_id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("party", String(100), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

votes = Table(
    "votes",
    metadata,
    Column("vote_id", Integer, primary_key=True, autoincrement=True),
    Column("voter_id", Integer, ForeignKey("voters.voter_id", ondelete="CASCADE")),
    Column("candidate_id", Integer, ForeignKey("candidates.candidate_id", ondelete="CASCADE")),
    Column("voted_at", DateTime(timezone=True), server_default=func.now()),
)

admin = Table(
    "admin",
    metadata,
    Column("admin_id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(50), nullable=False, unique=True),
    Column("password", String(255), nullable=False),
)


def init_db() -> None:
    metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine, future=True)


def get_voter_by_credentials(session: Session, aadhaar: str, password: str):
    stmt = select(voters).where(voters.c.aadhaar == aadhaar, voters.c.password == password)
    return session.execute(stmt).mappings().first()

