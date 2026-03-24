// 마지막 활동 전송 시각 저장
let lastActivitySentAt = 0;

// 상태 데이터를 서버에서 가져오는 함수
async function fetchStatus() {
    const res = await fetch("/api/status");
    const data = await res.json();

    // 포켓몬 이미지
    document.getElementById("pokemon-img").src = data.pokemon.sprite;

    // 이름
    document.getElementById("pokemon-name").innerText = data.pokemon.display_name;

    // 상태
    document.getElementById("state").innerText = data.state;

    // 메시지
    document.getElementById("message").innerText = data.message;

    // 시간
    document.getElementById("time").innerText = data.time;

    // 배터리
    document.getElementById("battery").innerText = data.battery + "%";

    // 충전 상태
    document.getElementById("charging").innerText = data.charging ? "충전 중" : "미충전";

    // 유휴 시간
    document.getElementById("idle-minutes").innerText = data.idle_minutes + "분";

    // 위치
    document.getElementById("location").innerText = data.location;

    // 날씨
    document.getElementById("weather").innerText =
        data.weather.weather_text +
        (data.weather.temperature !== null ? " / " + data.weather.temperature + "°C" : "");

    // 공기질
    document.getElementById("air-quality").innerText =
        data.air_quality.air_text +
        (data.air_quality.us_aqi !== null ? " / AQI " + data.air_quality.us_aqi : "");

    // 이벤트 로그
    const logList = document.getElementById("event-log");
    logList.innerHTML = "";

    data.events.forEach(event => {
        const li = document.createElement("li");
        li.innerText = `[${event.time}] ${event.message}`;
        logList.appendChild(li);
    });
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


// 이벤트 감지
document.addEventListener("click", sendActivity);
document.addEventListener("touchstart", sendActivity);
document.addEventListener("keydown", sendActivity);
document.addEventListener("mousemove", sendActivity);

// 5초마다 갱신
setInterval(fetchStatus, 5000);

// 최초 실행
fetchStatus();