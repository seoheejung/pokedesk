#!/data/data/com.termux/files/usr/bin/bash

# 에러 발생 시 즉시 종료
set -e

echo "[1] 패키지 업데이트"
pkg update -y
pkg upgrade -y

echo "[2] Python / Git / Termux API 설치"
pkg install python git termux-api -y

echo "[3] 저장소 권한 연결"
termux-setup-storage

echo "[4] 프로젝트 경로 확인"
PROJECT_DIR="$HOME/android-monitor-console"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "프로젝트 폴더가 없습니다: $PROJECT_DIR"
    echo "git clone 또는 파일 복사 후 다시 실행하세요."
    exit 1
fi

echo "[5] 프로젝트 폴더 이동"
cd "$PROJECT_DIR"

echo "[6] 가상환경 생성"
if [ ! -d "venv" ]; then
    python -m venv venv
fi

echo "[7] 가상환경 활성화"
source venv/bin/activate

echo "[8] pip 업그레이드"
pip install --upgrade pip

echo "[9] Termux 의존성 설치"
pip install -r requirements-termux.txt

echo "[완료] Termux 초기 설정 완료"
echo "다음 실행: ./termux_start.sh"