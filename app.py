import base64
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from connect_db import get_connection
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

@app.route('/api/test_db', methods=['GET'])
def test_db_connection():
    conn = get_connection()
    if conn:
        return jsonify({"message": "Database connection successful!"}), 200
    else:
        return jsonify({"error": "Failed to connect to the database"}), 500
    
    
@app.route('/api/user', methods=['POST'])
def user():
  if request.method == 'POST':
    body = request.get_json()
    name = body.get('name')
    username = body.get('username')
    user_role = body.get('user_role')
    
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                INSERT INTO users (name, username, user_role)
                VALUES (%s, %s, %s) RETURNING user_id
            """, (name, username, user_role))
            conn.commit()
            user = cur.fetchone()
            user_id = user.get('user_id')
            cur.close()
            conn.close()
            return jsonify({"user_id": user_id}), 201
        except Exception as e:
                return { "error": f"Failed to add User: {e}" }, 500
    else:
            return { "error": "Database connection failed" }, 500
        

@app.route('/api/showUsers', methods=['GET'])
def get_users():
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM users")  
            users = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(users), 200
        except Exception as e:
            return jsonify({"error": f"Failed to retrieve users: {e}"}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/getByUser', methods=['GET'])
def get_user_by_id():
    conn = get_connection()
    if conn:
        try:
            user_id = request.args.get('user_id')
            print(f"Fetching data for user_id: {user_id}")
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                select *
                    from users u 
                WHERE u.user_id = %s
            """, (user_id,))
            
            user = cur.fetchone()
            cur.close() 
            conn.close()
            return jsonify(user), 200
        except Exception as e:
            return jsonify({"error": f"Failed to fetch user: {e}"}), 500     
    else:
        return jsonify({"error": "Database connection failed"}), 500
    
@app.route('/api/upload', methods=['POST'])
def upload_file():
    conn = get_connection()
    if conn:
        try:    
            file = request.files['file']
            user_id = request.form['user_id']
            print(user_id)
            file_data = file.read()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                INSERT INTO datafile (file_name, file_type, file, user_id)
                VALUES (%s, %s, %s, %s)
             """, (file.filename, file.content_type, file_data, user_id))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"message": "File uploaded successfully"}), 200
        except Exception as e:
                return { "error": f"Failed to add User: {e}" }, 500
    else:
        return jsonify({"error": "Database connection failed"}), 500
    


@app.route('/api/getDataFile', methods=['GET'])
def get_data_with_users():
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT df.file_id , df.file_name, u.name 
                FROM datafile df 
                JOIN users u ON u.user_id = df.user_id;
            """)
            users = cur.fetchall()
            for user in users:
                for key, value in user.items():
                    if isinstance(value, memoryview): 
                        user[key] = base64.b64encode(value.tobytes()).decode('utf-8')  
                    elif isinstance(value, bytes): 
                        user[key] = base64.b64encode(value).decode('utf-8')
            cur.close()
            conn.close()
            return jsonify(users), 200
        except Exception as e:
            return jsonify({"error": f"Failed to retrieve data: {e}"}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500
    
@app.route('/api/file/<string:file_id>', methods=['DELETE'])
def delete_file(file_id):
    conn = get_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM datafile WHERE file_id = %s", (file_id,))
        conn.commit()

        if cur.rowcount == 0:
            return jsonify({"error": "File not found"}), 404

        cur.close()
        conn.close()
        return jsonify({"message": "File deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete file: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
