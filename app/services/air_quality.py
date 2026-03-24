import requests


def get_air_quality(lat=None, lon=None):
    """
    현재 공기질 조회
    - Open-Meteo Air Quality API 사용
    """

    try:
        # Open-Meteo 현재 공기질 조회
        response = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "pm10,pm2_5,us_aqi",
                "timezone": "Asia/Seoul",
            },
            timeout=3,
        )

        # HTTP 에러 발생 시 예외 처리
        response.raise_for_status()

        # JSON 변환
        data = response.json()

        # 현재 공기질 블록 추출
        current = data.get("current", {})

        # PM10
        pm10 = current.get("pm10")

        # PM2.5
        pm2_5 = current.get("pm2_5")

        # 미국 기준 AQI
        us_aqi = current.get("us_aqi")

        # AQI 문구 변환
        if us_aqi is None:
            air_text = "공기질 정보 없음"
        elif us_aqi <= 50:
            air_text = "좋음"
        elif us_aqi <= 100:
            air_text = "보통"
        elif us_aqi <= 150:
            air_text = "민감군 주의"
        elif us_aqi <= 200:
            air_text = "나쁨"
        elif us_aqi <= 300:
            air_text = "매우 나쁨"
        else:
            air_text = "위험"

        # 응답 구조 통일
        return {
            "pm10": pm10,
            "pm2_5": pm2_5,
            "us_aqi": us_aqi,
            "air_text": air_text,
        }

    # 실패 시 기본값 반환
    except Exception:
        return {
            "pm10": None,
            "pm2_5": None,
            "us_aqi": None,
            "air_text": "공기질 정보 없음",
        }