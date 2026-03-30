from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext


# ==============================
# 🔐 JWT Configuration
# ==============================

SECRET_KEY = "your_secret_key"  # 👉 change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


# ==============================
# 🔑 Password Hashing Setup
# ==============================

# This handles password hashing using bcrypt
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==============================
# 🔓 OAuth2 Scheme (for Swagger auth)
# ==============================

# This tells FastAPI where the login endpoint is
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ==============================
# 🔐 Password Functions
# ==============================

def hash_password(plain_password: str) -> str:
    """
    Hash the plain password before storing in DB
    """
    # bcrypt supports only up to 72 bytes
    if len(plain_password.encode("utf-8")) > 72:
        plain_password = plain_password[:72]

    return password_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare plain password with hashed password
    """
    return password_context.verify(plain_password, hashed_password)


# ==============================
# 🎟️ JWT Token Creation
# ==============================

def create_access_token(data: dict) -> str:
    """
    Generate JWT token with expiry
    """
    token_data = data.copy()

    expiry_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data.update({"exp": expiry_time})

    jwt_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return jwt_token


# ==============================
# 🔍 Get Current User from Token
# ==============================

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decode JWT token and extract user info
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")
        role: str = payload.get("role")

        # Validate token payload
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {
            "username": username,
            "role": role
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ==============================
# 🛡️ Role-Based Access Control
# ==============================

def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Allow only admin users
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return current_user


def require_participant(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Allow only participant users
    """
    if current_user["role"] != "participant":
        raise HTTPException(status_code=403, detail="Participant access required")

    return current_user