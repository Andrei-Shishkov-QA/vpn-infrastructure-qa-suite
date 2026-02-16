import paramiko
# Самая важная строка: мы берем список серверов из SSOT "inventory.py"
from inventory import SERVERS


def install_iperf(name, ip, user, password):
    print(f"🚀 Connecting to {name} ({ip})...")
    try:
        # Настройка SSH клиента
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=user, password=password, timeout=10)

        # Команда установки (Update + Install)
        # -y означает "отвечать Yes на все вопросы системы"
        command = "export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y iperf3"

        print(f"   📦 Installing iperf3 on {name}...")
        stdin, stdout, stderr = ssh.exec_command(command)

        # Ждем завершения команды и получаем код результата
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            print(f"   ✅ SUCCESS: iperf3 installed/updated on {name}")
        else:
            print(f"   ❌ ERROR on {name}:")
            print(stderr.read().decode())

        ssh.close()

    except Exception as e:
        print(f"   🔥 CONNECTION FAILED to {name}: {e}")


if __name__ == "__main__":
    print(f"--- Starting Deployment on {len(SERVERS)} servers ---")

    # Цикл по всем серверам из inventory.py
    for server_info in SERVERS:
        # Распаковываем данные (Name, IP, User, Password) и передаем в функцию
        install_iperf(*server_info)

    print("--- Deployment Finished ---")