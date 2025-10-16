# Study to Play

**Web application to encourage and supervise teenagers' study time.**  
It allows users to track study sessions, visualize progress, and manage study habits in a simple, motivating interface.

---

## Overview

Study to Play is a **modular web application built with Flask (Python)** that follows **clean architecture principles**.  
It separates the project into clear, testable layers — routes, services, repositories, models, and utilities — with a dedicated test suite and database migrations.

This project demonstrates:
- Scalable backend structure with Flask.  
- Layered architecture for maintainability and testing.  
- RESTful design and data persistence via SQLAlchemy.  
- Frontend integration with JavaScript for interactivity.  
- Automated testing using **Pytest**.  
- Database migrations handled with **Flask-Migrate**.

---

## Features

- Track and record study sessions.  
- Visualize progress and study history.  
- User authentication and session management.  
- SQLAlchemy ORM for relational data persistence.  
- Unit tests with Pytest.  
- Database migrations via Flask-Migrate.  
- Responsive UI with HTML, CSS, and JavaScript.  
- Modular architecture with reusable components.

---

## Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | Python, Flask |
| **Frontend** | HTML, CSS, JavaScript |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Migrations** | Flask-Migrate |
| **Testing** | Pytest |
| **Architecture** | Routes / Services / Repositories / Models / Utils |
| **Environment** | Virtualenv |
| **Version Control** | Git & GitHub |

---

## Project Structure
- `migrations/` — database migrations (Flask-Migrate)
- `tests/` — unit tests (Pytest)
- `app/`
  - `models/` — SQLAlchemy models
  - `repositories/` — CRUD operations
  - `services/` — business logic
  - `routes/` — Flask Blueprints
  - `utils/` — helper functions
  - `static/` — CSS/JS assets
  - `templates/` — HTML templates
