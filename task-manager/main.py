
from fastapi import Depends, HTTPException, FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
from security import (
    UserInDB,
    fake_token_generator,
    fakely_hash_password,
    fake_users_db,
    get_user_from_token,
    User
)
from routers import tasks

# Custom OpenAPI schema to remove the /token endpoint from the documentation
# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title="Customized Title",
#         version="2.0.0",
#         description="This is a custom OpenAPI schema",
#         routes=app.routes,
#     )
#     del openapi_schema["paths"]["/token"]
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

app = FastAPI(
    title="Task Manager API",
    description="This is a task management API",
    version="0.1.0",
)

app.include_router(tasks.router)
#app.openapi = custom_openapi

@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Manager API!"}

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
        )
    user = UserInDB(**user_dict)
    hashed_password = fakely_hash_password(
        form_data.password
    )
    if not hashed_password == user.hashed_password:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
        )
    token = fake_token_generator(user)
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/users/me", response_model=User)
def read_users_me(
    current_user: User = Depends(get_user_from_token),
):
    return current_user