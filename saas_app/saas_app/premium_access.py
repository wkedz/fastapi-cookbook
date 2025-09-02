from fastapi import APIRouter, Depends, status
from fastapi import HTTPException
from sqlalchemy.orm import Session


from saas_app.db_connection import get_session
from saas_app.responses import ResponseCreateUser, UserCreateBody, UserCreateResponse
from saas_app.models import Role
from saas_app.operations import add_user

router = APIRouter()

@router.post("/register/premium-user",
             status_code=status.HTTP_201_CREATED,
             response_model=ResponseCreateUser
            )
def register_premium_user(
    user: UserCreateBody,
    db: Session = Depends(get_session),
):
    db_user = add_user(
        db,
        username=user.username,
        password=user.password,
        email=user.email,
        role=Role.premium,  # Set role to premium
    )
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )
    return ResponseCreateUser(
        message="premium user created",
        user=UserCreateResponse(
            username=db_user.username,
            email=db_user.email,
        )
    )