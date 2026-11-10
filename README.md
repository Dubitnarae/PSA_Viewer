# PSA 입도 뷰어

레이저 회절 입도분석기 결과 파일을 장비 프로그램 없이 열어 보고 정리하는 Windows 프로그램입니다.
파일은 이 PC 안에서만 읽으며 밖으로 보내지 않습니다.

| 장비 | 파일 |
|---|---|
| HORIBA LA-960 | `.ngb` |
| Malvern Mastersizer 2000 | `.mea` |

## 내려받기

[최신 릴리스](https://github.com/Dubitnarae/PSA_Viewer/releases/latest)에서 `PSA_Viewer.exe`를 받아 실행합니다.

- 설치가 필요 없고, 인터넷 없이 동작합니다.
- 시작할 때 새 버전이 있으면 알려 주고, 동의하면 SHA256을 확인한 뒤 스스로 교체합니다.

## 기능

- **입도분포 보기**: 빈도·누적 곡선, D10 · D50 · D90 · Span. 여러 파일을 겹쳐 비교(화면에 8개까지)
- **수율 계산**: 기준 입경 이하 누적 % (예: 53 µm under)
- **데이터 목록**: 연 파일의 결과와 원본 사본을 자동 저장. 로트·메모 입력, 검색, CSV 저장
- **작업 저장 / 열기**: 열어 둔 파일과 수율 기준을 `.psa` 파일 하나로 저장
- **혼합 예측**: 분말 여러 개를 혼합비(무게 %)대로 섞었을 때의 분포 예측, 목표 D값·구간 분율에 맞는 혼합비 찾기, 실측 혼합품과 비교
- **혼합분말 보정**: 실측과 예측의 차이를 묶음별로 기록해 다음 예측에 반영
- **.mea 측정 조건 표시**: Mode, 균일도, 차폐율, 잔차, 농도, 분석 모델, SOP, 분산 조건, 장비 경보

버전별 변경 내용은 [CHANGELOG.md](CHANGELOG.md)에 있습니다.

## 저장 데이터

저장한 데이터는 exe와 같은 폴더의 `PSA_Data` 폴더에 쌓이며, 업데이트해도 그대로 남습니다.
저장 위치는 프로그램 안에서 바꿀 수 있습니다. exe를 옮길 때는 `PSA_Data` 폴더도 함께 옮기세요.

## 직접 빌드

Python과 `pywebview`, `pyinstaller`가 필요합니다.

```powershell
pip install pywebview pyinstaller
python app.py     # 빌드 없이 바로 실행
.\build.ps1       # dist\PSA_Viewer.exe 생성
```

점검: `node test_mix.js`, `node test_mea.js`, `python storage.py`

버전은 `version.py` 한 곳에서만 고칩니다.

## 알림

HORIBA, Malvern과 관계없는 개인 제작 프로그램입니다. 표시 값은 결과 파일에 기록된 값을 읽거나 다시 계산한 것이므로, 중요한 판단은 장비 프로그램의 값과 대조해 주세요.

개발: KIM YEONGDO
