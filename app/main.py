from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from datetime import datetime
import psutil

app = FastAPI()
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 상태별 포켓몬 매핑
# - 값은 PokeAPI 포켓몬 ID
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


def get_battery_status() -> tuple[int, bool]:
    """
    현재 배터리 상태 조회
    반환:
    - battery: 배터리 퍼센트
    - charging: 충전 여부

    예외 처리:
    - 데스크탑 등 배터리 정보가 없으면 기본값 반환
    """

    # psutil에서 배터리 정보 조회
    battery_info = psutil.sensors_battery()

    # 배터리 정보가 없으면 기본값 반환
    if battery_info is None:
        return 100, False

    # 배터리 퍼센트 정수 변환
    battery = int(battery_info.percent)

    # 충전 여부
    charging = bool(battery_info.power_plugged)

    # 배터리 상태 반환
    return battery, charging


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

    # 충전 중이면 회복 상태
    if charging:
        return "healing"

    # 배터리가 낮으면 경고 상태
    if battery <= 20:
        return "warning"

    # 오래 입력이 없으면 수면 상태
    if idle_minutes >= 30:
        return "sleep"

    # 짧은 유휴는 집중 상태로 가정
    if idle_minutes >= 10:
        return "focus"

    # 나머지는 기본 대기 상태
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


def build_events(state: str, battery: int, charging: bool, idle_minutes: int) -> list[dict]:
    """
    현재 상태 기준의 이벤트 로그 생성
    - 지금은 샘플 로그 형태
    - 다음 단계에서 메모리 저장 방식으로 변경
    """

    # 최근 이벤트 로그 리스트
    events = []

    # 상태 진입 로그 추가
    events.append({
        "type": "state",
        "message": f"{state} 상태 진입"
    })

    # 충전 상태 로그 추가
    if charging:
        events.append({
            "type": "power",
            "message": "충전 중"
        })
    else:
        events.append({
            "type": "power",
            "message": "충전 해제 상태"
        })

    # 배터리 경고 로그 추가
    if battery <= 20:
        events.append({
            "type": "battery",
            "message": f"배터리 부족: {battery}%"
        })

    # 유휴 시간 로그 추가
    events.append({
        "type": "idle",
        "message": f"유휴 시간: {idle_minutes}분"
    })

    # 최대 5개만 반환
    return events[:5]


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


@app.get("/api/status")
def get_status():
    """
    상태 API
    - 배터리/충전 상태는 실제 값 사용
    - 유휴 시간은 아직 샘플 값 유지
    """

    # 실제 배터리/충전 상태 조회
    battery, charging = get_battery_status()

    # 유휴 시간은 아직 샘플 값 사용
    idle_minutes = 12

    # 현재 시간 문자열 생성
    current_time = datetime.now().strftime("%H:%M")

    # 상태 계산
    state = calculate_state(
        battery=battery,
        charging=charging,
        idle_minutes=idle_minutes
    )

    # 상태별 포켓몬 선택
    pokemon = STATE_POKEMON[state]

    # 상태별 메시지 생성
    message = build_message(
        state=state,
        battery=battery,
        charging=charging,
        idle_minutes=idle_minutes
    )

    # 이벤트 로그 생성
    events = build_events(
        state=state,
        battery=battery,
        charging=charging,
        idle_minutes=idle_minutes
    )

    # 최종 응답 데이터
    data = {
        "state": state,                 # 현재 상태
        "message": message,             # 말풍선 메시지
        "battery": battery,             # 배터리 %
        "charging": charging,           # 충전 여부
        "idle_minutes": idle_minutes,   # 유휴 시간
        "time": current_time,           # 현재 시간
        "pokemon": pokemon,             # 포켓몬 정보
        "events": events                # 이벤트 로그
    }

    # JSON 반환
    return JSONResponse(content=data)