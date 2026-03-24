import subprocess
import json


def get_location_termux():
    """
    Termux에서 현재 위치 1회 조회
    """

    try:
        result = subprocess.check_output(
            ["termux-location", "-p", "gps", "-r", "once"],
            text=True,
            timeout=5
        )

        data = json.loads(result)

        lat = data.get("latitude")
        lon = data.get("longitude")

        if lat is None or lon is None:
            return None, None

        return lat, lon

    except Exception:
        return None, None