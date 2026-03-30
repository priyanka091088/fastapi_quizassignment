# 🎯 Role-Based Quiz API (FastAPI)

## 📌 Overview

This project is a **Role-Based Quiz API** built using **FastAPI** with **JWT Authentication** and **PostgreSQL**.

It supports two types of users:

* **Admin** → Manage quizzes and questions
* **Participant** → Attempt quizzes and view results

---

## 🚀 Features

### 🔐 Authentication

* User Registration (`/register`)
* User Login (`/login`)
* JWT-based authentication

### 👨‍💼 Admin Functionalities

* Create Quiz
* Delete Quiz
* Create Question
* Update Question
* Delete Question

### 👤 Participant Functionalities

* View all quizzes
* View quiz details
* Submit quiz answers
* View results

---

## 🛠️ Tech Stack

* **Backend**: FastAPI
* **Database**: PostgreSQL
* **ORM**: SQLAlchemy
* **Authentication**: JWT (python-jose)
* **Validation**: Pydantic

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone <your-repo-url>
cd fastapi_assignment
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure Database

Update `DATABASE_URL` in `database.py`:

```python
postgresql://username:password@localhost/quizdb
```

---

### 5️⃣ Run Application

```bash
uvicorn app.main:app --reload
```

---

### 6️⃣ API Base URL

```
http://localhost:8000
```

---

## 🔑 Authentication

After login, use the token in headers:

```
Authorization: Bearer <your_token>
```

---

## 📌 API Endpoints

### 🔹 Authentication

* POST `/register`
* POST `/login`

### 🔹 Admin

* POST `/quizzes`
* DELETE `/quizzes/{quiz_id}`
* POST `/questions`
* PUT `/questions/{question_id}`
* DELETE `/questions/{question_id}`

### 🔹 Participant

* GET `/quizzes`
* GET `/quizzes/{quiz_id}`
* POST `/submit`
* GET `/result/{quiz_id}`

---

## 🧪 Testing

APIs can be tested using:

* curl commands
* Postman

---

## 📂 Project Structure

```
app/
 ├── main.py
 ├── models.py
 ├── schemas.py
 ├── auth.py
 ├── database.py
```

---

## ✅ Assignment Requirements Covered

* ✔ Role-Based Access Control
* ✔ JWT Authentication
* ✔ Quiz & Question Management
* ✔ Answer Submission & Score Calculation
* ✔ PostgreSQL Integration
* ✔ Input Validation & Error Handling

---

## 👩‍💻 Author
Priyanka Jha
