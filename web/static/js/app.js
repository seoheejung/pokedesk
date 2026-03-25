// 마지막 활동 전송 시각 저장
let lastActivitySentAt = 0;

// 상태 데이터 조회
async function fetchStatus() {
    const res = await fetch("/api/status");
    const data = await res.json();

    // 콘솔
    document.getElementById("state-icon").innerText = data.profile.icon;
    document.getElementById("state-label").innerText = data.profile.label;
    document.getElementById("console-name").innerText = "ANDROID MONITOR CONSOLE";
    
    // 상태
    document.getElementById("state").innerText = data.state;

    // 상태 메시지
    document.getElementById("message").innerText = data.message;

    // 시간
    document.getElementById("time").innerText = data.time;

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

    return data;
}

// 환경 데이터 조회
async function fetchEnvironment() {
    const res = await fetch("/api/environment");
    const data = await res.json();

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
    document.getElementById("air-quality").innerText =
        data.air_quality.air_text +
        (data.air_quality.us_aqi !== null ? " / AQI " + data.air_quality.us_aqi : "");

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