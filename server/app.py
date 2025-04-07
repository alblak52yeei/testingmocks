from flask import Flask, request, jsonify
import os
import csv
import json

app = Flask(__name__)

# В реальном приложении данные должны храниться в БД
users = {}  # {username: {"password": password, "data": [dict из CSV]}}

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Требуется указать имя пользователя и пароль"}), 400
    
    if username in users:
        return jsonify({"error": "Пользователь уже существует"}), 400
    
    users[username] = {"password": password, "data": []}
    return jsonify({"message": "Пользователь успешно зарегистрирован"}), 201

@app.route('/api/upload', methods=['POST'])
def upload_data():
    if 'file' not in request.files:
        return jsonify({"error": "Файл не найден"}), 400
    
    file = request.files['file']
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not file or not username or not password:
        return jsonify({"error": "Не указаны все необходимые данные"}), 400
    
    if username not in users or users[username]["password"] != password:
        return jsonify({"error": "Неверные учетные данные"}), 401
    
    try:
        # Преобразуем CSV в список словарей
        csv_content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(csv_content.splitlines())
        data = list(csv_reader)
        
        # Сохраняем данные для пользователя
        users[username]["data"] = data
        
        return jsonify({"message": "Данные успешно загружены"}), 200
    except Exception as e:
        return jsonify({"error": f"Ошибка при обработке файла: {str(e)}"}), 400

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({"users": list(users.keys())}), 200

@app.route('/api/data/<username>', methods=['GET'])
def get_user_data(username):
    password = request.headers.get('Password')
    
    if not username or not password:
        return jsonify({"error": "Не указаны все необходимые данные"}), 400
    
    if username not in users or users[username]["password"] != password:
        return jsonify({"error": "Неверные учетные данные"}), 401
    
    return jsonify({"data": users[username]["data"]}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002) 