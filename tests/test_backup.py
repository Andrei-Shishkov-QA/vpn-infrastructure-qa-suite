import pytest
import allure
import os
import requests
import sys

# Add project root to path to see backup script imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.backup import TG_TOKEN, TG_CHAT_ID
from inventory import SERVERS


@allure.suite("Disaster Recovery: Backup System Validation")
class TestBackupConfiguration:

    @allure.id("REQ-006.1")
    @allure.title("Environment: Local Backup Directory Access")
    def test_backup_directory_exists(self):
        """Verifies that the local 'backups/' folder is created and writable."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        backup_dir = os.path.join(project_root, "backups")

        assert os.path.exists(backup_dir), "❌ The 'backups/' directory is missing!"
        assert os.access(backup_dir, os.W_OK), "❌ The 'backups/' directory is not writable!"

    @allure.id("REQ-006.2")
    @allure.title("Environment: Telegram API Credentials")
    def test_telegram_config(self):
        """Ensures that Telegram Bot tokens are correctly loaded from .env."""
        assert TG_TOKEN is not None, "❌ TG_BOT_TOKEN is missing in .env!"
        assert TG_CHAT_ID is not None, "❌ TG_CHAT_ID is missing in .env!"

    @allure.id("REQ-006.3")
    @allure.title("Integration: Telegram Delivery Check")
    def test_telegram_delivery_real(self):
        """
        Creates a dummy file and attempts to send it to Telegram.
        This confirms that the notification system is fully functional.
        """
        test_file = "qa_test_delivery.txt"
        with open(test_file, "w") as f:
            f.write("QA Test: Telegram delivery verification.")

        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument"
            with open(test_file, "rb") as f:
                payload = {"chat_id": TG_CHAT_ID, "caption": "🤖 QA System: Connection Test"}
                files = {"document": f}
                response = requests.post(url, data=payload, files=files, timeout=10)

            assert response.status_code == 200, f"❌ Telegram API returned error {response.status_code}: {response.text}"
            assert response.json().get("ok") is True, "❌ Telegram response 'ok' is False"

        finally:
            # Clean up: remove the test file
            if os.path.exists(test_file):
                os.remove(test_file)