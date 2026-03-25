# Android Monitor Console

> 안드로이드 폰을 활용한 서버 상태 모니터링 콘솔
> 모바일 디바이스를 실시간 운영 패널로 재활용하는 프로젝트

---

## 프로젝트 개요

Android Monitor Console은 안드로이드 디바이스를 운영 패널로 활용하여  
서버 상태를 실시간으로 확인하는 **모바일 전용 모니터링 콘솔**이다.

이 프로젝트는 단순한 웹 대시보드가 아니라   
**항상 켜져 있는 운영 콘솔 형태의 UI**를 목표로 한다.

샤오미 14T를 전용 실행 디바이스로 사용하며   
**Termux** 기반 로컬 서버 + 브라우저 UI 구조로 동작한다.

---

## 목표

- 모바일 디바이스를 운영 패널로 재활용
- 서버 상태를 실시간으로 시각화
- CLI 스타일의 간결한 UI 제공
- 터치 기반 관리 인터페이스 제공
- 로컬 환경에서 독립적으로 실행 가능

---

## 주요 기능

### 1. **디바이스 상태 반영**

- 배터리
- 유휴 시간
- 네트워크 상태 (타입 + 품질 + latency)
- OS 정보

### 2. **외부 환경 반영**

- 날씨 (온도 포함)
- 공기질 (AQI 기반)

---

## 왜 샤오미 14T인가

이 프로젝트에서 Xiaomi 14T는 개발 장비가 아니라 **전용 실행 단말**로 사용된다.

### 역할
- 상시 실행 모니터링 패널
- 터치 기반 관리 인터페이스
- 실시간 상태 표시 화면

> PC에서 개발한 뒤 안드로이드 폰으로 배포하는 구조로 사용한다.

---

## 시스템 구조

```text
[외부 API / 로컬 데이터]
- 날씨 / 공기질
- 디바이스 상태 (배터리 / 네트워크 / 유휴)

        ↓

[Flask Backend]
- 상태 판단 로직
- 환경 데이터 캐싱
- 이벤트 로그 처리

        ↓

[Frontend UI]
- 모바일 최적화 UI
- 상태 표시
- 주기적 데이터 갱신
```

---

## 실행 화면

### Desktop

<img src="images/desktop_1_task.png" width="500">

### Mobile

<div style="display: flex; gap: 12px; flex-wrap: wrap;">
  <img src="images/mobile_1_task.png" width="250">
  <img src="images/mobile_2_task.png" width="250">
</div>

---

## 기술 스택

### Runtime

| 구성 요소   | 설명                 |
| ------- | --------------------- |
| Android | 실행 디바이스 (샤오미 14T)  |
| Termux  | Android 내 Linux 실행 환경 |
| Python  | 백엔드 로직                |
| Flask   | API 서버                |


### Frontend

| 구성 요소      | 설명           |
| ---------- | ------------ |
| HTML       | UI 구조        |
| CSS        | 스타일링         |
| JavaScript | API 호출 및 렌더링 |

### External API

| API | 용도 |
| --- | --- |
| 날씨 API | 현재 날씨 정보 |
| 대기질 API | 미세먼지/공기 상태 |

---

## 상태 시스템

### 기본 상태

| 상태 (key) | 표시값 (UI) | 의미 |
|------------|------------|------|
| idle | SYSTEM IDLE | 기본 대기 상태 |
| sleep | LOW ACTIVITY | 장시간 입력 없음 |
| healing | CHARGING | 충전 중 상태 |
| warning | WARNING | 배터리 또는 환경 경고 상태 |
| focus | FOCUS | 일정 시간 입력 없음 (중간 단계) |
| event | EVENT | 시스템 이벤트 발생 상태 |

### 상태 전환 규칙

| 조건 | 상태 |
|------|------|
| 배터리 ≤ 20% | warning |
| 충전 중 | healing |
| 입력 없음 ≥ 30분 | sleep |
| 입력 없음 ≥ 10분 | focus |
| 시스템 이벤트 발생 | event |
| 그 외 | idle |

---

## 네트워크 상태

### 구성

| 항목      | 설명                                |
| ------- | ------------------------------------ |
| type    | wifi / mobile / ethernet / connected |
| quality | GOOD / NORMAL / SLOW / UNKNOWN       |
| latency | 로컬 환경에서만 ping 기반 ms            |

> Termux 환경에서는 RSSI 기반으로 네트워크 품질을 판단하며 latency 값은 제공되지 않는다.

### 판단 기준

| latency  | 상태      |
| -------- | ------- |
| < 50ms   | GOOD    |
| 50~150ms | NORMAL  |
| >150ms   | SLOW    |
| 측정 실패    | UNKNOWN |


---

## 디렉토리 구조

```
android-monitor-console/
├── app/
│   ├── core/
│   ├── constants/
│   ├── services/
│   └── main.py
├── web/
│   ├── static/
│   └── templates/
│       └── index.html
├── requirements.txt
├── requirements-termux.txt
├── termux_setup.sh
├── termux_start.sh
└── README.md
```

---

## 실행 방법

### [1단계] Windows에서 Flask 서버 실행 확인

#### 1. 가상환경 설정

```bash
# 생성
python -m venv venv

# 활성화
venv\Scripts\activate

# 비활성화
deactivate
```

#### 2. 패키지 설치

```bash
pip install -r requirements.txt

# 설치 확인
pip list
```

#### 3. 서버 실행 및 접속 확인

```
python -m app.main

# http://127.0.0.1:8000
```
`app.main` 내부에서 Flask 앱을 직접 실행하므로 `python -m app.main` 방식으로 기동


### [2단계] Termux 배포 및 실행

#### 1. Termux 설치 (중요)

> ⚠️ 반드시 F-Droid 버전 사용 (Play Store 버전은 지원되지 않음)

- Termux (F-Droid)
- Termux:API (F-Droid)

#### 2. Termux 기본 설정
```bash
pkg update && pkg upgrade -y
pkg install python git termux-api -y
termux-setup-storage
```

#### 3. Termux API 확인
```bash
which termux-battery-status
which termux-wifi-connectioninfo
```
> 명령이 나오지 않으면 Termux:API 앱 또는 설치 상태 확인 필요

#### 4. 프로젝트 복사
```bash
git clone https://github.com/seoheejung/android-monitor-console.git ~/android-monitor-console
cd ~/android-monitor-console
```

#### 5. 실행
```bash
# 권한 부여
chmod +x termux_setup.sh
chmod +x termux_start.sh

# 의존성 설치
./termux_setup.sh

# 서버 실행
./termux_start.sh
```

#### 6. 브라우저 접속 (모바일 패널 사용)

- 브라우저 접속 (http://127.0.0.1:8000)
- 전체화면 모드
- 충전 상태 유지
- 화면 꺼짐 시간은 Android 설정에서 별도 조정

#### 7. 종료 방법

```bash
# Termux 실행 화면
Ctrl+ C
```

---

### [3단계] Termux 재실행 절차

#### 1. Termux를 다시 열었을 때
```
cd ~/android-monitor-console
./termux_start.sh
```

#### 2. 브라우저 다시 접속
```
http://127.0.0.1:8000
```

---

### ⚠️ 환경별 의존성 파일
| 파일                        | 용도               |
| ------------------------- | ---------------- |
| `requirements.txt`        | Windows / 로컬 개발용 |
| `requirements-termux.txt` | Termux 실행용       |


### ⚠️ 환경별 배터리 처리 방식
| 환경              | 방식                    |
| --------------- | --------------------- |
| Windows / Linux | psutil                |
| Termux          | termux-battery-status |

> psutil은 Termux에서 사용 불가

### ⚠️ 주요 주의사항
| 항목            | 내용                           |
| ------------- | ---------------------------- |
| 실행 위치         | 반드시 프로젝트 루트에서 실행             |
| 포트            | 기본 8000 사용                   |
| Termux 배터리 조회 | `termux-api` 필요              |
| 로컬 개발         | `requirements.txt` 사용        |
| Termux 실행     | `requirements-termux.txt` 사용 |
| 네트워크 접속       | PC에서 폰에 접근할 경우 동일 Wi-Fi 필요   |

### ⚠️ 데이터 갱신 주기

| API              | 주기  | 내용            |
| ---------------- | --- | ------------- |
| /api/status      | 5초  | 상태, 배터리, 유휴   |
| /api/environment | 30초 | 날씨, 공기질, 네트워크 |

---

## 실행 흐름

1. 앱 실행
2. 디바이스 상태 수집
3. 외부 API 데이터 조회
4. 상태 해석 엔진이 현재 상태 계산
5. UI에서 주기적 갱신
6. 사용자 입력 처리

---

## 개발 원칙

- 모바일 전용 UI 기준 설계
- 최소한의 정보로 상태 전달
- 실시간성 유지
- 중복 제거
- 운영 도구 기준 설계


---

## 라이선스

MIT
