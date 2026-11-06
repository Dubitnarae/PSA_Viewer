"""저장 기능 (exe 창에서 화면 JS가 window.pywebview.api.* 로 부른다).

저장 폴더(기본: 프로그램 폴더\\PSA_Data, 위치는 psa_viewer_settings.json에 기록)
- originals\\<sha256>.<확장자> : 측정 원본 사본. 같은 파일은 한 번만 저장된다.
- library.json               : 데이터 목록(결과값·누적분포·로트·메모). 덮어쓰기 전 library.json.bak 보관.
- calib.json                 : 혼합 예측 보정 기록(묶음별 실측−예측 누적 차이). 덮어쓰기 전 calib.json.bak 보관.
- projects\\*.psa            : 작업 저장 파일(열어 둔 파일 목록·수율 기준, JSON).
측정 데이터이므로 이 폴더는 절대 커밋하지 않는다(.gitignore).
"""
import base64
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
SETTINGS = APP_DIR / "psa_viewer_settings.json"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
DOCS = {"library": "library.json", "calib": "calib.json"}  # JS가 고를 수 있는 목록 파일 (그 밖의 이름은 KeyError)


def _atomic_write(path: Path, data: bytes) -> None:
    """임시 파일에 다 쓴 뒤 바꿔치기 — 쓰는 도중 꺼져도 기존 파일이 깨지지 않는다."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


class Api:
    def __init__(self, base: Path | None = None):
        self._base = base  # 테스트용: 설정 파일 대신 이 폴더를 쓴다
        self._window = None  # _로 시작해야 pywebview가 JS로 노출하지 않음

    def _dir(self) -> Path:
        d = self._base
        if d is None:
            try:
                d = Path(json.loads(SETTINGS.read_text(encoding="utf-8"))["data_dir"])
            except (OSError, ValueError, KeyError, TypeError):
                d = APP_DIR / "PSA_Data"
        (d / "originals").mkdir(parents=True, exist_ok=True)
        (d / "projects").mkdir(exist_ok=True)
        return d

    def _dialog(self, kind, **kw):
        import webview

        r = self._window.create_file_dialog(getattr(webview.FileDialog, kind), **kw)
        if not r:
            return None
        return Path(r if isinstance(r, str) else r[0])

    # ---------- 정보 ----------
    def info(self):
        return {"data_dir": str(self._dir())}

    # ---------- 원본 ----------
    def save_original(self, name: str, b64: str) -> str:
        data = base64.b64decode(b64)
        sha = hashlib.sha256(data).hexdigest()
        ext = Path(name).suffix.lower() if Path(name).suffix.lower() in (".ngb", ".mea") else ".bin"
        orig = self._dir() / "originals"
        if not list(orig.glob(sha + ".*")):
            _atomic_write(orig / (sha + ext), data)
        return sha

    def read_original(self, sha: str):
        if not SHA_RE.match(sha or ""):
            return None
        hits = list((self._dir() / "originals").glob(sha + ".*"))
        return base64.b64encode(hits[0].read_bytes()).decode("ascii") if hits else None

    def delete_originals(self, shas: list) -> int:
        n = 0
        for sha in shas:
            if SHA_RE.match(sha or ""):
                for p in (self._dir() / "originals").glob(sha + ".*"):
                    p.unlink(missing_ok=True)
                    n += 1
        return n

    # ---------- 데이터 목록 ----------
    def lib_load(self, doc: str = "library") -> str:
        p = self._dir() / DOCS[doc]
        return p.read_text(encoding="utf-8") if p.exists() else "[]"

    def lib_save(self, text: str, doc: str = "library") -> bool:
        p = self._dir() / DOCS[doc]
        if not isinstance(json.loads(text), list):  # 깨진 데이터로 덮어쓰지 않기
            raise ValueError("데이터 목록 형식이 잘못되었습니다.")
        if p.exists():
            shutil.copy2(p, p.with_name(p.name + ".bak"))
        _atomic_write(p, text.encode("utf-8"))
        return True

    # ---------- 작업 저장 ----------
    def project_save(self, text: str, name: str = "작업.psa"):
        json.loads(text)
        p = self._dialog("SAVE", directory=str(self._dir() / "projects"), save_filename=name,
                         file_types=("PSA 작업 파일 (*.psa)",))
        if not p:
            return None
        if p.suffix.lower() != ".psa":
            p = p.with_name(p.name + ".psa")
        _atomic_write(p, text.encode("utf-8"))
        return p.name

    def project_open(self):
        p = self._dialog("OPEN", directory=str(self._dir() / "projects"), file_types=("PSA 작업 파일 (*.psa)",))
        return p.read_text(encoding="utf-8") if p else None

    # ---------- 내보내기·폴더 ----------
    def save_text(self, name: str, text: str):
        p = self._dialog("SAVE", directory=str(Path.home() / "Documents"), save_filename=name,
                         file_types=("CSV (*.csv)",))
        if not p:
            return None
        p.write_text(text, encoding="utf-8-sig", newline="")  # BOM: 엑셀이 한글을 바로 읽음. newline="": JS가 넣은 CRLF를 그대로(안 하면 빈 줄이 생김)
        return p.name

    def open_folder(self):
        os.startfile(self._dir())  # Windows 전용

    def change_dir(self):
        """저장 위치를 바꾼다. 옛 폴더의 내용은 새 폴더로 복사한다(옛 폴더는 그대로 둔다)."""
        p = self._dialog("FOLDER", directory=str(self._dir()))
        if not p:
            return None
        old, new = self._dir(), p / "PSA_Data"
        if new.resolve() != old.resolve():
            shutil.copytree(old, new, dirs_exist_ok=True)
            SETTINGS.write_text(json.dumps({"data_dir": str(new)}, ensure_ascii=False), encoding="utf-8")
        return str(new)


if __name__ == "__main__":  # 자체 점검: python storage.py
    import tempfile

    with tempfile.TemporaryDirectory() as t:
        api = Api(Path(t))
        raw = b"\xd0\xcf\x11\xe0 test"
        sha = api.save_original("a (iron).NGB", base64.b64encode(raw).decode())
        assert sha == api.save_original("other.ngb", base64.b64encode(raw).decode())  # 중복은 한 번만
        assert len(list((Path(t) / "originals").iterdir())) == 1
        assert base64.b64decode(api.read_original(sha)) == raw
        assert api.read_original("../library") is None
        assert api.lib_load() == "[]"
        api.lib_save('[{"key": 1}]'); api.lib_save('[{"key": 2}]')
        assert json.loads(api.lib_load())[0]["key"] == 2
        assert json.loads((Path(t) / "library.json.bak").read_text())[0]["key"] == 1
        try:
            api.lib_save("{broken"); raise AssertionError
        except ValueError:
            pass
        assert json.loads(api.lib_load())[0]["key"] == 2  # 깨진 저장은 기존 목록을 건드리지 않음
        api.lib_save('[{"g": 1}]', "calib")
        assert json.loads(api.lib_load("calib"))[0]["g"] == 1 and json.loads(api.lib_load())[0]["key"] == 2
        try:
            api.lib_load("../x"); raise AssertionError
        except KeyError:
            pass
        assert api.delete_originals([sha]) == 1 and api.read_original(sha) is None
    print("ok")
