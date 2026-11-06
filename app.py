"""PSA 입도 뷰어 - index.html을 데스크톱 창(WebView2)으로 띄운다."""
import sys
from pathlib import Path

import webview

import updater
from storage import Api
from version import APP_NAME, __version__


def check_update(window):
    """시작할 때 새 버전을 확인하고, 사용자가 동의하면 설치 후 다시 실행한다. 실패해도 조용히 넘어간다."""
    updater.cleanup()
    if not getattr(sys, "frozen", False):
        return  # 개발 환경(python app.py)에서는 확인하지 않음
    try:
        found = updater.check()
    except Exception:
        return  # 오프라인·비공개 저장소 등
    if not found:
        return
    ver, exe_url, sha_url, notes = found
    msg = f"새 버전 v{ver}이 있습니다 (지금 v{__version__}).\n\n{notes[:600]}\n\n지금 업데이트하고 다시 시작할까요?"
    if not window.create_confirmation_dialog("업데이트", msg):
        return
    try:
        updater.install(exe_url, sha_url)
    except Exception as e:
        window.create_confirmation_dialog("업데이트 실패", f"업데이트하지 못했습니다. 지금 버전을 계속 씁니다.\n\n{e}")
        return
    window.destroy()


# PyInstaller 실행 시 리소스는 sys._MEIPASS 아래에 풀린다
base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
api = Api()
win = webview.create_window(f"{APP_NAME} v{__version__}", str(base / "index.html"),
                            width=1400, height=950, js_api=api)
api._window = win
webview.start(check_update, win)
