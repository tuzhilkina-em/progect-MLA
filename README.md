# Test Autentification System

FastAPI-based authentication system with admin panel and time-limited codes.

## Features

- Admin-protected code generation
- Data encryption (priority)
- Time-limited access codes(pre-relized) and temporary-storage
- Responsive web interface
- Basic HTTP authentication for admin routes

## Project Structure
progect-MLA/
- app/
  - main.py # Main application logic
  - static/ # Static files (images)
  - templates/ # HTML templates
  - login.html # Login page
  - welcome.html # Welcome page
 
- README.md # This file
- gitignore # Git ignore rules
- poetry.lock
- pyproject.toml
- data.json
    

## Prerequisites

- Python 3.8+
- pip or Poetry
- Git

## Installation

1. Clone the repository
2. Set up virtual environment (recommended)
3. Install dependencies
4. Running the Application:
   cd app
   uvicorn app.main:app --reload

The application will be available at:
  http://localhost:8000 (main page)
  http://localhost:8000/admin/generate (protected)
  http://localhost:8000/admin/codes (protected)

License:
  MIT License
