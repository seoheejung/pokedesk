import subprocess
import json


def get_location_termux():
    """
    Termux에서 현재 위치 1회 조회
    """

    try:
        # 1차: 빠른 캐시 위치
        return subprocess.check_output(
            ["termux-location", "-p", "network", "-r", "last"],
            text=True,
            timeout=3
        )
    except Exception:
        try:
            # 2차: 실제 위치 요청
            return subprocess.check_output(
                ["termux-location", "-p", "network"],
                text=True,
                timeout=5
            )
        except Exception:
            return None