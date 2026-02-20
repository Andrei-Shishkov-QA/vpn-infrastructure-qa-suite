import pytest
import sys
import os
import testinfra
import urllib.parse
from pythonping import ping

# --- МАГИЯ ИМПОРТА ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inventory import SERVERS

test_data = [(s[0], s[1], s[2], s[3]) for s in SERVERS]


def get_host(ip, user, password):
    safe_password = urllib.parse.quote_plus(password) if password else ""
    connection_string = f"paramiko://{user}:{safe_password}@{ip}"

    # 🔥 УМНАЯ ЛОГИКА (Smart Sudo):
    use_sudo = False if user == 'root' else True

    return testinfra.get_host(connection_string, sudo=use_sudo)


class TestNetworkPerformance:

    @pytest.mark.network
    @pytest.mark.parametrize("name, ip, user, passw", [s[:4] for s in test_data])
    def test_latency_and_loss_from_client(self, name, ip, user, passw):
        """
        REQ-005 (Part 1): Пинг от тебя до сервера.
        """
        print(f"\n📡 [Client -> Server] Pinging {name} ({ip})...")
        response = ping(ip, count=4, verbose=False)

        loss = response.packet_loss * 100
        avg_rtt = response.rtt_avg_ms

        print(f"   📉 Packet Loss: {loss}%")
        print(f"   ⏱️ Avg Latency: {avg_rtt} ms")

        assert loss == 0, f"❌ PACKET LOSS on {name}: {loss}%"
        threshold = 100 if "RU" in name else 300
        assert avg_rtt < threshold, f"⚠️ SLOW PING on {name}: {avg_rtt}ms"

    @pytest.mark.network
    @pytest.mark.parametrize("name, ip, user, passw", [s[:4] for s in test_data])
    def test_server_download_speed_http(self, name, ip, user, passw):
        """
        REQ-005 (Part 2): Скорость (HTTP Download).
        Используем Global CDN (Cachefly) для проверки реальной ширины канала.
        """
        print(f"\n🚀 [Server -> Internet] CDN Speed Test on {name}...")
        host = get_host(ip, user, passw)

        # ✅ FIX: Используем Global CDN (Cachefly) вместо Selectel.
        # Он автоматически выбирает ближайший сервер к каждому VPS.
        target_url = "http://cachefly.cachefly.net/100mb.test"

        # Таймаут 15 секунд. Если CDN не отдал файл за 15 сек - интернет совсем плохой.
        cmd = f"curl -o /dev/null --silent --write-out '%{{speed_download}}' --max-time 15 --connect-timeout 5 {target_url}"

        try:
            result = host.run(cmd)

            if result.rc != 0:
                # Если Cachefly недоступен - это ЧП, лучше упасть с ошибкой, чем пропустить.
                pytest.fail(f"⚠️ CDN unreachable: {result.stderr}")

            bytes_sec = float(result.stdout.strip())
            mbps = (bytes_sec * 8) / 1_000_000

            print(f"   🏎️ Download Speed: {mbps:.2f} Mbps")

            # Порог 30 Мбит/с - это гарантия HD видео.
            assert mbps > 30, f"❌ SLOW CONNECTION on {name}: {mbps:.2f} Mbps"

        except Exception as e:
            pytest.fail(f"🔥 Script Error: {e}")