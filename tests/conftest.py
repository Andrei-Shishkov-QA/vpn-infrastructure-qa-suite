import pytest
import testinfra
import urllib.parse
import os
import sys
from allure_commons import plugin_manager
from allure_commons import hookimpl

# Add the root project folder to the system path.
# We need this to import SERVERS from inventory.py without errors.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="function")
def remote_host(request):
    """
    Core SSH connection fixture for all tests.
    It takes server data, safely encodes passwords, and creates a connection.
    """
    name, ip, user, password = request.param
    # SAFE ENCODING: We use urllib to encode special characters in the password.
    # For example, if a password has '@' or '/', it will not break the SSH URL.
    safe_password = urllib.parse.quote_plus(password) if password else ""
    # We added ?timeout=20 to give slow servers more time to respond
    connection_string = f"paramiko://{user}:{safe_password}@{ip}?timeout=20"

    # SMART LOGIC: Check if we need 'sudo'.
    # If the user is 'root', we do not need sudo. Otherwise, we enable it.
    use_sudo = (user != 'root')

    # Create the Testinfra host object
    host = testinfra.get_host(connection_string, sudo=use_sudo)

    # We add the server name to the host object.
    # This helps us print beautiful and clear error messages later.
    host.node_name = name
    return host

class AllureSanitizer:
    """
    DevSecOps Hook: This class protects our sensitive data.
    It checks Allure report parameters in memory and hides passwords and IPs.
    """

    @hookimpl(tryfirst=True)
    def report_result(self, result):
        if hasattr(result, 'parameters') and result.parameters:
            # List of words that indicate "secret data"
            sensitive_keys = {"password", "pass", "token", "secret", "key", "ip", "user"}
            for param in result.parameters:
                # If parameter name contains a sensitive word, we hide its value
                if param.name and any(key in param.name.lower() for key in sensitive_keys):
                    param.value = "'***'"
                    param.mode = "masked"

def pytest_configure(config):
    """
    This function runs automatically when Pytest starts.
    It turns on our AllureSanitizer to protect the test reports.
    """
    if config.pluginmanager.getplugin("allure_pytest"):
        plugin_manager.register(AllureSanitizer(), name="allure_sanitizer")