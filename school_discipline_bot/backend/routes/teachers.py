from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from tortoise.functions import Avg
from tortoise.expressions import Q

from backend.models import Teacher, Student, DisciplineRule, PointHistory
from backend.utils.security import get_current_user
from tortoise.contrib.pydantic import pydantic_model_creator

router = APIRouter()

from tortoise.transactions import in_transaction

# --- Pydantic Models ---

class PointAssignment(BaseModel):
    student_ids: List[int]
    rule_ids: List[int]
    comment: str

Student_Pydantic = pydantic_model_creator(Student, name="Student", exclude=("password_hash",))

class ClassPoints(BaseModel):
    class_name: str
    average_points: float

# --- Dependency to ensure user is a teacher ---

async def get_current_teacher(current_user: Union[Teacher, Student] = Depends(get_current_user)) -> Teacher:
    if not isinstance(current_user, Teacher):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    return current_user


# --- Teacher API Endpoints ---

@router.get("/classes", response_model=List[str], summary="Get all unique class names")
async def get_all_class_names(teacher: Teacher = Depends(get_current_teacher)):
    """
    Returns a list of all unique class names from the Student table.
    """
    class_names = await Student.all().distinct().values_list("class_name", flat=True)
    return class_names


@router.get("/students/by_class/{class_name}", response_model=List[Student_Pydantic], summary="Get students by class name")
async def get_students_by_class(class_name: str, teacher: Teacher = Depends(get_current_teacher)):
    """
    Returns a list of all students belonging to a specific class.
    """
    students = Student.filter(class_name=class_name)
    return await Student_Pydantic.from_queryset(students)


@router.get("/students/search", response_model=List[Student_Pydantic], summary="Search for students by name")
async def search_students(q: str = Query(..., min_length=1), teacher: Teacher = Depends(get_current_teacher)):
    """
    Searches for students by first or last name.
    """
    students = Student.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q)
    )
    return await Student_Pydantic.from_queryset(students)


@router.post("/points/assign", status_code=status.HTTP_201_CREATED, summary="Assign points to students")
async def assign_points(assignment: PointAssignment, teacher: Teacher = Depends(get_current_teacher)):
    """
    Assigns points to students based on rules. This endpoint is flexible:
    - One student, one rule
    - One student, multiple rules
    - Multiple students, one rule
    - Multiple students, multiple rules (all rules applied to all students)
    """
    if not assignment.student_ids or not assignment.rule_ids:
        raise HTTPException(status_code=400, detail="Student and rule IDs cannot be empty.")

    async with in_transaction():
        rules = await DisciplineRule.filter(id__in=assignment.rule_ids)
        if len(rules) != len(assignment.rule_ids):
            raise HTTPException(status_code=404, detail="One or more rules not found")

        students_to_update = await Student.filter(id__in=assignment.student_ids)
        if len(students_to_update) != len(assignment.student_ids):
            raise HTTPException(status_code=404, detail="One or more students not found")

        history_records = []
        total_points_map = {student.id: 0 for student in students_to_update}

        for rule in rules:
            for student in students_to_update:
                total_points_map[student.id] += rule.points
                history_records.append(
                    PointHistory(
                        student_id=student.id,
                        teacher_id=teacher.id,
                        rule_id=rule.id,
                        points_changed=rule.points,
                        comment=assignment.comment
                    )
                )

        # Update student points
        for student in students_to_update:
            student.points += total_points_map[student.id]
            await student.save(update_fields=["points"])

        # Bulk create history records
        await PointHistory.bulk_create(history_records)

    return {"message": f"Points assigned successfully to {len(students_to_update)} students."}


@router.get("/leaderboard/students", response_model=List[Student_Pydantic], summary="Get top 5 students")
async def get_student_leaderboard(teacher: Teacher = Depends(get_current_teacher)):
    """
    Returns the top 5 students with the highest points.
    """
    top_students = await Student.all().order_by("-points").limit(5)
    return await Student_Pydantic.from_queryset(top_students)


@router.get("/leaderboard/classes", response_model=List[ClassPoints], summary="Get top 3 classes")
async def get_class_leaderboard(teacher: Teacher = Depends(get_current_teacher)):
    """
    Returns the top 3 classes with the highest average points.
    """
    class_avg_points = await Student.all() \
        .group_by("class_name") \
        .annotate(average_points=Avg("points")) \
        .order_by("-average_points") \
        .limit(3) \
        .values("class_name", "average_points")

    return [ClassPoints(**data) for data in class_avg_points]
