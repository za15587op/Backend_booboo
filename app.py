import base64
import io
import os
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from connect_db import get_connection
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

# Test Database Connection
@app.route('/api/test_db', methods=['GET'])
def test_db_connection():
    conn = get_connection()
    if conn:
        return jsonify({"message": "Database connection successful!"}), 200
    else:
        return jsonify({"error": "Failed to connect to the database"}), 500

# Add User
@app.route('/api/user', methods=['POST'])
def add_user():
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
            cur.close()
            conn.close()
            return jsonify({"user_id": user.get('user_id')}), 201
        except Exception as e:
            return jsonify({"error": f"Failed to add user: {e}"}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500

# Get All Users
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

# Get Data with Users
@app.route('/api/data', methods=['GET'])
def get_data_with_users():
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT file_name, name 
                FROM datafile da 
                JOIN users u ON u.user_id = da.user_id;
            """)
            data = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify(data), 200
        except Exception as e:
            return jsonify({"error": f"Failed to retrieve data: {e}"}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500

# File Upload
@app.route('/api/upload', methods=['POST'])
def upload_file():
    conn = get_connection()
    if conn:
        try:
            file = request.files['file']
            user_id = request.form['user_id']
            file_data = file.read()
            
            # Insert file into the database
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                INSERT INTO datafile (file_name, file_type, file, user_id)
                VALUES (%s, %s, %s, %s)
            """, (file.filename, file.content_type, file_data, user_id))
            conn.commit()
            cur.close()
            conn.close()

            # Save file locally
            upload_folder = './uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file.save(os.path.join(upload_folder, file.filename))

            return jsonify({"message": "File uploaded successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to upload file: {e}"}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
