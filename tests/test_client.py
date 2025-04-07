import sys
import os
import json
import pytest
from unittest.mock import patch, Mock, MagicMock
import tempfile

# Добавляем пути для импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from client.cli import ServerClient

@pytest.fixture
def client():
    return ServerClient(base_url="http://mock-server.com")

def test_register_success(client):
    # Создаем mock для response
    mock_response = Mock()
    mock_response.json.return_value = {"message": "Пользователь успешно зарегистрирован"}
    mock_response.status_code = 201
    
    # Мокаем метод post в session
    with patch.object(client.session, 'post', return_value=mock_response):
        result, status_code = client.register("test_user", "test_password")
        
        # Проверяем результат
        assert status_code == 201
        assert result["message"] == "Пользователь успешно зарегистрирован"
        
        # Проверяем, что метод post был вызван с правильными параметрами
        client.session.post.assert_called_once_with(
            "http://mock-server.com/api/register",
            json={"username": "test_user", "password": "test_password"}
        )

def test_register_user_exists(client):
    # Создаем mock для response
    mock_response = Mock()
    mock_response.json.return_value = {"error": "Пользователь уже существует"}
    mock_response.status_code = 400
    
    # Мокаем метод post в session
    with patch.object(client.session, 'post', return_value=mock_response):
        result, status_code = client.register("existing_user", "test_password")
        
        # Проверяем результат
        assert status_code == 400
        assert result["error"] == "Пользователь уже существует"

def test_upload_data(client):
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_file.write(b"name,age,city\nJohn,30,New York\nAlice,25,London")
        temp_path = temp_file.name
    
    try:
        # Создаем mock для response
        mock_response = Mock()
        mock_response.json.return_value = {"message": "Данные успешно загружены"}
        mock_response.status_code = 200
        
        # Мокаем метод post в session
        with patch.object(client.session, 'post', return_value=mock_response), \
             patch('builtins.open', new_callable=Mock) as mock_open:
            
            # Настраиваем mock для open
            mock_open.return_value = open(temp_path, 'rb')
            
            result, status_code = client.upload_data("test_user", "test_password", temp_path)
            
            # Проверяем результат
            assert status_code == 200
            assert result["message"] == "Данные успешно загружены"
            
            # Проверяем, что метод post был вызван с правильными параметрами
            client.session.post.assert_called_once()
            
            # Проверяем URL вызова
            args, kwargs = client.session.post.call_args
            assert args[0] == "http://mock-server.com/api/upload"
            
            # Проверяем, что в kwargs есть 'files' и 'data'
            assert 'files' in kwargs
            assert 'data' in kwargs
            
            # Проверяем, что в data переданы правильные username и password
            assert kwargs['data']['username'] == "test_user"
            assert kwargs['data']['password'] == "test_password"
    
    finally:
        # Удаляем временный файл
        os.unlink(temp_path)

def test_get_users(client):
    # Создаем mock для response
    mock_response = Mock()
    mock_response.json.return_value = {"users": ["user1", "user2", "user3"]}
    mock_response.status_code = 200
    
    # Мокаем метод get в session
    with patch.object(client.session, 'get', return_value=mock_response):
        result, status_code = client.get_users()
        
        # Проверяем результат
        assert status_code == 200
        assert "users" in result
        assert len(result["users"]) == 3
        assert "user1" in result["users"]
        assert "user2" in result["users"]
        assert "user3" in result["users"]
        
        # Проверяем, что метод get был вызван с правильными параметрами
        client.session.get.assert_called_once_with("http://mock-server.com/api/users")

def test_get_user_data(client):
    # Создаем mock для response
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [
            {"name": "John", "age": "30", "city": "New York"},
            {"name": "Alice", "age": "25", "city": "London"}
        ]
    }
    mock_response.status_code = 200
    
    # Мокаем метод get в session
    with patch.object(client.session, 'get', return_value=mock_response):
        result, status_code = client.get_user_data("test_user", "test_password")
        
        # Проверяем результат
        assert status_code == 200
        assert "data" in result
        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "John"
        assert result["data"][1]["name"] == "Alice"
        
        # Проверяем, что метод get был вызван с правильными параметрами
        client.session.get.assert_called_once_with(
            "http://mock-server.com/api/data/test_user",
            headers={"Password": "test_password"}
        ) 