import datetime
from typing import Final

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import jwt, JWTError
from sqlalchemy.orm import Session

from saas_app.models import User
from saas_app.types import Token, TokenDataT
from saas_app.db_connection import get_session
from saas_app.operations import pwd_context, get_user

SECRET_KEY : Final[str] = "a_very_secret_key"
ALGORITHM : Final[str] = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES : Final[int] = 30


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(
    db: Session,
    username_or_email: str,
    password: str,
) -> User | None:
    """
    Authenticate a user by username or email and password.

    Args:
        db (Session): SQLAlchemy database session.
        username_or_email (str): The username or email of the user.
        password (str): The password of the user.

    Returns:
        User | None: The authenticated User object if credentials are valid, otherwise None.
    """    
    user = get_user(db, username_or_email)

    if not user or not pwd_context.verify(
        password, user.hashed_password
    ):
        return None
    return user


def create_access_token(data: TokenDataT) -> str:
    """
    Create a JWT access token.

    Args:
        data (dict): The data to encode in the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode: TokenDataT = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> TokenDataT | None:
    """
    Decode a JWT access token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict | None: The decoded token data if valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
def get_user_from_token(db: Session, token: str) -> User | None:
    """
    Retrieve a user from the database using a JWT token.

    Args:
        db (Session): SQLAlchemy database session.
        token (str): The JWT token.

    Returns:
        User | None: The User object if the token is valid and user exists, otherwise None.
    """
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        return None
    username = payload["sub"]
    return get_user(db, username)


@router.post("/token", response_model=Token)
def get_user_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session),
):
    user = get_user_from_token(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "description": f"{user.username} authorized.",
    }