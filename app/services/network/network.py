import os
from app.services.network.latency import get_latency_ms

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
            from app.services.network.termux_impl import get_network_status_termux
            return get_network_status_termux()

        # 로컬 환경이면 psutil 방식 import 후 실행
        from app.services.network.psutil_impl import get_network_status_psutil
        return get_network_status_psutil()

    except Exception:
        # 실패 시 기본값 반환
        return "unknown"
    
def get_network_detail():
    """
    실행 환경에 따라 네트워크 상세 정보 조회
    반환값:
    {
        "type": "wifi" | "connected" | "offline" | "unknown",
        "latency": int | None,
        "quality": "GOOD" | "NORMAL" | "SLOW" | "OFFLINE" | "UNKNOWN"
    }
    """
    try:
        if is_termux():
            from app.services.network.termux_impl import get_network_detail_termux
            return get_network_detail_termux()

        from app.services.network.psutil_impl import get_network_detail_psutil
        return get_network_detail_psutil()

    except Exception:
        return {
            "type": "unknown",
            "latency": None,
            "quality": "UNKNOWN"
        }