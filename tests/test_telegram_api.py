import os
import pytest
import requests


def test_telegram_connection():
    """
    Verifies that the Telegram Bot API is accessible and can send documents.
    This acts as a 'Canary' test for our Disaster Recovery alerting channel.
    """
    # 1. Получаем токены из переменных окружения GitHub Actions
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")

    # Если токенов нет (например, запуск локально без .env), пропускаем тест, чтобы он не светился красным
    if not token or not chat_id:
        pytest.skip("Telegram credentials not found in environment. Skipping test.")

    url = f"https://api.telegram.org/bot{token}/sendDocument"

    # 2. Создаем тот самый файлик и фразу ПРЯМО В ПАМЯТИ (без сохранения на диск)
    test_filename = "test_connection.txt"
    test_content = b"This is a QA automation test file. If you see this, backup delivery works!"

    payload = {
        "chat_id": chat_id,
        "caption": "🤖 QA Test: Telegram Connection Check",
        "disable_notification": True  # Делаем отправку тихой, чтобы не пиликало при каждом пуше кода
    }

    # Упаковываем наш виртуальный файл для отправки
    files = {
        "document": (test_filename, test_content)
    }

    # 3. Отправляем запрос и проверяем, что Телеграм ответил 200 OK
    try:
        response = requests.post(url, data=payload, files=files, timeout=10)
        assert response.status_code == 200, f"Telegram API Error: {response.text}"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Failed to connect to Telegram API: {str(e)}")