"""version.py -> version.js 동기화. 버전을 올린 뒤 `python sync_version.py` 실행."""
import version
open("version.js", "w", encoding="utf-8").write(
    f'const APP_NAME = "{version.APP_NAME}", APP_VERSION = "{version.__version__}", APP_AUTHOR = "{version.AUTHOR}";\n'
    "document.title = `${APP_NAME} v${APP_VERSION}`;\n"
)
