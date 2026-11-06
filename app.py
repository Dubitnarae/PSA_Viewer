"""PSA 입도 뷰어 - index.html을 데스크톱 창(WebView2)으로 띄운다."""
import sys
from pathlib import Path

import webview

from version import APP_NAME, __version__

# PyInstaller 실행 시 리소스는 sys._MEIPASS 아래에 풀린다
base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
webview.create_window(f"{APP_NAME} v{__version__}", str(base / "index.html"),
                      width=1400, height=950)
webview.start()
