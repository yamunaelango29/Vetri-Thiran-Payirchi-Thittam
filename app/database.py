from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

from .config import BASE_DIR, get_settings

settings = get_settings()

# Ensure the local data directory exists for the default SQLite setup.
if settings.database_url.startswith("sqlite:///"):
    db_relative = settings.database_url.replace("sqlite:///", "", 1)
    db_path = Path(db_relative)
    if not db_path.is_absolute():
        db_path = BASE_DIR / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(String(50))
    intensity: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    plan: Mapped[Optional["WorkoutPlan"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    original_plan: Mapped[str] = mapped_column(Text)
    updated_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nutrition_tip: Mapped[str] = mapped_column(Text)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship(back_populates="plan")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_user(db: Session, username: str, user_id: str, age: int, weight: float, goal: str, intensity: str) -> User:
    user = db.scalar(select(User).where(User.user_id == user_id))
    if user:
        user.username = username
        user.age = age
        user.weight = weight
        user.goal = goal
        user.intensity = intensity
    else:
        user = User(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user


def save_plan(db: Session, user: User, original_plan: str, nutrition_tip: str) -> WorkoutPlan:
    plan = user.plan
    if plan is None:
        plan = WorkoutPlan(
            user_id=user.id,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )
        db.add(plan)
    else:
        plan.original_plan = original_plan
        plan.updated_plan = None
        plan.feedback = None
        plan.nutrition_tip = nutrition_tip
        plan.updated_at = None

    db.commit()
    db.refresh(plan)
    return plan


def update_plan(db: Session, user_id: str, updated_plan: str, feedback: str, nutrition_tip: str | None = None) -> WorkoutPlan | None:
    user = get_user(db, user_id)
    if user is None or user.plan is None:
        return None

    user.plan.updated_plan = updated_plan
    user.plan.feedback = feedback
    user.plan.updated_at = datetime.now(timezone.utc)
    if nutrition_tip:
        user.plan.nutrition_tip = nutrition_tip

    db.commit()
    db.refresh(user.plan)
    return user.plan


def get_user(db: Session, user_id: str) -> User | None:
    return db.scalar(select(User).where(User.user_id == user_id))


def get_original_plan(db: Session, user_id: str) -> str | None:
    user = get_user(db, user_id)
    return user.plan.original_plan if user and user.plan else None


def get_all_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())


def delete_user(db: Session, user_id: str) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
