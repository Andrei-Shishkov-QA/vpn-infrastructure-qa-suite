import pytest
import testinfra
import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

servers = [
    ("NL-AMS", os.getenv("HOST_NL"), os.getenv("USER_NL"), os.getenv("PASS_NL")),
    ("AT-VIE", os.getenv("HOST_AT"), os.getenv("USER_AT"), os.getenv("PASS_AT")),
    ("RU-MOW", os.getenv("HOST_RU"), os.getenv("USER_RU"), os.getenv("PASS_RU")),
    ("DE-DUS", os.getenv("HOST_DE"), os.getenv("USER_DE"), os.getenv("PASS_DE")),
]
servers = [s for s in servers if s[1]]


def get_host(ip, user, password):
    """
    Helper function to establish SSH connection via Paramiko.
    Handles URL-encoding of passwords with special characters.
    """
    safe_password = urllib.parse.quote_plus(password)
    connection_string = f"paramiko://{user}:{safe_password}@{ip}"
    return testinfra.get_host(connection_string, sudo=False)

@pytest.mark.security
@pytest.mark.parametrize("name, ip, user, password", servers)
class TestSecurityRules:
    """
    SEC-01: Deep Security Audit Suite.
    Links to Requirements: REQ-001, REQ-002, REQ-003, REQ-004.
    """

    def test_os_version(self, name, ip, user, password):
        """
        REQ-004: OS Standardization (Ubuntu/Debian).
        Logic: Verify that the server runs a supported Linux distribution.
        This prevents 'configuration drift' where servers become too different to manage.
        """
        host = get_host(ip, user, password)
        os_info = host.system_info
        print(f"\n🔍 Checking {name}: Found {os_info.distribution} {os_info.release}")

        allowed_distros = ["ubuntu", "debian"]
        assert os_info.distribution.lower() in allowed_distros, \
            f"❌ Unknown OS: {os_info.distribution}"

    def test_firewall_status(self, name, ip, user, password):
        """
        REQ-002: Firewall (UFW) must be active.
        Logic: We check the command output 'ufw status' explicitly.
        We expect to see 'Status: active'. This covers both Ubuntu and Debian correctly,
        avoiding false negatives from systemd service status.
        """
        host = get_host(ip, user, password)

        # Запускаем команду консоли (как ты делал руками)
        # ufw status вернет текст, в котором мы ищем "Status: active"
        result = host.run("ufw status")

        # Проверяем, что команда выполнилась успешно
        assert result.rc == 0, f"⛔ Failed to run 'ufw status' on {name}"

        # Проверяем, что в ответе есть слово active (регистр не важен)
        assert "Status: active" in result.stdout, f"⛔ UFW is NOT active on {name}"

    @pytest.mark.xfail(reason="Fail2Ban installation pending (Task OPS-003)")
    def test_fail2ban_status(self, name, ip, user, password):
        """
        REQ-003: Intrusion Prevention System (Fail2Ban).
        Logic: Verify that 'fail2ban' service is running to block brute-force attacks.
        (Marked as xfail: We know it's missing on fresh servers, planned for next sprint).
        """
        host = get_host(ip, user, password)
        f2b = host.service("fail2ban")
        assert f2b.is_running, f"⛔ Fail2Ban is NOT running on {name}"

    @pytest.mark.xfail(reason="Root login required for current CI/CD (Task OPS-001)")
    def test_ssh_root_login_disabled(self, name, ip, user, password):
        """
        REQ-001: SSH Root Login must be disabled.
        Logic: Check /etc/ssh/sshd_config for 'PermitRootLogin no'.
        (Marked as xfail: Currently we use root user for automation, architectural exception).
        """
        host = get_host(ip, user, password)
        ssh_config = host.file("/etc/ssh/sshd_config")
        assert ssh_config.contains("PermitRootLogin no"), \
            f"⛔ {name} allows Root Login! Please fix /etc/ssh/sshd_config"