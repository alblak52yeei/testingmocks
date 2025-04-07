import sys
import os
import json
import io
import pytest
from unittest.mock import patch, Mock, MagicMock
import tempfile

# Добавляем пути для импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register_user(client):
    # Создаем mock для request.json
    with patch('flask.request.json', {'username': 'test_user', 'password': 'test_pass'}):
        response = client.post('/api/register')
        data = json.loads(response.data)
        assert response.status_code == 201
        assert data['message'] == 'Пользователь успешно зарегистрирован'

def test_register_user_already_exists(client):
    # Регистрируем пользователя
    with patch('flask.request.json', {'username': 'existing_user', 'password': 'test_pass'}):
        client.post('/api/register')

    # Пытаемся зарегистрировать того же пользователя
    with patch('flask.request.json', {'username': 'existing_user', 'password': 'test_pass'}):
        response = client.post('/api/register')
        data = json.loads(response.data)
        assert response.status_code == 400
        assert 'Пользователь уже существует' in data['error']

def test_upload_csv_data(client):
    # Регистрируем пользователя
    with patch('flask.request.json', {'username': 'csv_user', 'password': 'test_pass'}):
        client.post('/api/register')

    # Создаем временный CSV-файл
    csv_content = "name,age,city\nJohn,30,New York\nAlice,25,London"
    csv_file = io.BytesIO(csv_content.encode('utf-8'))

    # Создаем mock для request.files и request.form
    with patch('flask.request.files') as mock_files, \
         patch('flask.request.form') as mock_form:
        
        # Настраиваем mock-объекты
        mock_files.__getitem__.return_value = csv_file
        mock_files.__contains__.return_value = True
        mock_form.get.side_effect = lambda x: 'csv_user' if x == 'username' else 'test_pass'
        
        response = client.post('/api/upload')
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['message'] == 'Данные успешно загружены'

def test_get_users(client):
    # Регистрируем пользователей
    with patch('flask.request.json', {'username': 'user1', 'password': 'pass1'}):
        client.post('/api/register')
    with patch('flask.request.json', {'username': 'user2', 'password': 'pass2'}):
        client.post('/api/register')

    response = client.get('/api/users')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'users' in data
    assert 'user1' in data['users']
    assert 'user2' in data['users']

def test_get_user_data(client):
    # Регистрируем пользователя
    with patch('flask.request.json', {'username': 'data_user', 'password': 'test_pass'}):
        client.post('/api/register')

    # Загружаем данные для пользователя
    csv_content = "name,age,city\nJohn,30,New York\nAlice,25,London"
    csv_file = io.BytesIO(csv_content.encode('utf-8'))

    with patch('flask.request.files') as mock_files, \
         patch('flask.request.form') as mock_form:
        
        mock_files.__getitem__.return_value = csv_file
        mock_files.__contains__.return_value = True
        mock_form.get.side_effect = lambda x: 'data_user' if x == 'username' else 'test_pass'
        
        client.post('/api/upload')

    # Получаем данные пользователя
    with patch('flask.request.headers') as mock_headers:
        mock_headers.get.return_value = 'test_pass'
        
        response = client.get('/api/data/data_user')
        data = json.loads(response.data)
        assert response.status_code == 200
        assert 'data' in data
        assert len(data['data']) == 2
        assert data['data'][0]['name'] == 'John'
        assert data['data'][1]['name'] == 'Alice' 