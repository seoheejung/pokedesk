import psutil

def get_network_status_psutil() -> str:
    """
    로컬 환경에서 네트워크 상태 조회

    psutil만으로는 Wi-Fi / Mobile 구분이 어렵기 때문에
    연결 여부 중심으로만 판단한다.

    반환값:
    - connected
    - offline
    - unknown
    """
    try:
        stats = psutil.net_if_stats()

        for interface_name, interface_stat in stats.items():
            if interface_stat.isup and not interface_name.lower().startswith("lo"):
                return "connected"

        return "offline"

    except Exception:
        return "unknown"