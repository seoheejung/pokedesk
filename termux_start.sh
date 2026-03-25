#!/data/data/com.termux/files/usr/bin/bash

# 에러 발생 시 즉시 종료
set -e

echo "[1] 프로젝트 폴더 이동"
cd "$HOME/android-monitor-console"

echo "[2] 가상환경 확인"
if [ ! -d "venv" ]; then
    echo "venv가 없습니다."
    echo "./termux_setup.sh 먼저 실행하세요."
    exit 1
fi

echo "[3] 가상환경 활성화"
source venv/bin/activate

echo "[4] PYTHONPATH 설정"
export PYTHONPATH="$HOME/android-monitor-console"

echo "[5] 서버 실행"
echo "접속: http://127.0.0.1:8000"
echo "종료: Ctrl + C"

python -m app.main