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
```
### 5. Configure Database
Set up PostgreSQL and update .env (see .env.example).

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Run Server
```bash
python manage.py runserver
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

## Docker Setup (optional)
```bash
docker-compose up --build
```

## Project Structure
```bash
LetsChat/
├── apps/
│   ├── users/
│   ├── chat/
│   └── notifications/
├── config/
├── static/
├── manage.py
└── requirements.txt

```

## Author
Nyaguthii Carol [@Nyaguthii-C]