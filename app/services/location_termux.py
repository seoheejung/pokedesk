import subprocess
import json


def get_location_termux():
    """
    Termux에서 현재 위치 조회 (lat, lon 반환)
    """

    try:
        # 1차: 빠른 캐시 위치
        result = subprocess.check_output(
            ["termux-location", "-p", "network", "-r", "last"],
            text=True,
            timeout=3
        )
        data = json.loads(result)
        return data["latitude"], data["longitude"]

    except Exception:
        try:
            # 2차: 실제 위치 요청
            result = subprocess.check_output(
                ["termux-location", "-p", "network"],
                text=True,
                timeout=5
            )
            data = json.loads(result)
            return data["latitude"], data["longitude"]

        except Exception:
            return None, None