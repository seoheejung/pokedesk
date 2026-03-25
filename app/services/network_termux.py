import json
import subprocess


def get_network_status_termux() -> str:
    """
    Termux 환경에서 네트워크 상태 조회

    반환값:
    - wifi
    - mobile
    - ethernet
    - offline
    - unknown
    """
    try:
        result = subprocess.run(
            ["termux-connection-info"],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)

        connected = data.get("connected", False)
        network_type = data.get("type")

        if not connected:
            return "offline"

        if network_type in ("wifi", "mobile", "ethernet"):
            return network_type

        return "unknown"

    except Exception:
        return "unknown"