import os
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from dotenv import load_dotenv

# It's better to load env variables at the very beginning
load_dotenv()

from backend.routes import webapp_auth, students, teachers, admin

app = FastAPI(title="School Discipline Bot API")

# Include routers
app.include_router(webapp_auth.router, prefix="/auth", tags=["WebApp Auth"])
app.include_router(students.router, prefix="/students", tags=["Students"])
app.include_router(teachers.router, prefix="/teachers", tags=["Teachers"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.get("/")
async def root():
    return {"message": "Welcome to the School Discipline Bot Backend"}


TORTOISE_ORM = {
    "connections": {"default": os.getenv("DATABASE_URL")},
    "apps": {
        "models": {
            "models": ["backend.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True, # This will create the tables on startup
    add_exception_handlers=True,
)
