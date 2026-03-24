// 상태 데이터를 서버에서 가져오는 함수
async function fetchStatus() {
    // API 호출
    const res = await fetch("/api/status");

    // JSON 변환
    const data = await res.json();

    // 포켓몬 이미지 업데이트
    document.getElementById("pokemon-img").src = data.pokemon.sprite;

    // 포켓몬 이름 표시
    document.getElementById("pokemon-name").innerText = data.pokemon.display_name;

    // 현재 상태 표시
    document.getElementById("state").innerText = "STATE: " + data.state;

    // 말풍선 메시지 표시
    document.getElementById("message").innerText = data.message;

    // 현재 시간 표시
    document.getElementById("time").innerText = "TIME: " + data.time;

    // 배터리 표시
    document.getElementById("battery").innerText = "BATTERY: " + data.battery + "%";

    // 충전 상태 표시
    document.getElementById("charging").innerText = "CHARGING: " + (data.charging ? "ON" : "OFF");

    // 유휴 시간 표시
    document.getElementById("idle-minutes").innerText = "IDLE: " + data.idle_minutes + " min";

    // 이벤트 로그 DOM 선택
    const logList = document.getElementById("event-log");

    // 기존 로그 초기화
    logList.innerHTML = "";

    // 이벤트 로그 반복 렌더링
    data.events.forEach(event => {
        // li 요소 생성
        const li = document.createElement("li");

        // 로그 문구 입력
        li.innerText = "[" + event.time + "] [" + event.type + "] " + event.message;

        // 리스트에 추가
        logList.appendChild(li);
    });
}

// 5초마다 상태 갱신
setInterval(fetchStatus, 5000);

// 최초 1회 실행
fetchStatus();