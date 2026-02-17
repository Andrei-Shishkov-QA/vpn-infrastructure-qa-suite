import os
import sys
import pytest
import requests

# Добавляем корневую папку в пути, чтобы видеть scripts.backup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.backup import send_to_telegram, TG_TOKEN, TG_CHAT_ID
from inventory import SERVERS


def test_backup_directory_exists():
    """1. Проверяем, что папка backups/ создана и доступна для записи"""
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
    assert os.path.exists(backup_dir), "❌ Папка backups/ не существует!"
    assert os.access(backup_dir, os.W_OK), "❌ Папка backups/ недоступна для записи!"


def test_telegram_config():
    """2. Проверяем, что токены загрузились"""
    assert TG_TOKEN is not None, "❌ Токен бота не найден в .env"
    assert TG_CHAT_ID is not None, "❌ Chat ID не найден в .env"


def test_inventory_has_backup_paths():
    """3. Проверяем, что хотя бы у одного сервера прописаны пути для бэкапа"""
    servers_with_paths = 0
    for server in SERVERS:
        # 5-й элемент кортежа - это список путей
        if len(server) > 4 and len(server[4]) > 0:
            servers_with_paths += 1

    assert servers_with_paths > 0, "❌ Ни у одного сервера не прописаны пути бэкапа в .env!"


def test_telegram_delivery_real():
    """
    4. ИНТЕГРАЦИОННЫЙ ТЕСТ:
    Создаем маленький файл и реально пытаемся отправить его в Телеграм.
    Если придет 200 OK — значит, система доставки работает.
    """
    # Создаем временный тестовый файл
    test_filename = "test_connection.txt"
    with open(test_filename, "w") as f:
        f.write("This is a QA automation test file. If you see this, backup delivery works!")

    try:
        # Эмулируем отправку (используем requests напрямую, чтобы проверить статус-код)
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument"
        with open(test_filename, "rb") as f:
            files = {"document": f}
            data = {"chat_id": TG_CHAT_ID, "caption": "🤖 QA Test: Telegram Connection Check"}
            response = requests.post(url, files=files, data=data)

        # ПРОВЕРКИ
        assert response.status_code == 200, f"❌ Telegram API вернул ошибку: {response.text}"
        json_resp = response.json()
        assert json_resp["ok"] is True, "❌ Telegram ответил ok: false"

    finally:
        # Убираем за собой (удаляем тестовый файл)
        if os.path.exists(test_filename):
            os.remove(test_filename)