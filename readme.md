# API Documentation
### BACKEND
## Table of Contents
- [Introduction](#introduction)
- [Authentication](#authentication)
- [Program Management](#program-management)
  - [Create Program](#create-program)
  - [Update Program](#update-program)
  - [Delete Program](#delete-program)
  - [Start/Stop/Restart Program](#startstopRestart-program)
  - [Get All Programs](#get-all-programs)
- [Statistics](#statistics)
  - [Get SMS Stats for a Program](#get-sms-stats-for-a-program)
  - [Get Aggregate Stats](#get-aggregate-stats)
  - [Create Dummy Stats](#create-dummy-stats)
- [User Management](#user-management)
  - [Get User](#get-user)
  - [Create User](#create-user)
  - [Sign In](#sign-in)

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