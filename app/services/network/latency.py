import platform
import subprocess
import time


def get_latency_ms():
    """
    실행 환경에 맞는 ping 명령으로 latency(ms) 측정
    """
    try:
        system = platform.system()

        if system == "Windows":
            ping_cmd = ["ping", "-n", "1", "8.8.8.8"]
        else:
            ping_cmd = ["ping", "-c", "1", "8.8.8.8"]

        start = time.time()

        result = subprocess.run(
            ping_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if result.returncode != 0:
            return None

        return int((time.time() - start) * 1000)

    except Exception:
        return None