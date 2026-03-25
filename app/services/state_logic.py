def build_state_message(battery: int, charging: bool, idle_minutes: int) -> tuple[str, str]:
    """
    상태 기반 시스템 메시지 생성
    """

    # 배터리 경고 상태 (최우선)
    if battery <= 20:
        return "warning", f"배터리 잔량이 {battery}%입니다."

    # 충전 중
    if charging:
        return "healing", "충전 중입니다."

    # 장시간 미사용
    if idle_minutes >= 30:
        return "sleep", f"{idle_minutes}분 동안 입력이 없습니다."

    # 일정 시간 미사용
    if idle_minutes >= 10:
        return "focus", "장시간 입력 없음 상태입니다."

    # 기본 상태
    return "idle", "시스템 대기 상태입니다."


def build_environment_message(weather, air_quality) -> str:
    """
    환경 정보 기반 메시지 생성
    """

    if air_quality.get("us_aqi") is not None and air_quality["us_aqi"] > 100:
        return f"공기질 상태가 {air_quality['air_text']} 수준입니다."

    weather_text = weather.get("weather_text")

    if weather_text in ["약한 비", "비", "강한 비", "약한 소나기", "소나기", "강한 소나기"]:
        return "강수 상태가 감지되었습니다."

    if weather_text in ["약한 눈", "눈", "강한 눈"]:
        return "강설 상태가 감지되었습니다."

    if weather_text in ["흐림", "부분적으로 흐림", "안개", "서리 안개"]:
        return f"현재 날씨는 {weather_text}입니다."

    return "환경 상태는 안정적입니다."
