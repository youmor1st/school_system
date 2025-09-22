import asyncio
import argparse
from tortoise import Tortoise

from backend.models import Admin
from backend.utils.security import get_password_hash
from backend.config import TORTOISE_ORM


async def create_admin(username, password, first_name, last_name):
    """
    Initializes the database connection and creates an admin user.
    """
    print("Initializing database...")
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    print(f"Checking if admin '{username}' already exists...")
    if await Admin.exists(username=username):
        print(f"Admin with username '{username}' already exists. Aborting.")
        return

    print("Hashing password...")
    hashed_password = get_password_hash(password)

    print("Creating admin user...")
    await Admin.create(
        username=username,
        password_hash=hashed_password,
        first_name=first_name,
        last_name=last_name
    )
    print(f"Successfully created admin user '{username}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new admin user.")
    parser.add_argument("username", type=str, help="The username for the new admin.")
    parser.add_argument("password", type=str, help="The password for the new admin.")
    parser.add_argument("--first_name", type=str, default="Admin", help="The admin's first name.")
    parser.add_argument("--last_name", type=str, default="User", help="The admin's last name.")

    args = parser.parse_args()

    asyncio.run(create_admin(args.username, args.password, args.first_name, args.last_name))
