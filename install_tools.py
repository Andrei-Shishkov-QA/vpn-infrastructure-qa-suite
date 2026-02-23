import paramiko
import sys
import os

# Import the Single Source of Truth (SSOT) from inventory.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from inventory import SERVERS
except ImportError:
    print("❌ Error: inventory.py not found.")
    sys.exit(1)


def install_iperf(name, ip, user, password, backup_paths=None):
    """
    Connects to a remote server and installs iperf3.
    This ensures the server is ready for network performance testing.
    """
    print(f"🚀 Connecting to {name} ({ip})...")

    try:
        # Initialize SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect using optimized settings for high-latency networks
        ssh.connect(
            ip,
            username=user,
            password=password,
            timeout=15,
            look_for_keys=False,
            allow_agent=False
        )

        # Installation command:
        # 1. Sets non-interactive mode (prevents the system from asking questions)
        # 2. Updates package lists
        # 3. Installs iperf3 with '-y' to auto-confirm
        install_cmd = "export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y iperf3"

        print(f"   📦 Running update & install on {name}...")
        stdin, stdout, stderr = ssh.exec_command(install_cmd)

        # Wait for the command to finish and get the return code
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            print(f"   ✅ SUCCESS: iperf3 is ready on {name}")
        else:
            print(f"   ❌ ERROR on {name}:")
            print(stderr.read().decode())

        ssh.close()

    except Exception as e:
        print(f"   🔥 CONNECTION FAILED to {name}: {e}")


if __name__ == "__main__":
    print(f"--- Starting Dependency Deployment on {len(SERVERS)} servers ---")

    # Iterate through each server in the inventory
    for server_info in SERVERS:
        # Unpack the server data.
        # Since inventory.py might have 5 fields, we take the first 4 for this function.
        install_iperf(*server_info[:4])

    print("--- Deployment Finished ---")