# User Authentication System

A full-stack user authentication application developed as part of the WeIntern Full Stack Development Internship — Week 2, Task 3.

## Project Overview

This project allows users to register, log in, access a protected dashboard and log out securely.

The backend is developed using Python Flask, with PostgreSQL for storing user information.

## Technologies Used

- HTML5
- CSS3
- JavaScript
- Python
- Flask
- PostgreSQL
- bcrypt
- Flask-JWT-Extended
- Postman

## Features

- User registration with username, email and password
- Password hashing using bcrypt
- Login with email and password
- JWT authentication using HttpOnly cookies
- Protected profile API
- Authentication status verification
- Logout with JWT revocation
- Form validation and error handling

## Project Structure

```text
user-authentication-system/
├── backend/
│   ├── app.py
│   ├── auth.py
│   ├── database.py
│   └── requirements.txt
├── frontend/
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── style.css
│   └── script.js
├── database/
│   └── schema.sql
├── postman/
├── screenshots/
├── .env.example
├── .gitignore
└── README.md
```

## How to Run

### 1. Database Setup

Create a PostgreSQL database named `user_auth_db`.

Run the SQL statements in `database/schema.sql` using pgAdmin.

### 2. Backend Setup

Open the backend directory:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `backend/.env` using the variables shown in `.env.example`.

Enter your PostgreSQL credentials and a randomly generated JWT secret.

### 4. Start the Server

On Windows, if psycopg uses PostgreSQL's installed client library, configure the PostgreSQL `bin` directory in your terminal:

```powershell
$env:PATH = "C:\Program Files\PostgreSQL\18\bin;$env:PATH"
$env:PSYCOPG_IMPL = "python"
python app.py
```

The PostgreSQL installation path may differ on another computer.

### 5. Open the Application

- Register: http://127.0.0.1:5000/register
- Login: http://127.0.0.1:5000/login
- Dashboard: http://127.0.0.1:5000/dashboard

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register a user |
| POST | `/api/auth/login` | Log in |
| GET | `/api/auth/profile` | Retrieve authenticated user |
| GET | `/api/auth/check` | Check authentication |
| POST | `/api/auth/logout` | Log out |

## Security Features

- Passwords are hashed using bcrypt.
- PostgreSQL queries use parameterized SQL.
- JWTs are stored in HttpOnly cookies.
- CSRF protection is enabled for cookie-based authentication.
- Logged-out JWT identifiers are stored in PostgreSQL and checked during authentication.
- Database credentials and JWT signing secrets are excluded from Git.

## Limitations

This application is configured for local development. Public deployment would require HTTPS, secure cookies, rate limiting and production server configuration.

## Developer

**Garvit Maheshwari**

Full Stack Development Internship  
WeIntern Pvt Ltd — Week 2, Task 3