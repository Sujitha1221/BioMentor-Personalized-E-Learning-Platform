from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from service import UserService, UserCreate, UserUpdate
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

user_service = UserService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class LoginRequest(BaseModel):
    username: str
    password: str

class LogoutRequest(BaseModel):
    token: str


# User Routes
@app.post("/users/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    return user_service.create_user(user)

@app.get("/users/{username}")
def get_user(username: str):
    user = user_service.get_user(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@app.put("/users/{username}")
def update_user(username: str, user_update: UserUpdate):
    return user_service.update_user(username, user_update)

@app.delete("/users/{username}")
def delete_user(username: str):
    result = user_service.delete_user(username)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return {"message": "User deleted successfully"}


@app.post("/login")
def login(user: LoginRequest):
    token = user_service.login(user.username, user.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}

@app.post("/logout")
def logout(logout_data: LogoutRequest):
    user_service.logout(logout_data.token)
    return {"message": "User logged out successfully"}
