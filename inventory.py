import os
from dotenv import load_dotenv

# Load configuration from the .env file.
# This keeps our secret passwords and IP addresses out of the Git repository.
load_dotenv()

def get_backup_paths(env_var):
    """
    Takes a comma-separated string of paths from .env and makes a list.
    Example: "/etc/x-ui,/opt/outline" -> ['/etc/x-ui', '/opt/outline']
    """
    raw_paths = os.getenv(env_var, "")
    if not raw_paths:
        return []
    return [path.strip() for path in raw_paths.split(",")]

# ==========================================
# 🖥️ Server Nodes Inventory
# ==========================================
# We read server details from .env variables.
# This list acts as a Single Source of Truth (SSOT) for all tests and scripts.
_raw_servers = [
    (os.getenv("NODE_1_NAME", "Node-1"), os.getenv("NODE_1_IP"), os.getenv("NODE_1_USER"), os.getenv("NODE_1_PASS"), get_backup_paths("NODE_1_BACKUP_PATHS")),
    (os.getenv("NODE_2_NAME", "Node-2"), os.getenv("NODE_2_IP"), os.getenv("NODE_2_USER"), os.getenv("NODE_2_PASS"), get_backup_paths("NODE_2_BACKUP_PATHS")),
    (os.getenv("NODE_3_NAME", "Node-3"), os.getenv("NODE_3_IP"), os.getenv("NODE_3_USER"), os.getenv("NODE_3_PASS"), get_backup_paths("NODE_3_BACKUP_PATHS")),
    (os.getenv("NODE_4_NAME", "Node-4"), os.getenv("NODE_4_IP"), os.getenv("NODE_4_USER"), os.getenv("NODE_4_PASS"), get_backup_paths("NODE_4_BACKUP_PATHS")),
    # (os.getenv("NODE_5_NAME", "Node-5"), os.getenv("NODE_5_IP"), os.getenv("NODE_5_USER"), os.getenv("NODE_5_PASS"), get_backup_paths("NODE_5_BACKUP_PATHS")),
]

# Filter out empty nodes (where IP is not provided in .env)
SERVERS = [node for node in _raw_servers if node[1]]