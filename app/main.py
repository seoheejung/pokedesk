from flask import Flask, render_template, jsonify
from datetime import datetime
from app.services.battery import get_battery_status
from app.services.weather import get_weather
from app.services.air_quality import get_air_quality
from app.services.location_termux import get_location_termux
from app.services.geocoding import get_address

DEFAULT_LAT = 37.5665
DEFAULT_LON = 126.9780

DEVICE_LAT, DEVICE_LON = get_location_termux()

if DEVICE_LAT is None or DEVICE_LON is None:
    DEVICE_LAT, DEVICE_LON = DEFAULT_LAT, DEFAULT_LON
DEVICE_LOCATION = get_address(DEVICE_LAT, DEVICE_LON)

app = Flask(
    __name__,
    template_folder="../web/templates",
    static_folder="../web/static"
)

# 상태별 포켓몬 매핑
STATE_POKEMON = {
    "idle": {
        "name": "pikachu",
        "display_name": "피카츄",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
    },
    "sleep": {
        "name": "snorlax",
        "display_name": "잠만보",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/143.png",
    },
    "healing": {
        "name": "chansey",
        "display_name": "럭키",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/113.png",
    },
    "warning": {
        "name": "gastly",
        "display_name": "고오스",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/92.png",
    },
    "focus": {
        "name": "abra",
        "display_name": "케이시",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/63.png",
    },
    "event": {
        "name": "rotom",
        "display_name": "로토무",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/479.png",
    },
}

# 이벤트 로그 저장 (메모리 기반)
EVENT_LOGS = []

# 이전 상태 저장 (변화 감지용)
LAST_STATE = None

# 이전 충전 상태 저장
LAST_CHARGING = None

# 이전 배터리 경고 상태 저장
LAST_BATTERY_WARNING = None

# 마지막 사용자 활동 시각
LAST_ACTIVITY_AT = datetime.now()

# 마지막 activity 로그 기록 시각 (로그 과다 방지)
LAST_ACTIVITY_LOG_AT = None


def add_event(event_type: str, message: str) -> None:
    """
    이벤트 로그 추가
    """

    # 현재 시각 문자열 생성
    now = datetime.now().strftime("%H:%M:%S")

    # 새 이벤트를 맨 앞에 추가
    EVENT_LOGS.insert(0, {
        "time": now,
        "type": event_type,
        "message": message,
    })

    # 최근 10개까지만 유지
    del EVENT_LOGS[10:]


def get_idle_minutes() -> int:
    """
    마지막 활동 시각 기준으로 유휴 시간(분) 계산
    """

    # 현재 시각과 마지막 활동 시간 차이 계산
    delta = datetime.now() - LAST_ACTIVITY_AT

    # 초 → 분 변환
    return int(delta.total_seconds() // 60)


def calculate_state(battery: int, charging: bool, idle_minutes: int) -> str:
    """
    현재 상태 결정
    """

    # 배터리 경고 상태 (최우선)
    if battery <= 20:
        return "warning"

    # 충전 중
    if charging:
        return "healing"

    # 장시간 미사용
    if idle_minutes >= 30:
        return "sleep"

    # 일정 시간 미사용
    if idle_minutes >= 10:
        return "focus"

    # 기본 상태
    return "idle"


def build_message(state, battery, idle_minutes, weather, air_quality) -> str:
    """
    상태 + 날씨 + 공기질 기반 메시지 생성
    """

    # 공기질이 매우 안 좋으면 우선 경고
    if air_quality.get("us_aqi") is not None and air_quality["us_aqi"] > 100:
        return f"공기 상태가 {air_quality['air_text']}이야. 실내 대기를 권장할게."

    # 배터리 경고 상태
    if state == "warning":
        return f"배터리가 {battery}%야. 경고 상태야."

    # 충전 상태
    if state == "healing":
        return "충전 중이야. 회복 상태야."

    # 수면 상태
    if state == "sleep":
        return f"{idle_minutes}분 동안 입력이 없어. 잠든 상태야."

    # 집중 상태
    if state == "focus":
        return "집중 상태 유지 중이야."

    # 비/눈 같은 날씨 반영
    weather_text = weather.get("weather_text")

    if weather_text in ["약한 비", "비", "강한 비", "약한 소나기", "소나기", "강한 소나기"]:
        return "비가 오고 있어. 물 타입 분위기가 강해."

    if weather_text in ["약한 눈", "눈", "강한 눈"]:
        return "눈이 내리고 있어. 조용하고 차가운 분위기야."

    if weather_text in ["흐림", "부분적으로 흐림", "안개", "서리 안개"]:
        return f"지금 날씨는 {weather_text}이야. 차분하게 대기 중이야."

    # 기본 메시지
    return "대기 상태야."


def update_event_logs(state: str, battery: int, charging: bool) -> None:
    """
    상태 변화에 따라 이벤트 로그 갱신
    - 상태 변경 시 로그 추가
    - 충전 시작/해제 시 로그 추가
    - 배터리 부족 진입 시 로그 추가
    """

    # 전역 상태 사용 선언
    global LAST_STATE, LAST_CHARGING, LAST_BATTERY_WARNING

    # 마지막 상태가 없으면 앱 시작 로그 추가
    if LAST_STATE is None:
        add_event("system", "PokeDesk 시작")
        add_event("state", f"init → {state}")
        LAST_STATE = state

    # 상태가 바뀌었으면 상태 변경 로그 추가
    if LAST_STATE != state:
        add_event("state", f"{LAST_STATE} → {state}")
        LAST_STATE = state

    # 마지막 충전 상태가 없으면 현재 값으로 초기화
    if LAST_CHARGING is None:
        LAST_CHARGING = charging

    # 충전 시작 감지
    if LAST_CHARGING is False and charging is True:
        add_event("power", "충전 시작")
        LAST_CHARGING = charging

    # 충전 해제 감지
    elif LAST_CHARGING is True and charging is False:
        add_event("power", "충전 해제")
        LAST_CHARGING = charging

    # 현재 배터리 부족 여부 계산
    battery_warning = battery <= 20

    # 마지막 배터리 경고 상태가 없으면 현재 값으로 초기화
    if LAST_BATTERY_WARNING is None:
        LAST_BATTERY_WARNING = battery_warning

    # 배터리 부족 상태 진입 감지
    if LAST_BATTERY_WARNING is False and battery_warning is True:
        add_event("battery", f"배터리 부족 진입: {battery}%")
        LAST_BATTERY_WARNING = battery_warning

    # 배터리 부족 상태 해제 감지
    elif LAST_BATTERY_WARNING is True and battery_warning is False:
        add_event("battery", f"배터리 경고 해제: {battery}%")
        LAST_BATTERY_WARNING = battery_warning


@app.route("/")
def home():
    """
    메인 화면 렌더링
    """
    return render_template("index.html")


@app.route("/api/activity", methods=["POST"])
def update_activity():
    """
    사용자 입력 감지 API
    - 클릭 / 터치 / 키입력 발생 시 호출
    """

    # 전역 활동 시각 사용 선언
    global LAST_ACTIVITY_AT, LAST_ACTIVITY_LOG_AT

    now = datetime.now()

    # 마지막 활동 시각 갱신
    LAST_ACTIVITY_AT = now

    # 10초에 1번만 로그 기록
    if LAST_ACTIVITY_LOG_AT is None or (now - LAST_ACTIVITY_LOG_AT).total_seconds() > 10:
        add_event("activity", "사용자 입력")
        LAST_ACTIVITY_LOG_AT = now

    return jsonify({"ok": True})


@app.route("/api/status", methods=["GET"])
def status():
    """
    상태 API
    """

    # 현재 날씨 조회
    weather = get_weather(DEVICE_LAT, DEVICE_LON)

    # 현재 공기질 조회
    air_quality = get_air_quality(DEVICE_LAT, DEVICE_LON)

    # 배터리 상태 조회
    battery, charging = get_battery_status()

    # 유휴 시간 계산
    idle_minutes = get_idle_minutes()

    # 상태 계산
    state = calculate_state(battery, charging, idle_minutes)

    # 이벤트 로그 업데이트
    update_event_logs(state, battery, charging)

    # 메시지 생성
    message = build_message(state, battery, idle_minutes, weather, air_quality)

    # 포켓몬 선택
    pokemon = STATE_POKEMON.get(state, STATE_POKEMON["idle"])

    # JSON 응답 반환
    return jsonify({
        "state": state,
        "message": message,
        "battery": battery,
        "charging": charging,
        "idle_minutes": idle_minutes,
        "time": datetime.now().strftime("%H:%M:%S"),
        "pokemon": pokemon,
        "events": EVENT_LOGS,
        "weather": weather,
        "air_quality": air_quality,
        "location": DEVICE_LOCATION,
    })

# 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)