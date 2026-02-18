import sys
import os
import time
import socket
import platform
import warnings

# --- 1. УБИРАЕМ ШУМ ИЗ КОНСОЛИ ---
warnings.filterwarnings("ignore", category=DeprecationWarning)
import logging

logging.getLogger("paramiko").setLevel(logging.CRITICAL)

import paramiko

# --- MAGIC: Добавляем путь к inventory.py ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from inventory import SERVERS
except ImportError:
    print("❌ Critical Error: Could not import 'inventory.py'.")
    sys.exit(1)

# --- CONFIG ---
THRESHOLDS = {
    "disk_min_percent": 15, # Разрешимый объём оставшегося диска (если меньше, то сигнал)
    "mem_max_percent": 90, # Разрешимый объём использованной памяти (если больше, то сигнал)
}


def print_check(label, value, status="ok"):
    """Красивый вывод в консоль"""
    if status == "ok":
        icon = "✅ "
    elif status == "warn":
        icon = "⚠️"
    else:
        icon = "❌ "
    # Форматирование: иконка, название (15 симв), значение
    print(f"  ├── {icon} {label:<15}: {value}")


def check_ping(ip):
    system_os = platform.system().lower()
    if system_os == "windows":
        cmd = f"ping -n 1 -w 1000 {ip} > NUL 2>&1"
    else:
        cmd = f"ping -c 1 -W 1 {ip} > /dev/null 2>&1"
    return os.system(cmd) == 0


def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.5)
    result = sock.connect_ex((ip, port))
    sock.close()
    return result == 0


def check_remote_details(ip, user, password, backup_paths):
    """Глубокая проверка через SSH"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(ip, username=user, password=password, timeout=5)
    except Exception as e:
        return {"error": str(e)}

    data = {}

    # 1. DISK USAGE
    try:
        stdin, stdout, stderr = client.exec_command("df -h / | tail -1 | awk '{print $5}'")
        used_str = stdout.read().decode().strip().replace('%', '')
        data['disk_used'] = int(used_str)
    except:
        data['disk_used'] = -1

    # 2. RAM USAGE
    try:
        stdin, stdout, stderr = client.exec_command("free | grep Mem | awk '{print $3/$2 * 100.0}'")
        data['mem_used'] = float(stdout.read().decode().strip())
    except:
        data['mem_used'] = -1

    # 3. SERVICE DISCOVERY (Smart Check)
    # Сначала получаем список ВСЕХ запущенных докер-контейнеров одной командой
    running_containers = []
    try:
        stdin, stdout, stderr = client.exec_command("docker ps --format '{{.Names}}'")
        running_containers = stdout.read().decode().splitlines()
    except:
        pass  # Если докера нет, список будет пустым

    services_report = []  # Список кортежей (Название, Статус)

    # Анализируем backup_paths чтобы понять, что искать
    paths_str = "".join(backup_paths) if backup_paths else ""

    # --- LOGIC: X-UI (Systemd) ---
    if "x-ui" in paths_str:
        stdin, stdout, stderr = client.exec_command("systemctl is-active x-ui")
        st = stdout.read().decode().strip()
        services_report.append(("Service: x-ui", st == "active"))

    # --- LOGIC: OUTLINE (Docker 'shadowbox') ---
    if "outline" in paths_str:
        # Outline всегда называет свой контейнер 'shadowbox'
        is_running = "shadowbox" in running_containers
        services_report.append(("Docker: Outline", is_running))

    # --- LOGIC: REMNAWAVE (Docker 'remnawave' or similar) ---
    if "remnawave" in paths_str:
        # Ищем любой контейнер, в названии которого есть 'remnawave'
        is_running = any("remnawave" in name for name in running_containers)
        services_report.append(("Docker: Remna", is_running))

    data['services'] = services_report

    client.close()
    return data


def run_monitor():
    print(f"\n🔎  INFRASTRUCTURE DEEP SCAN")
    print(f"📅  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    for node in SERVERS:
        name, ip, user, password, backup_paths = node
        print(f"\n🖥️  {name} [{ip}]")

        # 1. BASIC NETWORK
        if check_ping(ip):
            print_check("PING", "Latency < 1s", "ok")
        else:
            print_check("PING", "Unreachable", "fail")
            continue

        if check_port(ip, 443):
            print_check("PORT 443", "Open (HTTPS)", "ok")
        else:
            print_check("PORT 443", "Closed/Blocked", "fail")

        # 2. DEEP SSH
        details = check_remote_details(ip, user, password, backup_paths)

        if "error" in details:
            print_check("SSH", f"Fail: {details['error']}", "fail")
            continue

        # Disk
        d = details['disk_used']
        if d > (100 - THRESHOLDS["disk_min_percent"]):
            print_check("DISK", f"{d}% Used (CRITICAL)", "fail")
        else:
            print_check("DISK", f"{d}% Used", "ok")

        # RAM
        m = details['mem_used']
        if m > THRESHOLDS["mem_max_percent"]:
            print_check("RAM", f"{int(m)}% Used (High)", "warn")
        else:
            print_check("RAM", f"{int(m)}% Used", "ok")

        # Services (Dynamic List)
        if not details['services']:
            print_check("APPS", "No apps monitored", "warn")
        else:
            for svc_name, is_up in details['services']:
                if is_up:
                    print_check(svc_name.upper(), "Active / Running", "ok")
                else:
                    print_check(svc_name.upper(), "STOPPED / DEAD", "fail")

    print("\n" + "=" * 60)
    print("✅ Scan Complete\n")


if __name__ == "__main__":
    run_monitor()