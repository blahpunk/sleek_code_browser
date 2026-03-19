#define MyAppId "{{D6CB43B2-71A3-44A5-8FC6-A80DBDFEA1A3}"
#define MyAppName "Sleek Code Browser"
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher=Sleek
DefaultDirName={autopf}\Sleek Code Browser
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir={#SourcePath}..\..\dist
OutputBaseFilename=SleekCodeBrowser-Setup-{#AppVersion}
SetupIconFile={#SourcePath}build\icon.ico
UninstallDisplayIcon={app}\SleekCodeBrowser.exe
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog
ChangesEnvironment=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "addtopath"; Description: "Add Sleek to PATH"; GroupDescription: "Additional tasks:"; Flags: checked
Name: "addcontextmenu"; Description: "Add Sleek to Explorer context menu"; GroupDescription: "Additional tasks:"; Flags: checked

[Files]
Source: "{#SourcePath}build\SleekCodeBrowser.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}sleek.cmd"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}build\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Sleek Code Browser"; Filename: "{app}\SleekCodeBrowser.exe"; IconFilename: "{app}\icon.ico"
Name: "{autoprograms}\Uninstall Sleek Code Browser"; Filename: "{uninstallexe}"

[Registry]
Root: HKLM; Subkey: "Software\Classes\Directory\shell\SleekHere"; ValueType: string; ValueName: ""; ValueData: "Sleek Here"; Tasks: addcontextmenu; Check: IsAdminInstallMode; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Directory\shell\SleekHere"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\SleekCodeBrowser.exe"; Tasks: addcontextmenu; Check: IsAdminInstallMode
Root: HKLM; Subkey: "Software\Classes\Directory\shell\SleekHere\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SleekCodeBrowser.exe"" ""%1"""; Tasks: addcontextmenu; Check: IsAdminInstallMode; Flags: uninsdeletekey

Root: HKLM; Subkey: "Software\Classes\Directory\Background\shell\SleekHere"; ValueType: string; ValueName: ""; ValueData: "Sleek Here"; Tasks: addcontextmenu; Check: IsAdminInstallMode; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Classes\Directory\Background\shell\SleekHere"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\SleekCodeBrowser.exe"; Tasks: addcontextmenu; Check: IsAdminInstallMode
Root: HKLM; Subkey: "Software\Classes\Directory\Background\shell\SleekHere\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SleekCodeBrowser.exe"" ""%V"""; Tasks: addcontextmenu; Check: IsAdminInstallMode; Flags: uninsdeletekey

Root: HKCU; Subkey: "Software\Classes\Directory\shell\SleekHere"; ValueType: string; ValueName: ""; ValueData: "Sleek Here"; Tasks: addcontextmenu; Check: not IsAdminInstallMode; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\SleekHere"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\SleekCodeBrowser.exe"; Tasks: addcontextmenu; Check: not IsAdminInstallMode
Root: HKCU; Subkey: "Software\Classes\Directory\shell\SleekHere\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SleekCodeBrowser.exe"" ""%1"""; Tasks: addcontextmenu; Check: not IsAdminInstallMode; Flags: uninsdeletekey

Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\SleekHere"; ValueType: string; ValueName: ""; ValueData: "Sleek Here"; Tasks: addcontextmenu; Check: not IsAdminInstallMode; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\SleekHere"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\SleekCodeBrowser.exe"; Tasks: addcontextmenu; Check: not IsAdminInstallMode
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\SleekHere\command"; ValueType: string; ValueName: ""; ValueData: """{app}\SleekCodeBrowser.exe"" ""%V"""; Tasks: addcontextmenu; Check: not IsAdminInstallMode; Flags: uninsdeletekey

[Code]
function GetPathRoot(): Integer;
begin
  if IsAdminInstallMode then
    Result := HKLM
  else
    Result := HKCU;
end;

function GetPathSubkey(): String;
begin
  if IsAdminInstallMode then
    Result := 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
  else
    Result := 'Environment';
end;

function PathListContains(const PathValue, DirectoryToFind: String): Boolean;
var
  Parts: TArrayOfString;
  Index: Integer;
begin
  Result := False;
  SplitString(PathValue, ';', Parts);
  for Index := 0 to GetArrayLength(Parts) - 1 do
  begin
    if CompareText(Trim(Parts[Index]), Trim(DirectoryToFind)) = 0 then
    begin
      Result := True;
      Exit;
    end;
  end;
end;

function AddPathEntry(const PathValue, DirectoryToAdd: String): String;
begin
  Result := Trim(PathValue);
  if PathListContains(Result, DirectoryToAdd) then
    Exit;

  if (Result <> '') and (Result[Length(Result)] <> ';') then
    Result := Result + ';';
  Result := Result + DirectoryToAdd;
end;

function RemovePathEntry(const PathValue, DirectoryToRemove: String): String;
var
  Parts: TArrayOfString;
  Index: Integer;
  Item: String;
begin
  Result := '';
  SplitString(PathValue, ';', Parts);
  for Index := 0 to GetArrayLength(Parts) - 1 do
  begin
    Item := Trim(Parts[Index]);
    if (Item = '') or (CompareText(Item, DirectoryToRemove) = 0) then
      continue;
    if Result <> '' then
      Result := Result + ';';
    Result := Result + Item;
  end;
end;

procedure AddInstallDirToPath();
var
  PathRoot: Integer;
  PathSubkey: String;
  PathValue: String;
begin
  PathRoot := GetPathRoot();
  PathSubkey := GetPathSubkey();
  if not RegQueryStringValue(PathRoot, PathSubkey, 'Path', PathValue) then
    PathValue := '';

  PathValue := AddPathEntry(PathValue, ExpandConstant('{app}'));
  RegWriteExpandStringValue(PathRoot, PathSubkey, 'Path', PathValue);
  RefreshEnvironment();
end;

procedure RemoveInstallDirFromPath();
var
  PathRoot: Integer;
  PathSubkey: String;
  PathValue: String;
begin
  PathRoot := GetPathRoot();
  PathSubkey := GetPathSubkey();
  if not RegQueryStringValue(PathRoot, PathSubkey, 'Path', PathValue) then
    exit;

  PathValue := RemovePathEntry(PathValue, ExpandConstant('{app}'));
  RegWriteExpandStringValue(PathRoot, PathSubkey, 'Path', PathValue);
  RefreshEnvironment();
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and WizardIsTaskSelected('addtopath') then
    AddInstallDirToPath();
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
    RemoveInstallDirFromPath();
end;
