from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from saas_app.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_user(
        session: Session,
        username: str,
        password: str,
        email: str,
) -> User | None:
    hashed_password = pwd_context.hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
    )
    session.add(db_user)
    try:
        session.commit()
        # After you commit a new object to the database, the object in memory may not have all the latest data from the database.
        # For example, fields like id (auto-incremented primary key) or timestamps that are set by the database won't be populated until after the commit.
        # tells SQLAlchemy to reload the object from the database, ensuring all fields (including those set by the database) are up-to-date in your Python object.
        session.refresh(db_user)
        return db_user
    except IntegrityError:
        session.rollback()
        return None