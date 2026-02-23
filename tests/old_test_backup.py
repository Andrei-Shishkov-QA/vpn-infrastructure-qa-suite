#import os
#import sys
#import time
#import tarfile
#import requests
#from paramiko import SSHClient, AutoAddPolicy
#from scp import SCPClient

# Add project root to sys.path to import inventory.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from inventory import SERVERS
except ImportError:
    print("❌ Critical Error: Could not import 'inventory.py'.")
    sys.exit(1)

# --- CONFIGURATION FROM ENV ---
# We load Telegram credentials from the environment variables
TG_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")


def send_to_telegram(file_path, server_name):
    """Sends the backup archive to a Telegram chat via Bot API."""
    if not TG_TOKEN or not TG_CHAT_ID:
        print(f"  ⚠️  Telegram config missing. Skipping upload for {server_name}.")
        return

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as f:
            payload = {"chat_id": TG_CHAT_ID, "caption": f"📦 Backup: {server_name}\n📅 {time.strftime('%Y-%m-%d')}"}
            files = {"document": f}
            response = requests.post(url, data=payload, files=files, timeout=30)

        if response.status_code == 200:
            print(f"  ├── ✅ Sent to Telegram successfully.")
        else:
            print(f"  ├── ❌ Telegram Error: {response.text}")
    except Exception as e:
        print(f"  ├── ❌ Failed to send to Telegram: {str(e)}")


def run_backup():
    print(f"\n📦  INFRASTRUCTURE BACKUP PROCESS")
    print(f"📅  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Ensure local 'backups' directory exists
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_backup_root = os.path.join(project_root, "backups")
    if not os.path.exists(local_backup_root):
        os.makedirs(local_backup_root)

    for name, ip, user, password, backup_paths in SERVERS:
        if not backup_paths:
            print(f"\n⏩ {name}: No backup paths defined. Skipping.")
            continue

        print(f"\n🖥️  Processing: {name} [{ip}]")
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())

        try:
            # Connect with the same optimized settings (timeout and no key search)
            ssh.connect(ip, username=user, password=password, timeout=15, look_for_keys=False)

            # Create a unique filename for this server's backup
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            remote_archive = f"/tmp/backup_{name}_{timestamp}.tar.gz"
            local_archive = os.path.join(local_backup_root, f"backup_{name}_{timestamp}.tar.gz")

            # 1. ARCHIVING: Compress remote directories into one file
            paths_str = " ".join(backup_paths)
            print(f"  ├── 🗜️  Archiving paths: {paths_str}")
            # 'z' for gzip, 'c' for create, 'f' for file. 'p' to preserve permissions.
            ssh.exec_command(f"tar -czpf {remote_archive} {paths_str} > /dev/null 2>&1")

            # 2. DOWNLOADING: Copy file from server to local machine
            print(f"  ├── 📥 Downloading archive...")
            with SCPClient(ssh.get_transport()) as scp:
                scp.get(remote_archive, local_archive)

            # 3. CLEANUP: Delete the archive from the server to save space
            ssh.exec_command(f"rm {remote_archive}")
            print(f"  ├── 🧹 Remote cleanup complete.")

            # 4. DELIVERY: Send the file to Telegram
            send_to_telegram(local_archive, name)

        except Exception as e:
            print(f"  ├── ❌ Backup failed: {str(e)}")
        finally:
            ssh.close()

    print("\n" + "=" * 60)
    print("✅ Backup Process Complete\n")


if __name__ == "__main__":
    run_backup()