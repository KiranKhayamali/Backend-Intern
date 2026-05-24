# Backend Internship — Python & FastAPI

This repository contains the work completed during my backend development internship at **[Codavatar](https://codavatar.com/)** (Kalopul, Kathmandu).

The internship focused on building practical backend development skills using modern technologies and frameworks including Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT authentication, and Docker.

---

## Technologies Used

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat&logo=pydantic&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat&logo=sqlalchemy&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=flat&logo=jsonwebtokens&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-6BA81E?style=flat&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=flat&logo=render&logoColor=black)
![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=flat&logo=poetry&logoColor=white)

---

## Repository Structure

```bash
root/
│
├── Learning/
│   ├── alembic
│   ├── fastapi
│   ├── GraphQL
│   ├── poetry-demo
│   ├── PostgreSQL
│   ├── Redis
│   ├── ToDo
│   ├── typeHints.txt
│   ├── Guidance.txt
│   ├── off_curriculum.txt
│   └── python_curriculum.txt
│
├── Projects/
│   ├── Blog
│   ├── CafePOS
│   └── file_structured_todo
│
└── Tasks/
    ├── assignment1.py
    ├── assignment2.py
    ├── assignment3.py
    └── fastapi_assignment.py
```

> `Guidance.txt` — tracks the overall journey of the internship
> `python_curriculum.txt` — detailed log of curriculum-based learning
> `off_curriculum.txt` — detailed log of self-directed learning outside the curriculum

---

## Project Descriptions

### 1. Learning

The `Learning` folder contains all code and scripts written while following the backend internship curriculum, along with self-directed exploration of additional technologies.

**Topics Covered**

| Topic | Description |
|-------|-------------|
| FastAPI | REST API development, routing, middleware, file handling |
| Type hints | Python type annotations and return types |
| PostgreSQL | Database setup, queries, and connection to FastAPI |
| SQLAlchemy | ORM-based database modeling, CRUD, and relationships |
| Alembic | Schema migrations, adding columns, FK relationships |
| Poetry & uv | Project and dependency management |
| GraphQL | Query language for APIs (off-curriculum) |
| Redis | In-memory caching and data store (off-curriculum) |

**Learning Outcomes**

- Understood core backend architecture and REST API design
- Practiced secure backend development with authentication and data validation
- Learned database modeling, migrations, and ORM-based querying
- Explored additional technologies (GraphQL, Redis) beyond the curriculum

---

### 2. Tasks & Assignments

The `Tasks` folder contains all assignments completed while following the curriculum.

**Assignment 1 — Python Fundamentals**

Covered core Python concepts:
- Getting user input & string formatting
- Lists, sets & tuples
- Booleans, operators & if/else statements

**Assignment 2 — Loops**

Covered:
- Loops in Python
- Dictionary assignment

**Assignment 3 — Functions**

Covered:
- Functions & imports in Python
- Object Oriented Programming & class inheritance
- The four pillars of OOP in Python

**Assignment 4 — FastAPI**

A FastAPI project covering:
- REST API service using HTTP request methods (GET, POST, PUT, DELETE)
- Pydantic models & data validation
- HTTP exceptions & status codes
- Query parameters & path parameters

---

### 3. Projects

The `Projects` folder contains the three backend applications developed during the internship.

---

#### File-Structured Todo

A FastAPI application providing a todo management service built with a clean file-structured architecture. Implements full CRUD operations, REST API design, JWT-based authentication, and Pydantic data validation.

**Features**
- Create, read, update & delete todos
- User authentication with JWT
- Pydantic request/response validation
- Organized file structure with routers and models separated

---

#### Blog Service

A FastAPI application providing a blog platform backend. Supports creating and managing posts and users with secure authentication and role-based access.

**Features**
- Post creation, retrieval, update & deletion
- User registration & JWT authentication
- Role-based access control
- Pydantic validation & HTTP exception handling

---

#### Cafe POS System

A FastAPI application providing the backend for a Cafe Point of Sale (POS) system, developed in parallel with the frontend internship team. Supports multiple user roles with different levels of access and functionality.

**Roles**

| Role | Responsibilities |
|------|-----------------|
| Reception | Order intake, billing & customer management |
| Waiter | Table management & order forwarding to kitchen |
| Chef | Kitchen order queue & status updates |
| Admin | Full access — menu, users, reports & dashboard |

**Features**
- Role-based authentication & access control
- Order management & menu management
- Admin dashboard
- REST API integration with the frontend application
- Pydantic data validation & secure JWT authentication

**Learning Outcomes**
- Learned scalable, layered backend architecture
- Understood dependency injection and service separation
- Practiced REST API design with role-based access control
- Integrated a backend API with a separate frontend application

---

## Skills Gained

| Category | Skills |
|----------|--------|
| Language | Python, type hints, OOP & class inheritance |
| API Framework | FastAPI, Uvicorn, REST API design, HTTP methods |
| Data Validation | Pydantic models, field validators, status codes |
| Database | PostgreSQL, SQLAlchemy ORM, SQL queries |
| Authentication | JWT, OAuth2, password hashing, role-based access |
| Migrations | Alembic schema migrations |
| Project Management | Poetry, uv, virtual environments |
| DevOps | Docker, docker-compose, Render deployment |
| Version Control | Git, GitHub, GitLab, SSH |
| Extra Curriculum | GraphQL, Redis |

---

## Conclusion

This internship at **Codavatar** provided comprehensive hands-on experience in backend development and modern web technologies. Through structured curriculum learning and real-world projects, I developed both technical depth and an understanding of professional backend development workflows.

The internship strengthened my knowledge of Python, FastAPI, SQLAlchemy, and REST API architecture — progressing from small learning exercises to building three complete backend applications including a full Cafe POS system integrated with a live frontend. Self-directed exploration of GraphQL and Redis further broadened my understanding of the backend ecosystem.

Overall, the experience significantly contributed to my growth as a backend developer and gave me a strong foundation in building scalable, secure, and maintainable backend systems.

---

*Internship at [Codavatar Tech. Pvt. Ltd.](https://www.codavatar.com) — Kalopul, Kathmandu*
