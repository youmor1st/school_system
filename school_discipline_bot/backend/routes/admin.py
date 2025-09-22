from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import DoesNotExist, IntegrityError

from backend.models import DisciplineRule, Teacher, Student
from backend.utils.security import get_password_hash

router = APIRouter()

# --- Pydantic Models for Rules ---

RuleIn_Pydantic = pydantic_model_creator(
    DisciplineRule, name="RuleIn", exclude_readonly=True
)
RuleOut_Pydantic = pydantic_model_creator(
    DisciplineRule, name="RuleOut"
)

# --- Pydantic Models for Teachers ---

Teacher_Pydantic = pydantic_model_creator(Teacher, name="TeacherOut", exclude=("password_hash",))
TeacherIn_Pydantic = pydantic_model_creator(
    Teacher, name="TeacherIn", exclude=("id", "telegram_id", "password_hash")
)

class TeacherCreate(TeacherIn_Pydantic):
    password: str

class TeacherUpdate(BaseModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None


# --- CRUD for Discipline Rules ---

@router.post(
    "/rules",
    response_model=RuleOut_Pydantic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new discipline rule",
    tags=["Admin - Rules"]
)
async def create_rule(rule: RuleIn_Pydantic):
    rule_obj = await DisciplineRule.create(**rule.dict(exclude_unset=True))
    return await RuleOut_Pydantic.from_tortoise_orm(rule_obj)


@router.get(
    "/rules",
    response_model=List[RuleOut_Pydantic],
    summary="Get all discipline rules",
    tags=["Admin - Rules"]
)
async def get_all_rules():
    return await RuleOut_Pydantic.from_queryset(DisciplineRule.all())


@router.get(
    "/rules/{rule_id}",
    response_model=RuleOut_Pydantic,
    summary="Get a specific discipline rule by ID",
    tags=["Admin - Rules"]
)
async def get_rule(rule_id: int):
    try:
        rule = await DisciplineRule.get(id=rule_id)
        return await RuleOut_Pydantic.from_tortoise_orm(rule)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with ID {rule_id} not found",
        )


@router.put(
    "/rules/{rule_id}",
    response_model=RuleOut_Pydantic,
    summary="Update a discipline rule",
    tags=["Admin - Rules"]
)
async def update_rule(rule_id: int, rule_details: RuleIn_Pydantic):
    try:
        await DisciplineRule.filter(id=rule_id).update(**rule_details.dict(exclude_unset=True))
        rule = await DisciplineRule.get(id=rule_id)
        return await RuleOut_Pydantic.from_tortoise_orm(rule)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with ID {rule_id} not found",
        )


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a discipline rule",
    tags=["Admin - Rules"]
)
async def delete_rule(rule_id: int):
    deleted_count = await DisciplineRule.filter(id=rule_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with ID {rule_id} not found",
        )
    return


# --- CRUD for Teachers ---

@router.post(
    "/teachers",
    response_model=Teacher_Pydantic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new teacher",
    tags=["Admin - Teachers"]
)
async def create_teacher(teacher: TeacherCreate):
    hashed_password = get_password_hash(teacher.password)
    teacher_data = teacher.dict(exclude={"password"})
    try:
        teacher_obj = await Teacher.create(**teacher_data, password_hash=hashed_password)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher with this username already exists.",
        )
    return await Teacher_Pydantic.from_tortoise_orm(teacher_obj)


@router.get(
    "/teachers",
    response_model=List[Teacher_Pydantic],
    summary="Get all teachers",
    tags=["Admin - Teachers"]
)
async def get_all_teachers():
    return await Teacher_Pydantic.from_queryset(Teacher.all())


@router.get(
    "/teachers/{teacher_id}",
    response_model=Teacher_Pydantic,
    summary="Get a specific teacher by ID",
    tags=["Admin - Teachers"]
)
async def get_teacher(teacher_id: int):
    try:
        teacher = await Teacher.get(id=teacher_id)
        return await Teacher_Pydantic.from_tortoise_orm(teacher)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with ID {teacher_id} not found",
        )


@router.put(
    "/teachers/{teacher_id}",
    response_model=Teacher_Pydantic,
    summary="Update a teacher",
    tags=["Admin - Teachers"]
)
async def update_teacher(teacher_id: int, teacher_details: TeacherUpdate):
    update_data = teacher_details.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    try:
        await Teacher.filter(id=teacher_id).update(**update_data)
        teacher = await Teacher.get(id=teacher_id)
        return await Teacher_Pydantic.from_tortoise_orm(teacher)
    except (DoesNotExist, IntegrityError) as e:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with ID {teacher_id} not found or username already exists.",
        )


@router.delete(
    "/teachers/{teacher_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a teacher",
    tags=["Admin - Teachers"]
)
async def delete_teacher(teacher_id: int):
    deleted_count = await Teacher.filter(id=teacher_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with ID {teacher_id} not found",
        )
    return


# --- Pydantic Models for Students ---

Student_Pydantic = pydantic_model_creator(Student, name="StudentOut", exclude=("password_hash",))
StudentIn_Pydantic = pydantic_model_creator(
    Student, name="StudentIn", exclude=("id", "telegram_id", "password_hash", "points")
)

class StudentCreate(StudentIn_Pydantic):
    password: str

class StudentUpdate(BaseModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None
    class_name: str | None = None
    points: int | None = None


# --- CRUD for Students ---

@router.post(
    "/students",
    response_model=Student_Pydantic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    tags=["Admin - Students"]
)
async def create_student(student: StudentCreate):
    hashed_password = get_password_hash(student.password)
    student_data = student.dict(exclude={"password"})
    try:
        student_obj = await Student.create(**student_data, password_hash=hashed_password)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this username already exists.",
        )
    return await Student_Pydantic.from_tortoise_orm(student_obj)


@router.get(
    "/students",
    response_model=List[Student_Pydantic],
    summary="Get all students",
    tags=["Admin - Students"]
)
async def get_all_students():
    return await Student_Pydantic.from_queryset(Student.all())


@router.get(
    "/students/{student_id}",
    response_model=Student_Pydantic,
    summary="Get a specific student by ID",
    tags=["Admin - Students"]
)
async def get_student(student_id: int):
    try:
        student = await Student.get(id=student_id)
        return await Student_Pydantic.from_tortoise_orm(student)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found",
        )


@router.put(
    "/students/{student_id}",
    response_model=Student_Pydantic,
    summary="Update a student",
    tags=["Admin - Students"]
)
async def update_student(student_id: int, student_details: StudentUpdate):
    update_data = student_details.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    if "password" in update_data and not update_data["password"]:
        del update_data["password"]

    try:
        await Student.filter(id=student_id).update(**update_data)
        student = await Student.get(id=student_id)
        return await Student_Pydantic.from_tortoise_orm(student)
    except (DoesNotExist, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found or username already exists.",
        )


@router.delete(
    "/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student",
    tags=["Admin - Students"]
)
async def delete_student(student_id: int):
    deleted_count = await Student.filter(id=student_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found",
        )
    return
