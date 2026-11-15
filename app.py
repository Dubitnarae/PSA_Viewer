"""PSA 입도 뷰어 - index.html을 데스크톱 창(WebView2)으로 띄운다.

한 번에 하나만 실행한다: 두 프로그램이 같은 데이터 목록을 따로 저장하면 한쪽 기록이 사라지기 때문.
이미 떠 있으면 연 파일(더블클릭한 .ngb·.mea)을 그 창으로 넘기고 바로 끝난다.
"""
import json
import os
import socket
import sys
import threading
from pathlib import Path

import webview

import updater
from storage import Api
from version import APP_NAME, __version__

ACK = b"PSA_VIEWER_OK"
PORT_FILE = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "PSA_Viewer" / "instance.port"


def forward(paths) -> bool:
    """이미 떠 있는 창이 있으면 파일 경로를 넘기고 True. 없으면(포트 파일이 옛것이어도) False."""
    try:
        port = int(PORT_FILE.read_text())
        with socket.create_connection(("127.0.0.1", port), timeout=2) as s:
            s.sendall(json.dumps(paths).encode("utf-8"))
            s.shutdown(socket.SHUT_WR)
            return s.recv(16) == ACK  # 다른 프로그램이 그 포트를 쓰고 있으면 응답이 다름
    except (OSError, ValueError):
        return False


def serve(api, win) -> None:
    """두 번째 실행이 보낸 경로를 받아 화면에 연다 (이 PC 안에서만, 127.0.0.1)."""
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen()
    PORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    PORT_FILE.write_text(str(srv.getsockname()[1]))

    def loop():
        while True:
            conn, _ = srv.accept()
            try:
                with conn:
                    conn.settimeout(5)  # 멈춘 연결 하나 때문에 다음 요청을 못 받는 일 막기
                    data = b""
                    while chunk := conn.recv(65536):
                        data += chunk
                    conn.sendall(ACK)
                paths = json.loads(data.decode("utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(paths, list):
                api._add_paths(p for p in paths if isinstance(p, str))
            win.restore()
            win.evaluate_js("openStartup()")

    threading.Thread(target=loop, daemon=True).start()


def check_update(window):
    """시작할 때 새 버전을 확인하고, 사용자가 동의하면 설치 프로그램을 실행한 뒤 끝난다. 실패해도 조용히 넘어간다."""
    if not getattr(sys, "frozen", False):
        return  # 개발 환경(python app.py)에서는 확인하지 않음
    try:
        found = updater.check()
    except Exception:
        return  # 오프라인·비공개 저장소 등
    if not found:
        return
    ver, setup_url, sha_url, notes = found
    msg = f"새 버전 v{ver}이 있습니다 (지금 v{__version__}).\n\n{notes[:600]}\n\n지금 업데이트할까요? 설치가 끝나면 다시 열려요."
    if not window.create_confirmation_dialog("업데이트", msg):
        return
    try:
        updater.install(setup_url, sha_url)
    except Exception as e:
        window.create_confirmation_dialog("업데이트 실패", f"업데이트하지 못했습니다. 지금 버전을 계속 씁니다.\n\n{e}")
        return
    window.destroy()


if __name__ == "__main__":
    args = [str(Path(a).resolve()) for a in sys.argv[1:]]
    if forward(args):
        sys.exit(0)
    # PyInstaller 실행 시 리소스는 sys._MEIPASS 아래에 있다
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    api = Api()
    api._add_paths(args)
    win = webview.create_window(f"{APP_NAME} v{__version__}", str(base / "index.html"),
                                width=1400, height=950, js_api=api)
    api._window = win
    serve(api, win)
    webview.start(check_update, win)
