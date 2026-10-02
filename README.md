# FitBuddy – AI Fitness Plan Generator

A complete FastAPI + Jinja2 + SQLite/SQLAlchemy web application based on the supplied FitBuddy project documentation.

## What is included

- FastAPI backend
- Jinja2 frontend
- SQLite database using SQLAlchemy 2
- Google Gemini integration using the current `google-genai` SDK
- Pro model for 7-day workout generation and feedback-based plan updates
- Flash model for concise nutrition/recovery tips
- Demo/fallback mode when no Gemini API key is configured
- HTML pages:
  - `/` – user input
  - `/result/{user_id}` – generated plan
  - `/submit-feedback` – feedback/update
  - `/view-all-users` – admin-style user/plan view
- JSON API endpoints under `/api`
- Automated tests with pytest
- Responsive CSS and small frontend JavaScript layer
- Environment configuration through `.env`

The original documentation describes FastAPI, Jinja2, SQLite/SQLAlchemy, Gemini Pro/Flash, the three main templates, feedback updates, and an all-users view. This implementation keeps that architecture while making the Gemini integration current and testable.

## Project structure

```text
FitBuddy-AI/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── gemini_client.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   ├── updated_plan.py
│   ├── routes.py
│   ├── schemas.py
│   └── main.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── all_users.html
│   └── error.html
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   └── images/README.md
├── tests/
│   └── test_app.py
├── data/
│   └── .gitkeep
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11 or newer recommended
- VS Code
- A modern browser
- A Gemini API key for real AI generation

The application can also run in demo mode without a Gemini API key.

## VS Code setup – Windows

Open the project folder in VS Code.

### 1. Create a virtual environment

```powershell
py -3.11 -m venv .venv
```

### 2. Activate it

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Command Prompt:

```cmd
.venv\Scripts\activate
```

If PowerShell blocks activation, use the VS Code terminal with Command Prompt, or allow scripts for the current user according to your normal Python/Windows setup.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment

Copy:

```text
.env.example
```

to:

```text
.env
```

For real Gemini generation, add your key:

```env
GEMINI_API_KEY=your_api_key_here
```

The current Google GenAI SDK reads the API key through the configured client. Keep the key private and never commit `.env`.

For a no-key local demo:

```env
DEMO_MODE=true
```

For real AI:

```env
DEMO_MODE=false
```

Recommended current model defaults in this project:

```env
GEMINI_PRO_MODEL=gemini-2.5-pro
GEMINI_FLASH_MODEL=gemini-2.5-flash
```

You can change these later without changing Python code.

## Run the application

From the project root:

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## First test without an API key

Use:

```env
DEMO_MODE=true
```

Then start the server and submit the form. The application generates deterministic demo content, stores it in SQLite, and exercises the complete frontend/backend/database flow.

## Test the Gemini integration

1. Create a Gemini API key.
2. Put it in `.env`.
3. Set:

```env
DEMO_MODE=false
```

4. Restart Uvicorn.
5. Submit a new user.
6. Check that a Gemini-generated plan and nutrition tip appear.
7. Submit feedback from the result page.
8. Confirm that the updated plan is saved.

If a Gemini request fails, the application returns a controlled error rather than exposing the API key or crashing the server.

## Run automated tests

```powershell
pytest -q
```

The tests force demo mode so they do not require a Gemini API key.

## API examples

### Generate a plan

```http
POST /api/generate-workout
Content-Type: application/json
```

```json
{
  "username": "Demo User",
  "user_id": "demo-001",
  "age": 20,
  "weight": 60,
  "goal": "general wellness",
  "intensity": "medium"
}
```

### Submit feedback

```http
POST /api/submit-feedback
Content-Type: application/json
```

```json
{
  "user_id": "demo-001",
  "feedback": "Include more mobility work and one additional rest day."
}
```

### List users

```http
GET /api/users
```

## Database

The SQLite database is created automatically at:

```text
data/fitbuddy.db
```

Do not commit the database to Git.

To reset local data, stop the server and delete:

```text
data/fitbuddy.db
```

The next server start recreates the database.

## Safety note

FitBuddy is a project/demo application, not a medical or diagnostic service. Generated exercise and nutrition text is general wellness information. Users should stop an exercise that causes pain and seek appropriate professional advice for medical, injury, or dietary conditions.

## Architecture

```text
Browser
   |
   v
Jinja2 HTML / FastAPI routes
   |
   +---- SQLAlchemy ----> SQLite
   |
   +---- Gemini service
            |
            +--> Pro model: workout + feedback revision
            |
            +--> Flash model: nutrition/recovery tip
```

## Troubleshooting

### `ModuleNotFoundError`

Make sure the virtual environment is active and run:

```powershell
pip install -r requirements.txt
```

### `python-multipart` error

Install:

```powershell
pip install python-multipart
```

It is already included in `requirements.txt`.

### Gemini authentication error

Check:

```env
GEMINI_API_KEY=...
DEMO_MODE=false
```

Then restart Uvicorn.

### Port already in use

Run:

```powershell
uvicorn app.main:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001
```
