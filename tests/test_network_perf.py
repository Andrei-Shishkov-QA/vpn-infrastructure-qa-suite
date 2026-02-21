import pytest
import allure
import os
from pythonping import ping
from inventory import SERVERS


@allure.suite("Network Performance & Capacity")
@pytest.mark.parametrize("remote_host", [s[:4] for s in SERVERS], ids=[s[0] for s in SERVERS], indirect=True)
class TestNetworkPerformance:

    @allure.id("REQ-005.1")
    @allure.title("Network: Latency and Packet Loss (Client to Server)")
    @pytest.mark.network
    @pytest.mark.skipif(os.getenv("GITHUB_ACTIONS") == "true", reason="ICMP ping is blocked in GitHub Actions")
    def test_latency_from_client(self, remote_host):
        """
        Measures the Round-Trip Time (RTT) from the local machine to the server.
        Ensures that latency is within acceptable limits for a stable VPN connection.
        """
        ip = remote_host.backend.hostname  # Get IP from the host object
        print(f"\n📡 Pinging {remote_host.node_name} ({ip})...")

        response = ping(ip, count=4)
        loss = response.packet_loss * 100
        avg_rtt = response.rtt_avg_ms

        with allure.step(f"Analyze Ping results for {remote_host.node_name}"):
            allure.attach(f"Loss: {loss}% | Avg RTT: {avg_rtt}ms", name="Ping Stats")

            assert loss == 0, f"❌ Critical packet loss on {remote_host.node_name}: {loss}%"

            # Thresholds: 100ms for RU nodes, 300ms for Global/EU nodes
            threshold = 100 if "RU" in remote_host.node_name else 300
            assert avg_rtt < threshold, f"⚠️ High latency on {remote_host.node_name}: {avg_rtt}ms"

    @allure.id("REQ-005.2")
    @allure.title("Network: Download Speed via Global CDN")
    @pytest.mark.network
    def test_server_download_speed(self, remote_host):
        """
        Verifies the server's internet bandwidth by downloading a test file from a Global CDN.
        This simulates real-world heavy usage (e.g., 4K video streaming).
        """
        # We use Cachefly CDN because it automatically selects the fastest mirror for each VPS
        target_url = "http://cachefly.cachefly.net/100mb.test"

        # Command to measure download speed in bytes/sec
        cmd = f"curl -o /dev/null --silent --write-out '%{{speed_download}}' --max-time 20 --connect-timeout 10 {target_url}"

        with allure.step("Execute speed test on remote server"):
            result = remote_host.run(cmd)

            if result.rc != 0:
                pytest.fail(f"❌ Could not reach CDN from {remote_host.node_name}: {result.stderr}")

            # Convert bytes/sec to Mbps (Megabits per second)
            bytes_sec = float(result.stdout.strip())
            mbps = (bytes_sec * 8) / 1_000_000

            print(f"🏎️  {remote_host.node_name} Speed: {mbps:.2f} Mbps")
            allure.attach(f"Speed: {mbps:.2f} Mbps", name="Bandwidth Result")

            # Requirement: Speed must be > 30 Mbps for high-quality streaming
            assert mbps > 30, f"❌ Connection too slow on {remote_host.node_name}: {mbps:.2f} Mbps"