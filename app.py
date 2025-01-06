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
    token = body.get('token')
    user_role = body.get('user_role')
    
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                INSERT INTO users (name, username, token, user_role)
                VALUES (%s, %s, %s, %s) RETURNING user_id
            """, (name, username, token, user_role))
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
    
    
# def convert_vector(file):
#     file_content = base64.b64decode(file['content'])
#     file_type = file['content_type']
    
#     try:
#         if 'image' in file_type: 
#             nparr = np.frombuffer(file_content, np.uint8)
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#             img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#             vector = img_gray.flatten()
            
#         elif 'pdf' in file_type: 
#             pdf_file = io.BytesIO(file_content)
#             doc = fitz.open(stream=pdf_file, filetype="pdf")
#             text = ""
#             for page in doc:
#                 text += page.get_text()
#             vector = np.array([ord(c) for c in text])

#         return vector
        
#     except Exception as e:
#         print(f"Error converting file: {e}")
#         return np.frombuffer(file_content, dtype=np.uint8)


# @app.route('/api/upload', methods=['POST'])
# def upload_file():
#     body = request.get_json()
#     file = body.get('files')
#     print(file)
#     conn = get_connection()
#     if conn:
#         try:
            
#             vector = convert_vector(file)
            
#             vector_binary = io.BytesIO()
#             np.save(vector_binary, vector)
#             vector_binary_data = vector_binary.getvalue()
            
#             cur = conn.cursor(cursor_factory=RealDictCursor)
#             cur.execute("""
#                 INSERT INTO datafile (file_name, file_type, file_vector)
#                 VALUES (%s, %s, %s, %s)
#             """, (file.filename, file.content_type, vector_binary_data))
#             cur.close()
            
#             # result = cur.fetchone()
#             conn.commit()
            
#             return jsonify({file}), 200
            
#         except Exception as e:
#             conn.rollback()
#             return jsonify({'error': f'เกิดข้อผิดพลาดในการประมวลผล: {str(e)}'}), 500
#         finally:
#             conn.close()
#     else:
#         return jsonify({"error": "Database connection failed"}), 500

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

            upload_folder = './uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            file.save(f"./uploads/{file.filename}")
            return jsonify({"message": "File uploaded successfully"}), 200
        except Exception as e:
                return { "error": f"Failed to add User: {e}" }, 500
    else:
        return jsonify({"error": "Database connection failed"}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
