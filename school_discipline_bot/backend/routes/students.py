from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, status

from backend.models import Teacher, Student, PointHistory
from backend.utils.security import get_current_user
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel

router = APIRouter()

# --- Pydantic Models ---

# Basic student profile
Student_Pydantic = pydantic_model_creator(Student, name="StudentProfile", exclude=("password_hash",))

# Custom Pydantic model for point history to exclude teacher details
class PointHistoryEntry(BaseModel):
    id: int
    points_changed: int
    comment: str
    rule_name: str
    created_at: str

    class Config:
        orm_mode = True

# --- Dependency to ensure user is a student ---

async def get_current_student(current_user: Union[Teacher, Student] = Depends(get_current_user)) -> Student:
    if not isinstance(current_user, Student):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    return current_user


# --- Student API Endpoints ---

@router.get("/me", response_model=Student_Pydantic, summary="Get current student's profile")
async def get_student_profile(student: Student = Depends(get_current_student)):
    """
    Returns the profile of the currently authenticated student.
    """
    return student


@router.get("/me/history", response_model=List[PointHistoryEntry], summary="Get current student's point history")
async def get_student_history(student: Student = Depends(get_current_student)):
    """
    Returns the point history for the currently authenticated student.
    The teacher who assigned the points is not included.
    """
    history = await PointHistory.filter(student=student).order_by("-created_at").prefetch_related("rule")

    # Manually construct the response to control the fields
    response = []
    for entry in history:
        response.append(
            PointHistoryEntry(
                id=entry.id,
                points_changed=entry.points_changed,
                comment=entry.comment,
                rule_name=entry.rule.name,
                created_at=entry.created_at.isoformat()
            )
        )
    return response


@router.get("/leaderboard", response_model=List[Student_Pydantic], summary="Get top 5 students leaderboard")
async def get_student_leaderboard(student: Student = Depends(get_current_student)):
    """
    Returns the top 5 students with the highest points.
    This is the same leaderboard visible to teachers.
    """
    top_students = await Student.all().order_by("-points").limit(5)
    return await Student_Pydantic.from_queryset(top_students)
