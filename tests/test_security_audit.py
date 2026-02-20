import pytest
import testinfra
import os
import urllib.parse  # <--- 1. Добавили библиотеку для кодирования паролей
from dotenv import load_dotenv

# Загружаем данные из .env файла
load_dotenv()

# Собираем список серверов
servers = [
    ("NL-AMS", os.getenv("HOST_NL"), os.getenv("USER_NL"), os.getenv("PASS_NL")),
    ("AT-VIE", os.getenv("HOST_AT"), os.getenv("USER_AT"), os.getenv("PASS_AT")),
    ("RU-MOW", os.getenv("HOST_RU"), os.getenv("USER_RU"), os.getenv("PASS_RU")),
    ("DE-DUS", os.getenv("HOST_DE"), os.getenv("USER_DE"), os.getenv("PASS_DE")),
]

# Фильтруем пустые
servers = [s for s in servers if s[1]]


@pytest.mark.smoke
@pytest.mark.parametrize("name, ip, user, password", [s[:4] for s in servers])
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