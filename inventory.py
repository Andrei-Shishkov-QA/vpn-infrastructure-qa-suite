import os
from dotenv import load_dotenv

load_dotenv()
"""
Infrastructure Inventory (Single Source of Truth).
Dynamically loads server credentials from secure environment variables (.env).
No sensitive data is hardcoded in this repository.
"""
# Вспомогательная функция для превращения строки "path1,path2" в список
def get_backup_paths(env_var):
    raw = os.getenv(env_var, "")
    if not raw:
        return []
    return [p.strip() for p in raw.split(",")]

# Описание инфраструктуры
# Мы используем generic-имена (Node 1, Node 2), чтобы проект был универсальным.
# В реальном .env вы можете привязать к ним любые сервера (хоть NL, хоть US).

_raw_servers = [
    # (Human Name, IP, User, Password)
    (os.getenv("NODE_1_NAME", "Node-1"), os.getenv("NODE_1_IP"), os.getenv("NODE_1_USER"), os.getenv("NODE_1_PASS"), get_backup_paths("NODE_1_BACKUP_PATHS")),
    (os.getenv("NODE_2_NAME", "Node-2"), os.getenv("NODE_2_IP"), os.getenv("NODE_2_USER"), os.getenv("NODE_2_PASS"), get_backup_paths("NODE_2_BACKUP_PATHS")),
    (os.getenv("NODE_3_NAME", "Node-3"), os.getenv("NODE_3_IP"), os.getenv("NODE_3_USER"), os.getenv("NODE_3_PASS"), get_backup_paths("NODE_3_BACKUP_PATHS")),
    (os.getenv("NODE_4_NAME", "Node-4"), os.getenv("NODE_4_IP"), os.getenv("NODE_4_USER"), os.getenv("NODE_4_PASS"), get_backup_paths("NODE_4_BACKUP_PATHS")),

    # Хотите 5-й сервер? Раскомментируйте и добавьте в .env:
    # (os.getenv("NODE_5_NAME"), os.getenv("NODE_5_IP"), os.getenv("NODE_5_USER"), os.getenv("NODE_5_PASS"), get_backup_paths("NODE_5_BACKUP_PATHS")),
]

# Фильтруем те узлы, для которых не задан IP (чтобы тесты не падали на пустых слотах)
SERVERS = [s for s in _raw_servers if s[1]]