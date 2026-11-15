# 릴리스 게시: build.ps1로 만들고 실행 확인한 dist\PSA_Viewer_Setup.exe를 그대로 올린다 (여기서 다시 빌드하지 않음).
# 올리는 파일
#  - PSA_Viewer_Setup.exe(+.sha256): 설치판(v0.8.0~)의 자동 업데이트가 받음
#  - PSA_Viewer.exe(+.sha256): 같은 설치 프로그램. v0.7.0 이하 exe 한 파일판의 자동 업데이트가 이 이름을 받아 실행 → 설치판으로 넘어옴
$ErrorActionPreference = "Stop"
$ver = (python -c "import version; print(version.__version__)").Trim()
$setup = "dist\PSA_Viewer_Setup.exe"
if (-not (Test-Path $setup)) { throw "먼저 build.ps1을 실행하세요." }
if ((Get-Item $setup).VersionInfo.ProductVersion -notlike "$ver*") { throw "설치 파일 버전이 $ver 이 아닙니다. build.ps1을 다시 실행하세요." }
Copy-Item $setup dist\PSA_Viewer.exe -Force
foreach ($n in "PSA_Viewer_Setup.exe", "PSA_Viewer.exe") {
  $hash = (Get-FileHash "dist\$n" -Algorithm SHA256).Hash.ToLower()
  Set-Content -Encoding ascii "dist\$n.sha256" "$hash  $n"
}
# CHANGELOG의 해당 버전 섹션을 릴리스 설명으로 사용
$notes = (Get-Content CHANGELOG.md -Raw -Encoding utf8) -split "(?m)^## " | Where-Object { $_.StartsWith("[$ver]") } | Select-Object -First 1
if (-not $notes) { throw "CHANGELOG.md에 [$ver] 섹션이 없습니다." }
$notes = ($notes -split "`n", 2)[1].Trim() -replace "(?s)\s*---\s*$", ""
$nf = New-TemporaryFile; [IO.File]::WriteAllText($nf, $notes)  # BOM 없이
git tag -f "v$ver"; git push -f origin "v$ver"
gh release create "v$ver" dist\PSA_Viewer_Setup.exe dist\PSA_Viewer_Setup.exe.sha256 dist\PSA_Viewer.exe dist\PSA_Viewer.exe.sha256 --title "PSA 입도 뷰어 v$ver" --notes-file $nf
Remove-Item $nf
