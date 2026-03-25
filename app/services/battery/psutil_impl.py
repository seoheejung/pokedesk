import psutil


def get_battery_status_psutil():
    """
    Windows / 일반 Linux용 배터리 조회
    - 배터리 정보가 없으면 기본값 반환
    """

    try:
        # psutil에서 배터리 정보 조회
        info = psutil.sensors_battery()

        # 배터리 정보 없으면 fallback
        if info is None:
            return 100, False

        # 안전하게 값 추출
        battery = int(info.percent) if info.percent is not None else 100
        charging = bool(info.power_plugged)

        return battery, charging

    # 예외 발생 시 fallback
    except Exception:
        return 100, False