import requests
import os
import sys
import json
from getpass import getpass

class ServerClient:
    def __init__(self, base_url="http://localhost:5002"):
        self.base_url = base_url
        self.session = requests.Session()
        self.current_user = None
        self.current_password = None
    
    def register(self, username, password):
        url = f"{self.base_url}/api/register"
        payload = {"username": username, "password": password}
        
        response = self.session.post(url, json=payload)
        return response.json(), response.status_code
    
    def upload_data(self, username, password, file_path):
        url = f"{self.base_url}/api/upload"
        files = {'file': open(file_path, 'rb')}
        data = {'username': username, 'password': password}
        
        response = self.session.post(url, files=files, data=data)
        return response.json(), response.status_code
    
    def get_users(self):
        url = f"{self.base_url}/api/users"
        response = self.session.get(url)
        return response.json(), response.status_code
    
    def get_user_data(self, username, password):
        url = f"{self.base_url}/api/data/{username}"
        headers = {"Password": password}
        
        response = self.session.get(url, headers=headers)
        return response.json(), response.status_code

def display_menu():
    print("\n=== Меню ===")
    print("1. Регистрация")
    print("2. Загрузка CSV файла")
    print("3. Получить список пользователей")
    print("4. Получить данные пользователя")
    print("5. Выход")
    return input("Выберите действие (1-5): ")

def main():
    client = ServerClient()
    
    while True:
        choice = display_menu()
        
        if choice == "1":
            username = input("Введите имя пользователя: ")
            password = getpass("Введите пароль: ")
            
            result, status_code = client.register(username, password)
            print(f"Статус: {status_code}, Ответ: {result}")
            
            if status_code == 201:
                client.current_user = username
                client.current_password = password
        
        elif choice == "2":
            if not client.current_user:
                username = input("Введите имя пользователя: ")
                password = getpass("Введите пароль: ")
            else:
                username = client.current_user
                password = client.current_password
                print(f"Используем текущего пользователя: {username}")
            
            file_path = input("Введите путь к CSV файлу: ")
            
            if not os.path.exists(file_path):
                print(f"Ошибка: Файл {file_path} не найден")
                continue
            
            result, status_code = client.upload_data(username, password, file_path)
            print(f"Статус: {status_code}, Ответ: {result}")
        
        elif choice == "3":
            result, status_code = client.get_users()
            
            if status_code == 200:
                print("Список пользователей:")
                for i, user in enumerate(result["users"], 1):
                    print(f"{i}. {user}")
            else:
                print(f"Ошибка: {result}")
        
        elif choice == "4":
            if not client.current_user:
                username = input("Введите имя пользователя: ")
                password = getpass("Введите пароль: ")
            else:
                username = client.current_user
                password = client.current_password
                print(f"Используем текущего пользователя: {username}")
            
            result, status_code = client.get_user_data(username, password)
            
            if status_code == 200:
                print("Данные пользователя:")
                for item in result["data"]:
                    print(item)
                
                # Вывод в JSON при необходимости
                save_json = input("Сохранить данные в JSON файл? (y/n): ")
                if save_json.lower() == 'y':
                    file_path = input("Введите путь для сохранения JSON файла: ")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(result["data"], f, ensure_ascii=False, indent=4)
                    print(f"Данные сохранены в {file_path}")
            else:
                print(f"Ошибка: {result}")
        
        elif choice == "5":
            print("Выход из программы...")
            break
        
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main() 