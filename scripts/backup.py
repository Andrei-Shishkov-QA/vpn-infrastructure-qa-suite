import os
import sys
import datetime
import requests
import paramiko
import time
from scp import SCPClient
from dotenv import load_dotenv

# Добавляем корневую папку проекта в пути, чтобы увидеть inventory.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inventory import SERVERS

load_dotenv()

# Настройки Телеграм
TG_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

RETENTION_DAYS = 7

# Папка для локального сохранения бэкапов
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "../backups")
os.makedirs(BACKUP_DIR, exist_ok=True)


def send_to_telegram(file_path, caption):
    """Отправляет файл в Телеграм боту"""
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument"

    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": TG_CHAT_ID, "disable_notification": "true", "caption": caption}

            response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            print(f"   ✅ Sent to Telegram!")
        else:
            print(f"   ❌ Telegram Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Failed to send: {e}")


def create_remote_backup(server_name, ip, user, password, paths):
    """
    1. Заходит по SSH.
    2. Архивирует указанные пути в .tar.gz (исключая мусор prometheus).
    3. Скачивает архив.
    """
    print(f"\n📦 Processing {server_name} ({ip})...")

    if not paths:
        print("   ⚠️ No backup paths defined in .env! Skipping.")
        return

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ip, username=user, password=password, timeout=10)

        # 1. Формируем имя файла: backup_RU-MOW_2026-02-17.tar.gz
        date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"backup_{server_name}_{date_str}.tar.gz"
        remote_path = f"/tmp/{filename}"
        local_path = os.path.join(BACKUP_DIR, filename)

        # 2. Собираем команду TAR
        # --exclude='*/prometheus': Игнорируем папку с метриками Outline (экономим место)
        paths_str = " ".join(paths)
        tar_cmd = f"tar --exclude='*/prometheus' --exclude='*/pg_wal' -czf {remote_path} {paths_str}"

        print(f"   ⚙️ Archiving remote files...")
        stdin, stdout, stderr = ssh.exec_command(tar_cmd)
        exit_status = stdout.channel.recv_exit_status()

        if exit_status != 0:
            print(f"   ❌ Tar failed: {stderr.read().decode()}")
            return

        # 3. Скачиваем файл (SCP)
        print(f"   ⬇️ Downloading to {local_path}...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.get(remote_path, local_path)

        # 4. Удаляем мусор на сервере
        ssh.exec_command(f"rm {remote_path}")

        # 5. Отправляем в Телеграм
        caption = f"📦 Backup: {server_name}\n📅 Date: {date_str}\n💾 Files: {', '.join(paths)}"
        send_to_telegram(local_path, caption)

        # (Опционально) Удаляем локальный файл после отправки, чтобы не засорять комп
        # os.remove(local_path)

    except Exception as e:
        print(f"   🔥 Error: {e}")
    finally:
        ssh.close()


def cleanup_old_backups(days):
    """Удаляет локальные файлы старше N дней"""
    if days <= 0:
        return

    print(f"\n🧹 Cleaning up local backups older than {days} days...")
    now = time.time()
    cutoff = days * 86400  # 86400 секунд в сутках

    count = 0
    if os.path.exists(BACKUP_DIR):
        for filename in os.listdir(BACKUP_DIR):
            file_path = os.path.join(BACKUP_DIR, filename)
            # Проверяем, что это файл
            if os.path.isfile(file_path):
                file_age = now - os.path.getmtime(file_path)
                if file_age > cutoff:
                    try:
                        os.remove(file_path)
                        print(f"   🗑️ Deleted old file: {filename}")
                        count += 1
                    except Exception as e:
                        print(f"   ⚠️ Could not delete {filename}: {e}")

    if count == 0:
        print("   ✨ Nothing to clean (all files are fresh).")

if __name__ == "__main__":
    print("🚀 Starting Backup Process...")

    # Проверка настроек
    if not TG_TOKEN or not TG_CHAT_ID:
        print("❌ Error: TG_BOT_TOKEN or TG_CHAT_ID is missing in .env")
        exit(1)

    # Запуск по всем серверам из inventory.py
    for server in SERVERS:
        # Разбираем кортеж (Name, IP, User, Pass, Paths)
        # Если вдруг путей нет в конфиге, ставим пустой список
        name, ip, user, password = server[0], server[1], server[2], server[3]
        paths = server[4] if len(server) > 4 else []

        create_remote_backup(name, ip, user, password, paths)
    cleanup_old_backups(RETENTION_DAYS)
    print("\n✅ All Done! Check your Telegram.")