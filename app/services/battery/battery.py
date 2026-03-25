import os


def is_termux():
    """
    현재 실행 환경이 Termux인지 판별
    """
    return "PREFIX" in os.environ and "com.termux" in os.environ.get("PREFIX", "")


def get_battery_status():
    """
    실행 환경에 따라 배터리 조회 방식 분기
    """

    try:
        # Termux 환경이면 termux-api 방식 import 후 실행
        if is_termux():
            from app.services.battery.termux_impl import get_battery_status_termux
            return get_battery_status_termux()

        # 로컬 환경이면 psutil 방식 import 후 실행
        from app.services.battery.psutil_impl import get_battery_status_psutil
        return get_battery_status_psutil()

    except Exception:
        # 실패 시 기본값 반환
        return 100, False