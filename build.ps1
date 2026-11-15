# 빌드: version.py 수정 -> 이 스크립트 -> dist\PSA_Viewer_Setup.exe 확인 -> publish.ps1
# 폴더형(onedir) 빌드: 실행할 때마다 임시 폴더에 풀지 않아 시작이 빠름. 설치 프로그램은 Inno Setup.
$ErrorActionPreference = "Stop"
python sync_version.py
if ($LASTEXITCODE) { throw "sync_version 실패" }
pyinstaller --noconfirm --onedir --windowed --name PSA_Viewer --icon icon.ico `
  --add-data "index.html;." --add-data "cfb.min.js;." --add-data "version.js;." app.py
if ($LASTEXITCODE) { throw "pyinstaller 실패" }
# 빌드 결과가 원본과 같은지 대조 (이 PC에서 빌드 파일이 깨진 적이 있음)
foreach ($f in "index.html", "cfb.min.js", "version.js") {
  if ((Get-FileHash $f).Hash -ne (Get-FileHash "dist\PSA_Viewer\_internal\$f").Hash) { throw "빌드 결과의 $f 가 원본과 다릅니다" }
}
$ver = (python -c "import version; print(version.__version__)").Trim()
$iscc = Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) { $iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" }
& $iscc /Qp "/DAppVer=$ver" installer.iss
if ($LASTEXITCODE) { throw "설치 프로그램 만들기 실패" }
Write-Host "완성: dist\PSA_Viewer_Setup.exe (v$ver)"
