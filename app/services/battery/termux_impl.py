import subprocess
import json


def get_battery_status_termux():
    """
    Termux용 배터리 조회
    - termux-battery-status 명령 결과를 사용
    """

    try:
        # termux-battery-status 실행
        result = subprocess.check_output(
            ["termux-battery-status"],
            text=True,
            timeout=2  # 무한 대기 방지
        )

        # JSON 파싱
        data = json.loads(result)

        # 안전하게 값 추출
        battery = int(data.get("percentage", 100))
        charging = data.get("status") == "CHARGING"

        return battery, charging

    # 실패 시 기본값 반환
    except (subprocess.SubprocessError, json.JSONDecodeError, KeyError, ValueError):
        return 100, False