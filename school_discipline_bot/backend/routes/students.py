from fastapi import APIRouter

router = APIRouter()

# Placeholder for student-related API endpoints
@router.get("/")
async def get_student_info():
    return {"message": "Student info endpoint"}
