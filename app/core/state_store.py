from datetime import datetime

DEFAULT_LAT = 37.5665
DEFAULT_LON = 126.9780

DEVICE_LAT = DEFAULT_LAT
DEVICE_LON = DEFAULT_LON
DEVICE_LOCATION = "위치 확인 중"

CACHE = {
    "weather": None,
    "air": None,
    "updated_at": None
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
