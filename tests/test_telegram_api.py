import os
import pytest
import requests

def test_telegram_connection():
    """
    Verifies that the Telegram Bot API is accessible and can send documents.
    This acts as a 'Canary' test for our Disaster Recovery alerting channel.
    """
    # 1. Fetch tokens from GitHub Actions environment variables
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")

    # Skip the test if tokens are missing (e.g., local run without .env) to avoid false negative failures
    if not token or not chat_id:
        pytest.skip("Telegram credentials not found in environment. Skipping test.")

    url = f"https://api.telegram.org/bot{token}/sendDocument"

    # 2. Create the test file and content IN MEMORY (no disk I/O)
    test_filename = "test_connection.txt"
    test_content = b"This is a QA automation test file. If you see this, backup delivery works!"

    payload = {
        "chat_id": chat_id,
        "caption": "🤖 QA Test: Telegram Connection Check",
        # Fix: Telegram API expects lowercase "true" or "1" in multipart/form-data requests
        "disable_notification": "true"
    }

    # Package the in-memory file for upload
    files = {
        "document": (test_filename, test_content)
    }

    # 3. Send the request and assert that Telegram returns 200 OK
    try:
        response = requests.post(url, data=payload, files=files, timeout=10)
        assert response.status_code == 200, f"Telegram API Error: {response.text}"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Failed to connect to Telegram API: {str(e)}")