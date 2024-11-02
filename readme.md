# API Documentation
### BACKEND & FRONTEND

## Table of Contents
- [Setup](#setup)
  - [Backend Setup](#backend-setup)
    - [Prerequisites](#backend-prerequisites)
    - [Backend Installation](#backend-installation)
    - [Backend Configuration](#backend-configuration)
    - [Running the Backend](#running-the-backend)
  - [Frontend Setup](#frontend-setup)
    - [Prerequisites](#frontend-prerequisites)
    - [Frontend Installation](#frontend-installation)
    - [Running the Frontend](#running-the-frontend)
- [Introduction](#introduction)
- [Authentication](#authentication)
- [Program Management](#program-management)
- [Statistics](#statistics)
- [User Management](#user-management)

## Setup

### Backend Setup

#### Backend Prerequisites
Before setting up the project, ensure you have the following installed:
- Python 3.8 or higher
- MySQL
- MongoDB
- Git

#### Backend Installation

1. Clone the repository
```bash
git clone https://github.com/Wali-dev/SMS-management.git
cd SMS-management
cd backend
```

2. Create and activate a virtual environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

#### Backend Configuration

1. Create a `.env` file in the root directory with the following variables:
```env
SQL_DATABASE_URL=mysql://username:password@localhost/database_name
MONGODB_DATABASE_URL=mongodb://localhost:27017/database_name
JWT_SECRET_KEY=your_secret_key
```

2. Set up the databases
- Create a MySQL database with the name specified in your `.env` file
- Ensure MongoDB is running and accessible at the URL specified in your `.env` file

#### Running the Backend

1. Initialize the database tables
```bash
pyhton init_db.py
```

2. Start the Flask application
```bash
python main.py
```

The backend will start running on `http://localhost:5000`

### Frontend Setup

#### Frontend Prerequisites
- Node.js 14.x or higher
- npm 6.x or higher

#### Frontend Installation

1. Navigate to the frontend directory from the project root
```bash
cd frontend
```

2. Install dependencies
```bash
npm install
```

#### Running the Frontend

1. Start the development server
```bash

npm run dev
```

The frontend will start running on `http://localhost:3000`

## Introduction
This API allows you to manage SMS programs, track their performance metrics, and manage user accounts. The API is built using Flask, Flask-SQLAlchemy, and Flask-MongoEngine.

## Authentication
The API uses JWT-based authentication. Include the `Authorization` header with a valid JWT token.

## Program Management

### Create Program
**Endpoint:** `POST /program/create`
**Request:** 
```json
{
  "pair_name": "My Program",
  "proxy": "proxy.example.com:8080",
  "active_status": true,
  "priority": 1,
  "number_list": (file)
}
```
**Response:**
```json
{
  "message": "Pair created successfully",
  "pair_id": "612a4b1c3b0b1c0b1c0b1c0b",
  "pair": { ... }
}
```

### Update Program
**Endpoint:** `PATCH /program/update/<pair_id>`
**Request:** 
```json
{
  "pair_name": "Updated Program",
  "active_status": false,
  "priority": 2,
  "proxy": "new.proxy.example.com:8080"
}
```
**Response:**
```json
{
  "message": "Pair updated successfully",
  "pair": { ... }
}
```

### Delete Program
**Endpoint:** `DELETE /program/delete/<pair_id>`
**Response:**
```json
{
  "message": "Pair deleted successfully",
  "pair_id": "612a4b1c3b0b1c0b1c0b1c0b"
}
```

### Start/Stop/Restart Program
**Endpoint:** `POST /program/<operation>`
**Request:**
```json
{
  "pair_name": "My Program"
}
```
**Response:**
```json
{
  "message": "Started processing pair",
  "success": true
}
```

### Get All Programs
**Endpoint:** `GET /program/pairs`
**Response:**
```json
[
  {
    "pairName": "My Program",
    "activeStatus": true,
    "priority": 1,
    "proxy": "proxy.example.com:8080",
    "sessionDetails": {},
    "createdAt": "2023-08-15T12:34:56.789Z",
    "numberListFile": { ... },
    "pair_id": "612a4b1c3b0b1c0b1c0b1c0b"
  },
  { ... }
]
```

## Statistics

### Get SMS Stats for a Program
**Endpoint:** `GET /stats/<pair_name>`
**Response:**
```json
{
  "message": "Stats retrieved successfully",
  "stats": { ... }
}
```

### Get Aggregate Stats
**Endpoint:** `GET /stats/aggregate`
**Response:**
```json
{
  "message": "Aggregate stats retrieved successfully",
  "stats": { ... }
}
```

### Create Dummy Stats
**Endpoint:** `POST /stats/dummy`
**Request:**
```json
{
  "pair_name": "My Program",
  "total_sms_sent": 1000,
  "total_sms_failed": 100
}
```
**Response:**
```json
{
  "message": "Stats created successfully",
  "stats": { ... }
}
```

## User Management

### Get User
**Endpoint:** `GET /user/<user_id>`
**Response:**
```json
{
  "username": "johndoe",
  "password": "hashed_password",
  "email": "johndoe@example.com"
}
```

### Create User
**Endpoint:** `POST /user`
**Request:**
```json
{
  "username": "johndoe",
  "password": "password123",
  "email": "johndoe@example.com"
}
```
**Response:**
```json
{
  "message": "User created",
  "userId": "612a4b1c3b0b1c0b1c0b1c0b"
}
```

### Sign In
**Endpoint:** `POST /signin`
**Request:**
```json
{
  "identifier": "johndoe",
  "password": "password123"
}
```
**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjEyYTRiMWMzYjBiMWMwYjFjMGIxYzBiIiwiZXhwIjoxNjYyOTQ4NDAwfQ.BpOJ-SqJcPZmDlr6Nx5Lbr8uQe_AH8BxIbA3HWwD_XM"
}
```