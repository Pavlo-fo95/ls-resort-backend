# LS Resort Backend

Backend API for the Body Restoration Studio website.

This service provides authentication, API endpoints, and integration logic for the LS Resort frontend application.

## Project Purpose

Backend supports:
- Authentication (JWT)
- Google OAuth login
- Admin bootstrap logic
- Contact forms and service endpoints
- Body restoration studio infrastructure

## Tech Stack
- FastAPI
- Uvicorn
- Pydantic
- Async SQLAlchemy (aiosqlite)
- SQLite (development)
- JWT Authentication

## Quick start (Windows)

```bash
git clone https://github.com/Pavlo-fo95/ls-resort-backend.git
cd ls-resort-backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run (choose the correct entrypoint)
uvicorn app.main:app --reload
# OR if entrypoint is in root main.py:
# uvicorn main:app --reload
