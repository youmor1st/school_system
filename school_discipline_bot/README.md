# School Discipline Bot

This project is a Telegram Mini App designed to manage student discipline points in a school. It consists of a FastAPI backend API and an Aiogram Telegram bot.

## Project Structure

-   `/backend`: FastAPI application (API)
-   `/bot`: Aiogram application (Telegram Bot)
-   `/docker-compose.yml`: Defines the services for the database, backend, and bot.
-   `/requirements.txt`: Python dependencies for the project.

## Getting Started

### 1. Set Up Environment Variables

First, you need to create a `.env` file for your environment variables. You can copy the example file:

```bash
cp .env.example .env
```

Now, open the `.env` file and fill in the required values, especially `BOT_TOKEN` with the token you get from BotFather on Telegram.

### 2. Run the Application

This project uses Docker Compose to run all the services (database, backend, bot). Make sure you have Docker installed and running.

To build and start all services, run the following command from this directory:

```bash
docker-compose up --build -d
```

The services will now be running in the background.
- The **Backend API** will be accessible at `http://localhost:8000`.
- The **API documentation** (Swagger UI) will be at `http://localhost:8000/docs`.

### 3. Create the First Admin User

The system has three roles: Admin, Teacher, and Student. To manage the application, you first need to create an administrator account. This is done using a command-line script.

While the services are running, execute the following command in your terminal. Replace `admin_username` and `admin_password` with your desired credentials.

```bash
docker-compose exec backend python backend/create_admin.py admin_username admin_password
```

For example:
```bash
docker-compose exec backend python backend/create_admin.py superadmin MySecurePassword123
```

You can now use these credentials to log in via the API (e.g., at `http://localhost:8000/docs`) and get an access token to use the protected admin endpoints.
