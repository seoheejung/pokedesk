import json
import subprocess


def get_network_status_termux():
    """
    Termux 환경에서 Wi-Fi 상태만 조회
    """
    try:
        result = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)

        if data.get("supplicant_state") == "COMPLETED" and data.get("ssid"):
            return "wifi"

        return "offline"

    except Exception:
        return "unknown"


def get_network_detail_termux():
    """
    Termux 환경에서 Wi-Fi 상세 정보 조회
    RSSI 기반으로 품질 판단
    """
    try:
        result = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)

        if data.get("supplicant_state") != "COMPLETED" or not data.get("ssid"):
            return {
                "type": "offline",
                "latency": None,
                "quality": "OFFLINE"
            }

        rssi = data.get("rssi")

        if rssi is None:
            quality = "UNKNOWN"
        elif rssi >= -50:
            quality = "GOOD"
        elif rssi >= -67:
            quality = "NORMAL"
        else:
            quality = "SLOW"

        return {
            "type": "wifi",
            "latency": None,
            "quality": quality
        }

    except Exception:
        return {
            "type": "unknown",
            "latency": None,
            "quality": "UNKNOWN"
        }