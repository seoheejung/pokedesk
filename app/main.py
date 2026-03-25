from flask import Flask, render_template, jsonify
from datetime import datetime
from app.services.battery.battery import get_battery_status
from app.services.location_termux import get_location_termux
from app.services.geocoding import get_address
from threading import Thread

import platform
import app.core.state_store as store
from app.services.environment import get_cached_env
from app.services.state_logic import build_state_message
from app.services.event_log import get_idle_minutes, update_event_logs
from app.constants.state_profile import STATE_PROFILE
from app.services.network.network import get_network_detail

app = Flask(
    __name__,
    template_folder="../web/templates",
    static_folder="../web/static"
)

def init_location():
    """
    디바이스 위치 초기화 및 캐시 무효화

    역할:
    - Termux를 통해 현재 위치(lat, lon)를 1회 조회
    - 성공 시 전역 위치 정보 갱신
    - 위치가 변경되었으므로 날씨/공기질 캐시 초기화

    주의:
    - 외부 호출(get_location_termux, get_address)이 포함되므로
      매 요청마다 호출하면 성능 저하 발생
    - 최초 1회 또는 필요 시에만 호출해야 함
    """

    # 현재 위치 조회 (Termux API 호출)
    lat, lon = get_location_termux()

    # 위치 조회 성공 시에만 반영
    if lat is not None and lon is not None:
        # 전역 좌표 갱신
        store.DEVICE_LAT = lat
        store.DEVICE_LON = lon
        
        # 좌표 → 주소 변환 (외부 API)
        store.DEVICE_LOCATION = get_address(lat, lon)

        # 위치가 바뀌었으므로 환경 데이터 캐시 무효화
        store.CACHE["weather"] = None
        store.CACHE["air"] = None
        store.CACHE["updated_at"] = None
    else:
        # 위치 조회 실패 시 기존 좌표(기본 좌표 포함) 기준 주소 설정
        store.DEVICE_LOCATION = get_address(store.DEVICE_LAT, store.DEVICE_LON)

def warm_up_location():
    """
    서버 시작 후 백그라운드에서 위치 1회 초기화
    - 첫 /api/status 응답을 막지 않기 위해 별도 스레드에서 실행
    """
    try:
        init_location()
        get_cached_env()
    except Exception as e:
        print("[warm_up_location] 실패:", e)

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
    - 클릭 / 터치 / 키입력 발생 시 마지막 활동 시각만 갱신
    """
    store.LAST_ACTIVITY_AT = datetime.now()
    return jsonify({"ok": True})


@app.route("/api/status", methods=["GET"])
def status():
    """
    빠른 상태 API
    - 배터리 / 유휴 시간 / 상태 / 이벤트만 반환
    """
    # 배터리 상태 조회
    battery, charging = get_battery_status()

    # 유휴 시간 계산
    idle_minutes = get_idle_minutes()

    # 상태 + 상태 메시지 생성
    state, state_message = build_state_message(battery, charging, idle_minutes)

    # 이벤트 로그 업데이트
    update_event_logs(state, battery, charging)

    # profile 선택
    profile = STATE_PROFILE.get(state, STATE_PROFILE["idle"])

    # JSON 응답 반환
    return jsonify({
        "state": state,
        "message": state_message,
        "battery": battery,
        "charging": charging,
        "idle_minutes": idle_minutes,
        "profile": profile,
        "events": store.EVENT_LOGS,
        "os": f"{platform.system()} ({platform.release()})",
    })

@app.route("/api/environment", methods=["GET"])
def environment():
    """
    느린 환경 정보 API
    - 날씨 / 공기질 / 위치 / 네트워크 반환
    """
    if store.DEVICE_LOCATION == "위치 확인 중":
        try:
            init_location()
        except Exception as e:
            print("[environment] init_location 실패:", e)

    weather, air_quality = get_cached_env()

    network = get_network_detail()

    return jsonify({
        "weather": weather,
        "air_quality": air_quality,
        "location": store.DEVICE_LOCATION,
        "network": network,
    })

# 서버 실행
if __name__ == "__main__":
    Thread(target=warm_up_location, daemon=True).start()
    app.run(host="0.0.0.0", port=8000)