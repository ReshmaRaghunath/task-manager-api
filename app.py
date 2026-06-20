from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from auth import generate_token, token_required

app = Flask(__name__)

# ----------------- USER ROUTES -----------------

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400
        
    # Securely hash the password before saving it to the database
    hashed_password = generate_password_hash(password, method='scrypt')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
    except:
        return jsonify({"message": "Username already exists"}), 400
    finally:
        conn.close()
        
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    
    # Verify the user exists and the hashed password matches
    if user and check_password_hash(user['password'], password):
        token = generate_token(user['id'])
        return jsonify({"token": token}), 200
        
    return jsonify({"message": "Invalid credentials"}), 401


# ----------------- TASK CRUD ROUTES -----------------

@app.route('/tasks', methods=['POST'])
@token_required
def create_task(current_user_id):
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    category = data.get('category', 'General')
    
    if not title:
        return jsonify({"message": "Title is required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, title, description, category) VALUES (?, ?, ?, ?)",
        (current_user_id, title, description, category)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Task created successfully"}), 201

@app.route('/tasks', methods=['GET'])
@token_required
def get_tasks(current_user_id):
    # Optional filters from the URL query parameters
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    
    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [current_user_id]
    
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)
        
    conn = get_db_connection()
    tasks = conn.execute(query, params).fetchall()
    conn.close()
    
    task_list = []
    for t in tasks:
        task_list.append({
            "id": t["id"],
            "title": t["title"],
            "description": t["description"],
            "category": t["category"],
            "status": t["status"]
        })
        
    return jsonify(task_list), 200

@app.route('/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(current_user_id, task_id):
    conn = get_db_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, current_user_id)).fetchone()
    conn.close()
    
    if not task:
        return jsonify({"message": "Task not found"}), 404
        
    return jsonify({
        "id": task["id"],
        "title": task["title"],
        "description": task["description"],
        "category": task["category"],
        "status": task["status"]
    }), 200

@app.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(current_user_id, task_id):
    data = request.get_json()
    
    conn = get_db_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, current_user_id)).fetchone()
    
    if not task:
        conn.close()
        return jsonify({"message": "Task not found"}), 404
        
    title = data.get('title', task['title'])
    description = data.get('description', task['description'])
    category = data.get('category', task['category'])
    status = data.get('status', task['status'])
    
    conn.execute(
        "UPDATE tasks SET title = ?, description = ?, category = ?, status = ? WHERE id = ? AND user_id = ?",
        (title, description, category, status, task_id, current_user_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Task updated successfully"}), 200

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user_id, task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    task = cursor.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, current_user_id)).fetchone()
    if not task:
        conn.close()
        return jsonify({"message": "Task not found"}), 404
        
    cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, current_user_id))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Task deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)