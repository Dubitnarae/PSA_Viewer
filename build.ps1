# exe 빌드: 먼저 version.py 수정 -> python sync_version.py -> 이 스크립트 실행
python sync_version.py
pyinstaller --noconfirm --onefile --windowed --name PSA_Viewer `
  --add-data "index.html;." --add-data "cfb.min.js;." --add-data "version.js;." app.py
