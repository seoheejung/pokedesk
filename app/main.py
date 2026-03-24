from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from datetime import datetime
from app.services.battery import get_battery_status

app = FastAPI()
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

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

# 최근 이벤트 로그를 메모리에 저장
EVENT_LOGS = []

# 마지막 상태를 저장
LAST_STATE = None

# 마지막 충전 상태를 저장
LAST_CHARGING = None

# 마지막 배터리 경고 상태를 저장
LAST_BATTERY_WARNING = None

# 마지막 사용자 활동 시각 저장
LAST_ACTIVITY_AT = datetime.now()

# 마지막 activity 기록 시간 추가
LAST_ACTIVITY_LOG_AT = None


def add_event(event_type: str, message: str) -> None:
    """
    이벤트 로그 추가
    - 가장 최근 로그가 위로 오도록 앞에 삽입
    - 최대 10개만 유지
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

    # 현재 시각
    now = datetime.now()

    # 마지막 활동 이후 지난 시간 계산
    delta = now - LAST_ACTIVITY_AT

    # 초 단위를 분으로 변환
    idle_minutes = int(delta.total_seconds() // 60)

    # 유휴 시간 반환
    return idle_minutes


def calculate_state(battery: int, charging: bool, idle_minutes: int) -> str:
    """
    현재 상태 계산
    우선순위:
    1. 충전 중이면 healing
    2. 배터리 20 이하이면 warning
    3. 유휴 시간 30분 이상이면 sleep
    4. 유휴 시간 10분 이상이면 focus
    5. 그 외 idle
    """

    # 배터리가 낮으면 경고 상태
    if battery <= 20:
        return "warning"
    
    # 충전 중이면 회복 상태
    if charging:
        return "healing"

    # 오래 입력이 없으면 수면 상태
    if idle_minutes >= 30:
        return "sleep"

    # 일정 시간 조용하면 집중 상태
    if idle_minutes >= 10:
        return "focus"

    # 그 외는 기본 대기 상태
    return "idle"


def build_message(state: str, battery: int, charging: bool, idle_minutes: int) -> str:
    """
    상태별 말풍선 메시지 생성
    """

    # 회복 상태 메시지
    if state == "healing":
        return "충전 중이야. 회복 상태로 전환할게."

    # 경고 상태 메시지
    if state == "warning":
        return f"배터리가 {battery}%야. 경고 상태야."

    # 수면 상태 메시지
    if state == "sleep":
        return f"{idle_minutes}분 동안 입력이 없어. 잠든 상태로 전환할게."

    # 집중 상태 메시지
    if state == "focus":
        return "조용한 상태가 유지되고 있어. 집중 상태야."

    # 이벤트 상태 메시지
    if state == "event":
        return "새로운 이벤트가 있어. 브리핑을 확인해."

    # 기본 메시지
    return "현재는 대기 상태야."


def update_event_logs(state: str, battery: int, charging: bool, idle_minutes: int) -> None:
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


@app.get("/")
def home(request: Request):
    """
    메인 화면 렌더링
    - index.html 반환
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/api/activity")
def update_activity():
    """
    사용자 활동 시각 갱신
    - 클릭 / 터치 / 키입력 발생 시 호출
    """

    # 전역 활동 시각 사용 선언
    global LAST_ACTIVITY_AT

    # 마지막 활동 시각 갱신
    LAST_ACTIVITY_AT = datetime.now()

    # 10초에 1번만 기록
    global LAST_ACTIVITY_LOG_AT

    now = datetime.now()

    if LAST_ACTIVITY_LOG_AT is None or (now - LAST_ACTIVITY_LOG_AT).seconds > 10:
        add_event("activity", "사용자 입력 감지")
        LAST_ACTIVITY_LOG_AT = now

    # 활동 로그 반환
    return JSONResponse(content={
        "ok": True,
        "message": "activity updated"
    })


@app.get("/api/status")
def get_status():
    """
    상태 API
    - 배터리/충전 상태는 실제 값 사용
    - 유휴 시간은 마지막 활동 시각 기준 계산
    - 이벤트 로그는 메모리 기반 누적 관리
    """

    # 실제 배터리/충전 상태 조회
    battery, charging = get_battery_status()

    # 마지막 활동 시각 기준 유휴 시간 계산
    idle_minutes = get_idle_minutes()

    # 현재 시간 문자열 생성
    current_time = datetime.now().strftime("%H:%M:%S")

    # 현재 상태 계산
    state = calculate_state(
        battery=battery,
        charging=charging,
        idle_minutes=idle_minutes
    )

    # 이벤트 로그 갱신
    update_event_logs(
        state=state,
        battery=battery,
        charging=charging,
        idle_minutes=idle_minutes
    )

    # 상태별 메시지 생성
    message = build_message(
        state=state,
        battery=battery,
        charging=charging,
        idle_minutes=idle_minutes
    )

    # 상태별 포켓몬 선택
    pokemon = STATE_POKEMON.get(state, STATE_POKEMON["idle"])

    # 최종 응답 데이터
    data = {
        "state": state,                 # 현재 상태
        "message": message,             # 말풍선 메시지
        "battery": battery,             # 배터리 %
        "charging": charging,           # 충전 여부
        "idle_minutes": idle_minutes,   # 유휴 시간
        "time": current_time,           # 현재 시간
        "pokemon": pokemon,             # 포켓몬 정보
        "events": EVENT_LOGS            # 누적 이벤트 로그
    }

    # JSON 반환
    return JSONResponse(content=data)