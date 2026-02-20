import pytest
import testinfra
import os
import sys
import urllib.parse  # <--- 1. Добавили библиотеку для кодирования паролей
from dotenv import load_dotenv

# Загружаем данные из .env файла
load_dotenv()

# Поднимаемся на уровень выше, чтобы импортировать inventory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inventory import SERVERS


@pytest.mark.smoke
@pytest.mark.parametrize("name, ip, user, password", [s[:4] for s in SERVERS], ids=[s[0] for s in SERVERS])
def test_server_connectivity(name, ip, user, password):
    """
        SMOKE TEST (REQ-000): Verifies SSH connectivity to the server.

        This test covers multiple layers of the stack implicitly:
        1. Network Layer: IP is reachable.
        2. Transport Layer: Port 22 is open and accepting TCP connections.
        3. Application (SSH): SSH Daemon is running and accepts the handshake.
        4. Auth Layer: Credentials (root + password) are correct.
        5. Execution: System can fork a process ('hostname') and return stdout.

        If this test fails, further security auditing (REQ-001+) is impossible.
        """
    # 2. КОДИРУЕМ ПАРОЛЬ (Safe Encoding)
    # Если в пароле есть слэши / или собаки @, они заменятся на %2F и %40
    safe_password = urllib.parse.quote_plus(password)

    # 3. Используем safe_password в строке подключения
    connection_string = f"paramiko://{user}:{safe_password}@{ip}"

    host = testinfra.get_host(connection_string, sudo=False)

    try:
        actual_hostname = host.check_output("hostname")
        # Вывод без лишних кавычек для красоты
        print(f"\n✅ CONNECTED: [{name}] IP: {ip} | Hostname: {actual_hostname.strip()}")
        assert actual_hostname is not None

    except Exception as e:
        pytest.fail(f"❌ FAILED to connect to {name} ({ip}): {str(e)}")