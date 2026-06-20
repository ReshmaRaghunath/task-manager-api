# Task Manager API

A secure RESTful API built with Python and Flask to manage personal tasks. This project features user registration, secure login via JWT (JSON Web Tokens), and full CRUD operations for task management using an SQLite database.

## Features
- **User Authentication:** Secure password hashing using Werkzeug and token-based protection using JWT.
- **Task Management:** Create, read, update, and delete tasks.
- **Filtering:** View tasks filtered by category or completion status.

## Tech Stack
- **Framework:** Flask (Python)
- **Database:** SQLite
- **Security:** PyJWT, Werkzeug Hashing

## How to Run Locally

1. **Clone the repository:**
   git clone https://github.com/ReshmaRaghunath/task-manager-api.git
   cd task-manager-api

2. **Set up the virtual environment:**
   python3 -m venv venv
   source venv/bin/activate

3. **Install dependencies:**
   pip install -r requirements.txt

4. **Initialize the Database:**
   python database.py

5. **Start the server:**
   python app.py

## API Endpoints

### Authentication
- POST /signup - Register a new user account. Requires a JSON body containing username and password.
- POST /login - Log in and receive a JWT token. Requires a JSON body containing username and password.

### Tasks (Requires Authorization Header)
Header format: Authorization: Bearer <your_token>
- POST /tasks - Create a new task. Requires a JSON body containing title, plus optional description and category.
- GET /tasks - Get all tasks belonging to the logged-in user (supports query filters like /tasks?status=pending or /tasks?category=Work).
- GET /tasks/<id> - Retrieve a single task by its specific ID.
- PUT /tasks/<id> - Modify task details or mark a task as completed/pending using its ID.
- DELETE /tasks/<id> - Remove a task from the database by its ID.
