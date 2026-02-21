import pytest
import allure
from inventory import SERVERS


# We use 'indirect=True' to pass server data to the 'remote_host' fixture.
# This makes the test code very clean and readable.
@allure.suite("Infrastructure Security Audit")
@pytest.mark.parametrize("remote_host", [s[:4] for s in SERVERS], ids=[s[0] for s in SERVERS], indirect=True)
class TestSecurityInfrastructure:

    @allure.id("REQ-000")
    @allure.title("Smoke Test: SSH Connectivity")
    @pytest.mark.smoke
    def test_server_connectivity(self, remote_host):
        """
        Verifies that the server is reachable and accepting SSH commands.
        This is the foundation for all other infrastructure tests.
        """
        with allure.step("Execute 'hostname' command"):
            actual_hostname = remote_host.check_output("hostname")

        with allure.step("Verify response"):
            assert actual_hostname is not None
            print(f"✅ Successfully connected to {remote_host.node_name}")

    @allure.id("REQ-004")
    @allure.title("Audit: OS Distribution Compliance")
    def test_os_version(self, remote_host):
        """Standardization check: Ensures the node runs a supported Linux version."""
        distro = remote_host.system_info.distribution.lower()
        allowed_distros = ["ubuntu", "debian"]

        assert distro in allowed_distros, f"❌ Unsupported OS: {distro} on {remote_host.node_name}"

    @allure.id("REQ-002")
    @allure.title("Audit: Firewall (UFW) Status")
    @pytest.mark.security
    def test_firewall_status(self, remote_host):
        """Ensures that the Uncomplicated Firewall (UFW) is active and protecting the node."""
        with allure.step("Check UFW status"):
            result = remote_host.run("ufw status")

        assert "Status: active" in result.stdout, f"⚠️ UFW is INACTIVE on {remote_host.node_name}!"

    @allure.id("REQ-003")
    @allure.title("Audit: Fail2Ban Service with Self-Healing")
    @pytest.mark.security
    def test_fail2ban_status(self, remote_host):
        """
        Verifies Fail2Ban service.
        If it is missing or stopped, the test attempts to fix the system automatically.
        """
        f2b_pkg = remote_host.package("fail2ban")
        f2b_service = remote_host.service("fail2ban")

        # SELF-HEALING LOGIC
        if not f2b_pkg.is_installed or not f2b_service.is_running:
            with allure.step("Self-Healing: Attempting to repair Fail2Ban"):
                # Update cache and install packages
                remote_host.run("apt-get update")
                distro = remote_host.system_info.distribution.lower()

                # Debian requires rsyslog for Fail2Ban to work correctly
                pkgs = "fail2ban rsyslog" if distro == "debian" else "fail2ban"
                remote_host.run(f"DEBIAN_FRONTEND=noninteractive apt-get install -y {pkgs}")

                # Try to enable and restart the service
                remote_host.run("systemctl enable fail2ban")
                remote_host.run("systemctl restart fail2ban")

        with allure.step("Final verification"):
            assert f2b_service.is_running, f"❌ Fail2Ban is DEAD on {remote_host.node_name} even after repair attempt."