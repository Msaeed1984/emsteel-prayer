; Inno Setup Script for EMSTEEL Prayer Agent
; تم التطوير بواسطة IT Client Excellence

#define MyAppName "EMSTEEL Prayer Agent"
#define MyAppVersion "1.0"
#define MyAppPublisher "IT Client Excellence"
#define MyAppExeName "EMSTEEL_Prayer_Agent.exe"

[Setup]
; معرف فريد للتطبيق
AppId={{EMSTEEL-PRAYER-AGENT}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

; =====================================================
; 🔥 المسار الافتراضي للتثبيت - Program Files (64-bit)
; =====================================================
DefaultDirName={pf}\{#MyAppName}

; بديل إذا أردت Force 32-bit (غير موصى به)
; DefaultDirName={pf32}\{#MyAppName}

DefaultGroupName={#MyAppName}
AllowNoIcons=yes
PrivilegesRequired=lowest
; مجلد خروج المثبت النهائي
OutputDir=C:\Users\Administrator\emsteel\prayer_agent\installer
OutputBaseFilename=EMSTEEL_Prayer_Setup
; أيقونة المثبت
SetupIconFile=C:\Users\Administrator\emsteel\prayer_agent\Emsteel2026.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
DisableProgramGroupPage=yes
UsePreviousAppDir=yes
CreateUninstallRegKey=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startup"; Description: "Run at Windows startup"; GroupDescription: "Startup options"

[Files]
; ملف EXE الرئيسي - من مجلد dist
Source: "C:\Users\Administrator\emsteel\prayer_agent\dist\EMSTEEL_Prayer_Agent.exe"; DestDir: "{app}"; Flags: ignoreversion

; أيقونة البرنامج
Source: "C:\Users\Administrator\emsteel\prayer_agent\Emsteel2026.ico"; DestDir: "{app}"; Flags: ignoreversion

; ملف بيانات الصلاة (لن يتم حذفه عند إلغاء التثبيت)
Source: "C:\Users\Administrator\emsteel\prayer_agent\prayer_data.json"; DestDir: "{app}"; Flags: ignoreversion uninsneveruninstall

; ملف الإعدادات (إذا كان موجوداً مسبقاً، لا يتم استبداله)
Source: "C:\Users\Administrator\emsteel\prayer_agent\prayer_settings.json"; DestDir: "{app}"; Flags: ignoreversion uninsneveruninstall onlyifdoesntexist

; مجلد الأيقونات بالكامل
Source: "C:\Users\Administrator\emsteel\prayer_agent\icons\*"; DestDir: "{app}\icons"; Flags: recursesubdirs createallsubdirs

[Icons]
; اختصار في قائمة ابدأ
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; اختصار إلغاء التثبيت
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; اختصار على سطح المكتب (اختياري)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; إضافة البرنامج إلى بدء التشغيل التلقائي مع Windows
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "EMSTEEL_Prayer"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startup

[Run]
; تشغيل البرنامج فور انتهاء التثبيت
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: postinstall nowait skipifsilent runascurrentuser

[UninstallDelete]
; حذف مجلد الأيقونات عند إلغاء التثبيت
Type: filesandordirs; Name: "{app}\icons"

[Code]
var
  WelcomePage: TWizardPage;
  WelcomeLabel: TNewStaticText;

procedure InitializeWizard;
begin
  WelcomePage := CreateCustomPage(wpWelcome, 'EMSTEEL Prayer Agent', 'برنامج أوقات الصلاة والأذان');
  
  WelcomeLabel := TNewStaticText.Create(WelcomePage);
  WelcomeLabel.Parent := WelcomePage.Surface;
  WelcomeLabel.Caption := '📌 البرنامج سيعمل في شريط المهام بجانب الساعة' + #13#13 +
                          '🔔 سيظهر إشعار عند كل وقت أذان' + #13#13 +
                          '🔊 يمكنك التحكم في الصوت واللغة من قائمة البرنامج' + #13#13 +
                          '--------------------------------------------' + #13#13 +
                          '📌 The program will run in the system tray' + #13 +
                          '🔔 A notification will appear at each prayer time' + #13 +
                          '🔊 You can control sound and language from the menu';
  WelcomeLabel.AutoSize := False;
  WelcomeLabel.Width := WelcomePage.SurfaceWidth - 20;
  WelcomeLabel.Height := 150;
  WelcomeLabel.WordWrap := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ErrorCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    if MsgBox('✅ تم تثبيت EMSTEEL Prayer Agent بنجاح!' + #13#13 +
       '📍 المسار: ' + ExpandConstant('{app}') + #13#13 +
       'البرنامج يعمل الآن في شريط المهام بجانب الساعة.' + #13#13 +
       '✅ EMSTEEL Prayer Agent has been installed successfully!' + #13 +
       '📍 Path: ' + ExpandConstant('{app}') + #13#13 +
       'The program is now running in the system tray.' + #13#13 +
       'هل تريد فتح مجلد التثبيت؟' + #13 +
       'Do you want to open the installation folder?', 
       mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', ExpandConstant('{app}'), '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
    end;
  end;
end;