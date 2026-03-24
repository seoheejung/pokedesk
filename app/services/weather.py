import requests

# 날씨 상태 코드 문구 매핑
WEATHER_CODE_MAP = {
    0: "맑음",
    1: "대체로 맑음",
    2: "부분적으로 흐림",
    3: "흐림",
    45: "안개",
    48: "서리 안개",
    51: "약한 이슬비",
    53: "이슬비",
    55: "강한 이슬비",
    61: "약한 비",
    63: "비",
    65: "강한 비",
    71: "약한 눈",
    73: "눈",
    75: "강한 눈",
    80: "약한 소나기",
    81: "소나기",
    82: "강한 소나기",
    95: "뇌우",
}


def get_weather(lat=None, lon=None):
    """
    현재 날씨 조회
    - Open-Meteo current API 사용
    """

    try:
        # Open-Meteo 현재 날씨 조회
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weather_code",
                "timezone": "Asia/Seoul",
            },
            timeout=3,
        )

        # HTTP 에러 발생 시 예외 처리
        response.raise_for_status()

        # JSON 변환
        data = response.json()

        # 현재 날씨 블록 추출
        current = data.get("current", {})

        # 현재 기온
        temperature = current.get("temperature_2m")

        # 날씨 코드
        weather_code = current.get("weather_code")

        # 한글 날씨명 변환
        weather_text = WEATHER_CODE_MAP.get(weather_code, "알 수 없음")

        # 응답 구조 통일
        return {
            "temperature": temperature,
            "weather_code": weather_code,
            "weather_text": weather_text,
        }

    # 실패 시 기본값 반환
    except Exception:
        return {
            "temperature": None,
            "weather_code": None,
            "weather_text": "날씨 정보 없음",
        }