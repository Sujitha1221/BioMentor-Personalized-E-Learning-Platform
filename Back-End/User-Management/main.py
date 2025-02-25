from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from service import UserService, UserCreate, UserUpdate
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

user_service = UserService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend URL for better security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Define login & logout request models
class LoginRequest(BaseModel):
    email: str  # Changed from username to email
    password: str

class LogoutRequest(BaseModel):
    token: str


# User Routes
@app.post("/users/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    return user_service.create_user(user)

@app.get("/users/{email}")
def get_user(email: str):
    user = user_service.get_user(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@app.put("/users/{email}")
def update_user(email: str, user_update: UserUpdate):
    return user_service.update_user(email, user_update)

@app.delete("/users/{email}")
def delete_user(email: str):
    result = user_service.delete_user(email)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return {"message": "User deleted successfully"}


@app.post("/login")
def login(user: LoginRequest):
    token = user_service.login(user.email, user.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}

@app.post("/logout")
def logout(logout_data: LogoutRequest):
    user_service.logout(logout_data.token)
    return {"message": "User logged out successfully"}
