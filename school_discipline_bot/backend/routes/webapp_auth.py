from datetime import timedelta
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.models import Student, Teacher, Admin
from backend.utils.security import create_access_token, verify_password, get_current_user
from tortoise.contrib.pydantic import pydantic_model_creator

router = APIRouter()

# Pydantic models for response
Student_Pydantic = pydantic_model_creator(Student, name="StudentAuth", exclude=("password_hash",))
Teacher_Pydantic = pydantic_model_creator(Teacher, name="TeacherAuth", exclude=("password_hash",))
Admin_Pydantic = pydantic_model_creator(Admin, name="AdminAuth", exclude=("password_hash",))


async def authenticate_user(username: str, password: str) -> Union[Student, Teacher, Admin, None]:
    """
    Finds a user in the database and verifies their password.
    Checks Student, Teacher, and Admin tables.
    """
    user = await Student.get_or_none(username=username)
    if not user:
        user = await Teacher.get_or_none(username=username)
    if not user:
        user = await Admin.get_or_none(username=username)

    if not user:
        return None  # User not found in any table

    if not verify_password(password, user.password_hash):
        return None  # Invalid password

    return user


@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Logs in a user and returns an access token.
    This is the primary authentication endpoint.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Determine the role based on the model type
    if isinstance(user, Student):
        role = "student"
    elif isinstance(user, Teacher):
        role = "teacher"
    else:
        role = "admin"

    # Create the access token
    access_token_expires = timedelta(minutes=30)  # Or get from config
    access_token = create_access_token(
        data={"sub": str(user.id), "role": role}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "role": role}


@router.get("/me", response_model=Union[Student_Pydantic, Teacher_Pydantic, Admin_Pydantic])
async def read_users_me(current_user: Union[Student, Teacher, Admin] = Depends(get_current_user)):
    """
    Returns the profile of the currently authenticated user.
    """
    # The `get_current_user` dependency handles token validation and user fetching.
    return current_user
