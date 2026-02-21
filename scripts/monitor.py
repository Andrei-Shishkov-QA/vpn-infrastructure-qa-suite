import sys
import os
import time
import socket
import platform
import warnings
import logging
import paramiko

# --- 1. SILENCE THE NOISE ---
warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("paramiko").setLevel(logging.CRITICAL)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from inventory import SERVERS
except ImportError:
    print("❌ Critical Error: Could not import 'inventory.py'.")
    sys.exit(1)

THRESHOLDS = {
    "disk_min_percent": 15,
    "mem_max_percent": 90,
}


def print_check(label, value, status="ok"):
    icon = "✅ " if status == "ok" else "⚠️ " if status == "warn" else "❌ "
    print(f"  ├── {icon} {label:<15}: {value}")


def check_ping(ip):
    system_os = platform.system().lower()
    flag = "-n 1 -w 1000" if system_os == "windows" else "-c 1 -W 1"
    null_dev = "NUL" if system_os == "windows" else "/dev/null"
    return os.system(f"ping {flag} {ip} > {null_dev} 2>&1") == 0


def check_port(ip, port):
    """Checks if a specific port (like 443) is open and accepting connections."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)
    result = sock.connect_ex((ip, port))
    sock.close()
    return result == 0


def check_remote_details(ip, user, password, backup_paths):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # We use a 15s timeout to help with unstable home connections
        client.connect(ip, username=user, password=password, timeout=15)
    except Exception as e:
        return {"error": str(e)}

    data = {}
    try:
        _, stdout, _ = client.exec_command("df -h / | tail -1 | awk '{print $5}'")
        used_str = stdout.read().decode().strip().replace('%', '')
        data['disk_used'] = int(used_str) if used_str.isdigit() else 0

        _, stdout, _ = client.exec_command("free | grep Mem | awk '{print $3/$2 * 100.0}'")
        res = stdout.read().decode().strip()
        data['mem_used'] = float(res) if res else 0.0

        _, stdout, _ = client.exec_command("docker ps --format '{{.Names}}'")
        running_containers = stdout.read().decode().splitlines()

        services_report = []
        paths_str = "".join(backup_paths).lower() if backup_paths else ""

        if "x-ui" in paths_str:
            _, stdout, _ = client.exec_command("systemctl is-active x-ui")
            services_report.append(("Service: X-UI", stdout.read().decode().strip() == "active"))

        if "outline" in paths_str:
            services_report.append(("Docker: Outline", "shadowbox" in running_containers))

        if "remnawave" in paths_str:
            services_report.append(("Docker: Remna", any("remnawave" in n for n in running_containers)))

        data['services'] = services_report
    except:
        data['error'] = "Data parsing error"
    finally:
        client.close()
    return data


def run_monitor():
    print(f"\n🔎  INFRASTRUCTURE HEALTH MONITOR")
    print(f"📅  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    for node in SERVERS:
        name, ip, user, password, backup_paths = node
        print(f"\n🖥️  {name} [{ip}]")

        # 1. Network: Ping
        if check_ping(ip):
            print_check("PING", "Reachable", "ok")
        else:
            print_check("PING", "Unreachable", "fail")
            continue

        # 2. Network: Port 443 (Restored!)
        if check_port(ip, 443):
            print_check("PORT 443", "Open (HTTPS/VPN)", "ok")
        else:
            print_check("PORT 443", "Closed/Filtered", "fail")

        # 3. Deep System Metrics
        details = check_remote_details(ip, user, password, backup_paths)
        if "error" in details:
            print_check("SSH", f"Connection Failed: {details['error']}", "fail")
            continue

        d_status = "fail" if details['disk_used'] > (100 - THRESHOLDS["disk_min_percent"]) else "ok"
        print_check("DISK", f"{details['disk_used']}% Used", d_status)

        m_status = "warn" if details['mem_used'] > THRESHOLDS["mem_max_percent"] else "ok"
        print_check("RAM", f"{int(details['mem_used'])}% Used", m_status)

        for svc_name, is_up in details.get('services', []):
            print_check(svc_name.upper(), "Active" if is_up else "DOWN", "ok" if is_up else "fail")

    print("\n" + "=" * 60)
    print("✅ Scan Complete\n")


if __name__ == "__main__":
    run_monitor()