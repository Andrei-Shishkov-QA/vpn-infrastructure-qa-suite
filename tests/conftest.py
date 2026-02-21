import pytest
import os
from allure_commons import plugin_manager
from allure_commons import hookimpl
"""
Global Security Hook (DevSecOps)
Intercepts Allure reports in memory before serialization to disk.
Destructively mutates and masks sensitive credentials (passwords, IPs, users) 
to prevent security leaks in publicly hosted Allure HTML reports.
"""
# Класс-санитайзер, который перехватывает отчет перед записью на диск
class AllureSecuritySanitizer:
    @hookimpl(tryfirst=True)
    def report_result(self, result):
        """
        Физически удаляет пароли из объекта отчета в оперативной памяти.
        """
        if hasattr(result, 'parameters') and result.parameters:
            # Список слов, которые мы считаем опасными
            sensitive_keys = {"password", "pass", "passw", "token", "secret", "key", "credential", "ip", "user"}

            for param in result.parameters:
                if param.name:
                    name_lower = param.name.lower()
                    # Если имя параметра содержит "опасное" слово
                    if any(key in name_lower for key in sensitive_keys):
                        # Заменяем реальное значение на маску
                        param.value = "'***'"
                        param.mode = "masked"


def pytest_configure(config):
    """
    Регистрирует наш защитный плагин в системе Allure при запуске тестов.
    """
    if config.pluginmanager.getplugin("allure_pytest"):
        sanitizer = AllureSecuritySanitizer()
        plugin_manager.register(sanitizer, name="allure_security_sanitizer")