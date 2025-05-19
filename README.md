# LetsChat

A real-time chat application built with Django, Django Channels, PostgreSQL, and WebSockets. Supports user registration, authentication, private messaging, and live notifications — all containerized with Docker and tested using TDD.

---

## Features

- 🔐 User authentication with profile
- 💬 One-on-one real-time chat using Django Channels
- 🛎️ Live in-app notifications for new messages
- 📄 API documentation via Swagger (drf-yasg)
- 🧪 Test-driven development using `pytest`
- 🐘 PostgreSQL database
- 🐳 Dockerized for consistent dev environment
- 🖼️ [LetsChat FrontEnd](https://github.com/Nyaguthii-C/letschat-frontend) (login/signup/chat UI)

---

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Real-Time**: Django Channels, Redis (for WebSocket layer)
- **Database**: PostgreSQL
- **Docs**: Swagger / drf-yasg
- **Testing**: Pytest, pytest-django
- **DevOps**: Docker, Docker Compose
- **Frontend**: Vite, TypeScript, React, shadcn-ui,Tailwind CSS ( initially scaffolded using lovable.dev, with custom integration and enhancements.)

<!-- ---

## 📸 Screenshots

> _(Optional) Add GIFs or screenshots of login, chat UI, notification bell, etc._ -->

---

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/Nyaguthii-C/LetsChat.git
cd LetsChat

```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environmental Variables .env
```
GETSTREAM_API_KEY=valuehere
GETSTEAM_PASSWORD=valuehere
POSTGRES_DB=valuehere
POSTGRES_USER=valuehere
POSTGRES_PASSWORD=valuehere
DJANGO_SECRET_KEY=valuehere
DEBUG=TrueOrFalse
REDIS_URL=valuehere
```
### 5. Configure Database
Set up PostgreSQL and update .env (see .env.example).
<!-- Create a PostgreSQL database and user (if not already created).
#### Log in to PostgreSQL:
   Open your terminal and log in to the PostgreSQL command line interface:

   ```bash
   psql -U postgres
   ```

   (Replace `postgres` with your username if you use a different PostgreSQL username.)

#### Create a Database:
   To create a new database, run:

   ```sql
   CREATE DATABASE your_db_name;
   ```

#### Create a User:
   Create a user (if it doesn’t exist) with a password:

   ```sql
   CREATE USER your_db_user WITH PASSWORD 'your_db_password';
   ```

#### Grant Privileges:
   Grant all privileges on the database to the user:

   ```sql
   GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;
   ```

#### Exit PostgreSQL:

   ```sql
   \q
   ``` -->

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Collect static files
```bash
python manage.py collectstatic
```
### 7. Run Server (supporting asgi)
<!-- ```bash
python manage.py runserver
``` -->

```bash
daphne config.asgi:application
```

## Running Tests
```bash
pytest
```

## API Documentation
Access Swagger UI at:
```bash
http://localhost:8000/swagger/

```

## 🐳 Docker Setup (Optional, Recomended for Consistency)

<!-- 0. Installing Docker and Docker Compose
```bash
sudo apt update && sudo apt install docker.io docker-compose -y
sudo systemctl enable docker -->
```

1. Build and Run the Containers

```bash
sudo docker-compose up --build
```

2. Access App
```bash
API: http://localhost:8000

Swagger Docs: http://localhost:8000/swagger/
```

3. Common Docker Commands

### Stop all services
```bash
docker-compose down
```
### View logs from web app
```bash
docker-compose logs -f web
```
### Bash into the web container
```bash
docker-compose exec web bash
```


## Project Structure
```bash
LetsChat/
├── apps/
│   ├── users/
│   ├── chat/
│   └── notifications/
├── config/
├── staticfiles/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env

```

## Author
[Nyaguthii Carol](https://github.com/Nyaguthii-C)
