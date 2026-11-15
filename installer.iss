; PSA 입도 뷰어 설치 프로그램 (Inno Setup 6). build.ps1이 /DAppVer=버전 을 넘겨 컴파일한다.
; 관리자 권한 없이 사용자 폴더(%LOCALAPPDATA%\Programs\PSA_Viewer)에 설치 → 자동 업데이트가 UAC 창 없이 조용히 설치됨.
; 측정 데이터는 설치 폴더가 아니라 문서\PSA_Data에 둔다(storage.py). 제거해도 데이터는 남는다.
#ifndef AppVer
  #define AppVer "0.0.0"
#endif

[Setup]
AppId={{4640EAF6-8F6C-4161-8DF9-BB79E1480695}
AppName=PSA 입도 뷰어
AppVersion={#AppVer}
AppVerName=PSA 입도 뷰어 v{#AppVer}
AppPublisher=KIM YEONGDO
AppPublisherURL=https://github.com/Dubitnarae/PSA_Viewer
VersionInfoVersion={#AppVer}
DefaultDirName={localappdata}\Programs\PSA_Viewer
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=PSA_Viewer_Setup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\PSA_Viewer.exe
UninstallDisplayName=PSA 입도 뷰어
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
ChangesAssociations=yes

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "바탕 화면에 바로 가기 만들기"
Name: "assocngb"; Description: ".ngb 파일(HORIBA LA-960)을 두 번 누르면 이 프로그램으로 열기"
; .mea는 XRD 등 다른 장비도 쓰는 확장자라 기본 연결은 하지 않고 "연결 프로그램" 목록에만 넣는다

[InstallDelete]
; 업데이트 때 옛 버전의 라이브러리가 섞이지 않게 비우고 새로 깖
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "dist\PSA_Viewer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; v0.7.0 이하(exe 한 파일판)에서 넘어올 때: 옛 업데이트가 이 설치 프로그램을 옛 exe 자리에 놓고 실행하므로
; {src} = 옛 프로그램 폴더. 거기 있던 데이터와 저장 위치 설정을 가져온다(옛 폴더는 그대로 둠)
Source: "{src}\psa_viewer_settings.json"; DestDir: "{app}"; Flags: external skipifsourcedoesntexist onlyifdoesntexist uninsneveruninstall
Source: "{src}\PSA_Data\*"; DestDir: "{userdocs}\PSA_Data"; Flags: external recursesubdirs createallsubdirs skipifsourcedoesntexist onlyifdoesntexist uninsneveruninstall

[Icons]
Name: "{autoprograms}\PSA 입도 뷰어"; Filename: "{app}\PSA_Viewer.exe"
Name: "{autodesktop}\PSA 입도 뷰어"; Filename: "{app}\PSA_Viewer.exe"; Tasks: desktopicon

[Registry]
Root: HKA; Subkey: "Software\Classes\PSAViewer.Result"; ValueType: string; ValueData: "입도분석 결과"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\PSAViewer.Result\DefaultIcon"; ValueType: string; ValueData: "{app}\PSA_Viewer.exe,0"
Root: HKA; Subkey: "Software\Classes\PSAViewer.Result\shell\open\command"; ValueType: string; ValueData: """{app}\PSA_Viewer.exe"" ""%1"""
Root: HKA; Subkey: "Software\Classes\.ngb\OpenWithProgids"; ValueType: string; ValueName: "PSAViewer.Result"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.mea\OpenWithProgids"; ValueType: string; ValueName: "PSAViewer.Result"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.ngb"; ValueType: string; ValueName: ""; ValueData: "PSAViewer.Result"; Flags: uninsdeletevalue; Tasks: assocngb

[Run]
; 조용한 설치(자동 업데이트)에서도 실행되도록 skipifsilent를 붙이지 않음
Filename: "{app}\PSA_Viewer.exe"; Description: "PSA 입도 뷰어 실행"; Flags: nowait postinstall

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssDone) and (not WizardSilent) and DirExists(ExpandConstant('{src}\PSA_Data')) then
    MsgBox('예전 프로그램 폴더의 데이터를 문서\PSA_Data 로 복사했어요.' + #13#10 + #13#10 +
      '앞으로는 시작 메뉴나 바탕 화면의 "PSA 입도 뷰어"로 실행해 주세요.' + #13#10 +
      '예전 폴더(' + ExpandConstant('{src}') + ')는 새 프로그램에서 데이터를 확인한 뒤 지워도 돼요.',
      mbInformation, MB_OK);
end;
