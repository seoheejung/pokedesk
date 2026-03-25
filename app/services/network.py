import os
from app.services.network_latency import get_latency_ms

def is_termux():
    """
    현재 실행 환경이 Termux인지 판별
    """
    return "PREFIX" in os.environ and "com.termux" in os.environ.get("PREFIX", "")


def get_network_status():
    """
    실행 환경에 따라 네트워크 조회 방식 분기
    """

    try:
        # Termux 환경이면 termux-api 방식 import 후 실행
        if is_termux():
            from app.services.network_termux import get_network_status_termux
            return get_network_status_termux()

        # 로컬 환경이면 psutil 방식 import 후 실행
        from app.services.network_psutil import get_network_status_psutil
        return get_network_status_psutil()

    except Exception:
        # 실패 시 기본값 반환
        return "unknown"
    
def get_network_detail():
    """
    네트워크 타입 + latency + 품질 반환
    """
    network_type = get_network_status()

    # 연결 자체가 끊긴 경우
    if network_type == "offline":
        return {
            "type": "offline",
            "latency": None,
            "quality": "OFFLINE"
        }

    # ping 측정
    latency = get_latency_ms()

    # 연결은 있으나 latency 측정 실패
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