"""자동 업데이트 (설치판 전용).

GitHub 최신 릴리스에서 PSA_Viewer_Setup.exe와 .sha256을 받아 SHA256이 맞을 때만
설치 프로그램을 조용히(/VERYSILENT) 실행한다. 설치 프로그램이 끝나면 프로그램을 다시 띄운다(installer.iss [Run]).
토큰 없이 읽으므로 저장소가 공개여야 한다.
v0.7.0 이하(exe 한 파일판)는 릴리스의 PSA_Viewer.exe를 받아 자기 자리에 바꿔 넣고 실행하므로,
릴리스에는 같은 설치 프로그램을 PSA_Viewer.exe 이름으로도 올린다(publish.ps1) — 옛 판이 설치판으로 넘어오는 다리.
"""
import hashlib
import json
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path

from version import GITHUB_REPO, __version__

SETUP_NAME = "PSA_Viewer_Setup.exe"
UA = {"User-Agent": f"PSA_Viewer/{__version__}"}


def is_newer(candidate: str, current: str = __version__) -> bool:
    t = lambda v: tuple(int(n) for n in re.findall(r"\d+", v))
    a, b = t(candidate), t(current)
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)) > b + (0,) * (n - len(b))


def _get(url: str, timeout: float = 30) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def check():
    """새 버전이 있으면 (버전, 설치 파일 주소, sha256 주소, 릴리스 설명), 없으면 None. 실패는 예외."""
    rel = json.loads(_get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest", 8))
    ver = rel.get("tag_name", "").lstrip("vV")
    assets = {a["name"]: a["browser_download_url"] for a in rel.get("assets", [])}
    if not is_newer(ver) or SETUP_NAME not in assets or SETUP_NAME + ".sha256" not in assets:
        return None
    return ver, assets[SETUP_NAME], assets[SETUP_NAME + ".sha256"], rel.get("body") or ""


def verified(data: bytes, sha_text: str) -> bool:
    expected = sha_text.split()[0].strip().lower() if sha_text.strip() else ""
    return bool(re.fullmatch(r"[0-9a-f]{64}", expected)) and hashlib.sha256(data).hexdigest() == expected


def install(setup_url: str, sha_url: str) -> None:
    """내려받아 검증한 뒤 설치 프로그램을 조용히 실행한다. 호출한 쪽은 곧바로 프로그램을 끝내야 한다
    (설치 프로그램이 실행 중인 파일을 바꿔야 하므로)."""
    data = _get(setup_url, 300)
    if not verified(data, _get(sha_url).decode("ascii", "replace")):
        raise RuntimeError("내려받은 파일의 SHA256이 맞지 않아 설치하지 않았습니다.")
    setup = Path(tempfile.mkdtemp(prefix="psa_update_")) / SETUP_NAME
    setup.write_bytes(data)
    subprocess.Popen([str(setup), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS"], close_fds=True)


if __name__ == "__main__":  # 자체 점검: python updater.py
    assert is_newer("0.3.0", "0.2.0") and is_newer("v0.2.1", "0.2.0") and is_newer("1.0", "0.9.9")
    assert not is_newer("0.2.0", "0.2.0") and not is_newer("0.1.9", "0.2.0")
    h = hashlib.sha256(b"abc").hexdigest()
    assert verified(b"abc", f"{h}  {SETUP_NAME}\n") and not verified(b"abd", h) and not verified(b"abc", "")
    print("ok")
