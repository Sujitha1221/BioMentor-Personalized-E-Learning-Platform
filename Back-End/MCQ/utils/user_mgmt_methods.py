from fastapi import HTTPException, Header
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

# JWT Secret & Algorithm
SECRET_KEY = "E-learningplatform2k25"  # Change this to a strong secret key
ALGORITHM = "HS256"

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
    

def get_current_user(authorization: str = Header(None)):
    """Extract token from Authorization header and verify JWT."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization.replace("Bearer ", "")  # Remove "Bearer " prefix

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id  # ✅ Return user ID for dependency injection
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")