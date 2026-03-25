// 마지막 활동 전송 시각 저장
let lastActivitySentAt = 0;

const typeMap = {
    wifi: "Wi-Fi",
    mobile: "Mobile",
    ethernet: "Ethernet",
    connected: "Connected",
    offline: "Offline",
    unknown: "Unknown"
};

// 상태 데이터 조회
async function fetchStatus() {
    const res = await fetch("/api/status");
    const data = await res.json();

    // 상태 아이콘
    const iconEl = document.getElementById("state-icon");
    iconEl.innerText = data.profile.icon;
    iconEl.className = "state-icon";
    iconEl.classList.add(data.state);

    // 상태 라벨
    document.getElementById("state-label").innerText = data.profile.label;

    // 시스템 정보
    document.getElementById("os-info").innerText = data.os;

    // 상태 텍스트
    const stateEl = document.getElementById("state");

    if (stateEl) {
        // 텍스트 결합 업데이트: LABEL ( MESSAGE ) 형식
        stateEl.innerText = `${data.profile.label} · ${data.message}`;

        // 기존 상태 클래스 제거 (배열 활용)
        const stateClasses = [
            "state-idle", "state-sleep", "state-focus", 
            "state-warning", "state-healing", "state-event"
        ];
        stateEl.classList.remove(...stateClasses);

        // 새로운 상태 클래스 추가
        stateEl.classList.add(`state-${data.state}`);
    }

    // 배터리
    document.getElementById("battery").innerText = data.battery + "%";

    // 충전 상태
    document.getElementById("charging").innerText = data.charging ? "충전 중" : "미충전";

    // 유휴 시간
    document.getElementById("idle-minutes").innerText = data.idle_minutes + "분";

    // 이벤트 로그
    const logList = document.getElementById("event-log");
    logList.innerHTML = "";

    data.events.forEach(event => {
        const li = document.createElement("li");
        li.innerText = `[${event.time}] ${event.message}`;
        logList.appendChild(li);
    });

    // 로그 자동 하단 스크롤
    logList.scrollTop = logList.scrollHeight;

    return data;
}

// 환경 및 네트워크 데이터 조회
async function fetchEnvironment() {
    const res = await fetch("/api/environment");
    const data = await res.json();

    // 네트워크 상태
    const net = data.network;

    if (net.type === "offline") {
        document.getElementById("network").innerText = "OFFLINE";
    } else if (net.latency === null) {
        document.getElementById("network").innerText =
            `${typeMap[net.type] || net.type} · ${net.quality}`;
    } else {
        document.getElementById("network").innerText =
            `${typeMap[net.type] || net.type} · ${net.quality} (${net.latency}ms)`;
    }

    // 위치
    document.getElementById("location").innerText = data.location;

    // 환경 메시지
    const environmentMessageEl = document.getElementById("environment-message");
    if (environmentMessageEl) {
        environmentMessageEl.innerText = data.message;
    }

    // 날씨
    document.getElementById("weather").innerText =
        data.weather.weather_text +
        (data.weather.temperature !== null ? " / " + data.weather.temperature + "°C" : "");

    // 공기질
    const airEl = document.getElementById("air-quality");
    airEl.innerText =
        data.air_quality.air_text +
        (data.air_quality.us_aqi !== null ? " / AQI " + data.air_quality.us_aqi : "");

    // AQI 강조 클래스 초기화 후 재적용
    airEl.classList.remove("aqi-bad");

    if (data.air_quality.us_aqi !== null && data.air_quality.us_aqi >= 100) {
        airEl.classList.add("aqi-bad");
    }

    return data;
}

// 사용자 활동 전송
async function sendActivity() {
    const now = Date.now();

    if (now - lastActivitySentAt < 3000) return;

    lastActivitySentAt = now;

    await fetch("/api/activity", {
        method: "POST"
    });
}

// 최초 로딩
async function initDashboard() {
    try {
        await fetchStatus();
        await fetchEnvironment();
    } catch (error) {
        console.error("초기 로딩 실패:", error);
    }
}

// 이벤트 감지
document.addEventListener("click", sendActivity);
document.addEventListener("touchstart", sendActivity);
document.addEventListener("keydown", sendActivity);
document.addEventListener("mousemove", sendActivity);

// 최초 실행
initDashboard();

// 빠른 상태는 5초마다
setInterval(fetchStatus, 5000);

// 느린 환경 정보는 30초마다
setInterval(fetchEnvironment, 30000);