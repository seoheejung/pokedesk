import psutil
from app.services.network.latency import get_latency_ms


def get_network_status_psutil():
    """
    로컬 환경에서 네트워크 연결 상태 조회
    """
    try:
        stats = psutil.net_if_stats()

        for interface_name, interface_stat in stats.items():
            if interface_stat.isup and not interface_name.lower().startswith("lo"):
                return "connected"

        return "offline"

    except Exception:
        return "unknown"


def get_network_detail_psutil():
    """
    로컬 환경에서 네트워크 상세 정보 조회
    ping 기반 latency + 품질 판단
    """
    network_type = get_network_status_psutil()

    if network_type == "offline":
        return {
            "type": "offline",
            "latency": None,
            "quality": "OFFLINE"
        }

    latency = get_latency_ms()

    if latency is None:
        return {
            "type": network_type,
            "latency": None,
            "quality": "UNKNOWN"
        }

    if latency < 50:
        quality = "GOOD"
    elif latency < 150:
        quality = "NORMAL"
    else:
        quality = "SLOW"

    return {
        "type": network_type,
        "latency": latency,
        "quality": quality
    }