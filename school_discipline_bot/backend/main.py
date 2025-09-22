from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from backend.routes import webapp_auth, students, teachers, admin
from backend.config import TORTOISE_ORM

app = FastAPI(title="School Discipline Bot API")

# Include routers
app.include_router(webapp_auth.router, prefix="/auth", tags=["WebApp Auth"])
app.include_router(students.router, prefix="/students", tags=["Students"])
app.include_router(teachers.router, prefix="/teachers", tags=["Teachers"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.get("/")
async def root():
    return {"message": "Welcome to the School Discipline Bot Backend"}


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # This will create the tables on startup
    add_exception_handlers=True,
)
