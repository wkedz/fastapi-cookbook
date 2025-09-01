from contextlib import asynccontextmanager
from sqlalchemy.orm import Session


from fastapi import FastAPI, Depends, HTTPException, status

from saas_app.db_connection import get_engine, get_session
from saas_app.models import Base
from saas_app.operations import add_user
from saas_app.responses import (
    UserCreateBody,
    UserCreateResponse,
    ResponseCreateUser,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=get_engine())
    yield

app = FastAPI(
    title="SaaS App",
    lifespan=lifespan,
    )


@app.post(
    "/register/user",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCreateUser,
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "The user already exists"
        }
    }
)
def register(
    user: UserCreateBody,
    session: Session = Depends(get_session),
) -> dict[str, UserCreateResponse]:
    new_user = add_user(
        session,
        **user.model_dump()
    )
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user already exists"
        )
    user_response = UserCreateResponse(
        username=new_user.username,
        email=new_user.email,
    )
    return ResponseCreateUser(message="user created", user=user_response).model_dump()