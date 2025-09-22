from fastapi import APIRouter

router = APIRouter()

# Placeholder for future authentication routes
@router.post("/login")
async def login():
    return {"message": "Login endpoint"}
