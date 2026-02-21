import pytest
import testinfra
import os
import sys
import urllib.parse
"""
    Requirement: REQ-003 - Intrusion Prevention System (Fail2Ban).
    Logic: Verifies that 'fail2ban' is installed and actively running.
    Self-Healing: If missing or crashed, the script automatically installs the package, 
    resolves OS-specific dependencies (e.g., rsyslog for Debian 12), and restarts the service.
    """
# Добавляем корневую папку в путь поиска, чтобы Python увидел inventory.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory import SERVERS as servers

def get_host(ip, user, password):
    """
    Helper function to establish SSH connection via Paramiko.
    Handles URL-encoding of passwords with special characters.
    """
    safe_password = urllib.parse.quote_plus(password)
    connection_string = f"paramiko://{user}:{safe_password}@{ip}"
    return testinfra.get_host(connection_string, sudo=False)

@pytest.mark.security
@pytest.mark.parametrize("name, ip, user, password", [s[:4] for s in servers], ids=[s[0] for s in servers])
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

    def test_fail2ban_status(self, name, ip, user, password):
        """
        REQ-003: Intrusion Prevention System (Fail2Ban).
        Self-Healing 2.0: Install if missing, AND restart if stopped/crashed.
        """
        host = get_host(ip, user, password)
        fail2ban_pkg = host.package("fail2ban")
        f2b_service = host.service("fail2ban")

        # ТРИГГЕР: Пакет не установлен ИЛИ служба не работает
        if not fail2ban_pkg.is_installed or not f2b_service.is_running:
            print(f"\n🛠️ fail2ban не работает на {name}. Начинаю ремонт...")

            # Блок 1: Если вообще не установлен — ставим
            if not fail2ban_pkg.is_installed:
                host.run("apt-get update")
                if host.system_info.distribution.lower() == "debian":
                    print(f"   [Debian Fix] Устанавливаем fail2ban + rsyslog...")
                    host.run("DEBIAN_FRONTEND=noninteractive apt-get install -y fail2ban rsyslog")
                    host.run("systemctl enable rsyslog")
                    host.run("systemctl start rsyslog")
                else:
                    host.run("DEBIAN_FRONTEND=noninteractive apt-get install -y fail2ban")

            # Блок 2: Спец-фикс для Debian (принудительно создаем лог-файл, чтобы f2b не падал)
            if host.system_info.distribution.lower() == "debian":
                host.run("touch /var/log/auth.log")

            # Блок 3: Пытаемся запустить службу
            host.run("systemctl enable fail2ban")
            restart_cmd = host.run("systemctl restart fail2ban")

            # Блок 4: Если запуск провалился — выводим системный журнал для дебага
            if restart_cmd.rc != 0:
                logs = host.run("journalctl -u fail2ban -n 15 --no-pager").stdout
                pytest.fail(f"❌ fail2ban крашится при запуске на {name}!\nЛоги сервера:\n{logs}")

            print(f"✅ fail2ban успешно починен и запущен на {name}")

        # Финальная проверка
        f2b_check = host.service("fail2ban")
        assert f2b_check.is_running, f"⛔ Fail2Ban is NOT running on {name}"
        assert f2b_check.is_enabled, f"⛔ Fail2Ban is NOT enabled on startup on {name}"

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