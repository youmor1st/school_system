from fastapi import APIRouter

router = APIRouter()

# Placeholder for admin-related API endpoints
@router.get("/students")
async def get_all_students():
    return {"message": "Admin: get all students endpoint"}
