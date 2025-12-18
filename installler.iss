[Setup]
AppId={{08E49D96-FC81-4729-9CCF-DCE70EFF758E}
AppName=Accuracy Report
AppVersion=1.1.1
AppPublisher=Preston Fox
AppPublisherURL=https://github.com/Hauh4444/WIS-Accuracy-Data-Analytics
AppSupportURL=https://github.com/Hauh4444/WIS-Accuracy-Data-Analytics
AppUpdatesURL=https://github.com/Hauh4444/WIS-Accuracy-Data-Analytics
CloseApplications=yes
CloseApplicationsFilter=AccuracyReport.exe
DefaultDirName={autopf}\Accuracy Report
DisableDirPage=yes
UninstallDisplayIcon={app}\AccuracyReport.exe
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
DisableProgramGroupPage=yes
OutputBaseFilename=mysetup
SolidCompression=yes
WizardStyle=modern dynamic

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "assets\resources\accessdatabaseengine_X64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "dist\AccuracyReport.exe"; DestDir: "{app}"; Flags: replacesameversion restartreplace

[Registry]
Root: HKA; Subkey: "Software\Classes\\OpenWithProgids"; ValueType: string; ValueName: ""; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\"; ValueType: string; ValueName: ""; ValueData: ""; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\AccuracyReport.exe,0"
Root: HKA; Subkey: "Software\Classes\\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\AccuracyReport.exe"" ""%1"""

[Icons]
Name: "{autoprograms}\Accuracy Report"; Filename: "{app}\AccuracyReport.exe"
Name: "{autodesktop}\Accuracy Report"; Filename: "{app}\AccuracyReport.exe"; Tasks: desktopicon

[Run]
Filename: "{tmp}\accessdatabaseengine_X64.exe"; Parameters: "/quiet"; StatusMsg: "Installing Access Database Engine..."; Flags: waituntilterminated
Filename: "{app}\AccuracyReport.exe"; Description: "{cm:LaunchProgram,Accuracy Report}"; Flags: nowait postinstall skipifsilent