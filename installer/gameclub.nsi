; gameclub.nsi  -  NSIS installer script for GameClub
; Produces a single GameClub_Setup.exe that installs everything

Unicode True

;--------------------------------
; General

Name "GameClub"
OutFile "..\GameClub_Setup.exe"
InstallDir "$PROGRAMFILES64\GameClub"
InstallDirRegKey HKLM "Software\GameClub" "InstallPath"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
SetCompressorDictSize 32

;--------------------------------
; Version info embedded in the EXE

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName"     "GameClub"
VIAddVersionKey "ProductVersion"  "1.0.0"
VIAddVersionKey "CompanyName"     "Nikola Stojadinovic"
VIAddVersionKey "FileDescription" "GameClub Installer"
VIAddVersionKey "FileVersion"     "1.0.0"
VIAddVersionKey "LegalCopyright"  "Copyright (c) 2026 Nikola Stojadinovic"

;--------------------------------
; Interface

!include "MUI2.nsh"

!define MUI_ABORTWARNING
!define MUI_ICON "..\assets\gameclub.ico"
!define MUI_UNICON "..\assets\gameclub.ico"

; Welcome page
!define MUI_WELCOMEPAGE_TITLE "Welcome to GameClub Setup"
!define MUI_WELCOMEPAGE_TEXT "This will install GameClub - Controller Game Launcher on your computer.$\n$\nGameClub lets you browse and launch your games using a controller.$\n$\nClick Next to continue."
!insertmacro MUI_PAGE_WELCOME

; License
!insertmacro MUI_PAGE_LICENSE "license.rtf"

; Install directory
!insertmacro MUI_PAGE_DIRECTORY

; Components: choose whether to add the desktop shortcut
!insertmacro MUI_PAGE_COMPONENTS

; Start menu folder
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "GameClub"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKLM"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\GameClub"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "StartMenuFolder"
Var StartMenuFolder
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

; Install files page
!insertmacro MUI_PAGE_INSTFILES

; Finish page - offer to launch
!define MUI_FINISHPAGE_RUN "$INSTDIR\GameClub.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch GameClub now"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Before installing: offer to remove the old "GAMES" version
; (GameClub replaces it - your settings, covers and play stats are kept,
;  they live in your user folder, not in the install folder)

Function .onInit
    ; Older versions of this app: GAMES, then PadHub. Offer to remove them first
    ; (your settings, covers and play stats are kept - they live in your user folder).
    ReadRegStr $0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PadHub" "UninstallString"
    StrCmp $0 "" games
    ReadRegStr $1 HKLM "Software\PadHub" "InstallPath"
    MessageBox MB_YESNO|MB_ICONQUESTION \
        "PadHub is installed - GameClub is its new name.$\n$\nRemove PadHub now? Your settings, covers and play stats are kept." \
        IDNO games
    nsExec::Exec 'taskkill /f /im PadHub.exe'
    StrCmp $1 "" 0 +3
        ExecWait '$0 /S'
        Goto games
    ExecWait '$0 /S _?=$1'
    Delete "$1\Uninstall.exe"
    RMDir "$1"
  games:
    ReadRegStr $0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GAMES" "UninstallString"
    StrCmp $0 "" done
    ReadRegStr $1 HKLM "Software\GAMES" "InstallPath"
    MessageBox MB_YESNO|MB_ICONQUESTION \
        "An older version of this app (GAMES) is installed.$\n$\nRemove it now? GameClub replaces it - your settings, covers and play stats are kept." \
        IDNO done
    nsExec::Exec 'taskkill /f /im GAMES.exe'
    StrCmp $1 "" 0 +3
        ExecWait '$0 /S'
        Goto done
    ExecWait '$0 /S _?=$1'
    Delete "$1\Uninstall.exe"
    RMDir "$1"
  done:
FunctionEnd

;--------------------------------
; Installer section

Section "GameClub (required)" SecMain
    SectionIn RO   ; can't deselect

    ; Close GameClub if it's running so its files can be replaced
    nsExec::Exec 'taskkill /f /im GameClub.exe'

    SetOutPath "$INSTDIR"

    ; Copy entire PyInstaller bundle
    File /r "..\dist\GameClub\*.*"

    ; Write install path to registry
    WriteRegStr HKLM "Software\GameClub" "InstallPath" "$INSTDIR"
    WriteRegStr HKLM "Software\GameClub" "Version"     "1.0.0"

    ; Add/Remove Programs entry
    WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GameClub" \
                  "DisplayName"     "GameClub"
    WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GameClub" \
                  "DisplayVersion"  "1.0.0"
    WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GameClub" \
                  "Publisher"       "Nikola Stojadinovic"
    WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GameClub" \
                  "InstallLocation" "$INSTDIR"
    WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GameClub" \
                  "URLInfoAbout"    "https://github.com/stojadinovic771-boop/GameClub"
    WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GameClub" \
                  "DisplayIcon"     "$INSTDIR\GameClub.exe"
    WriteRegStr   HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GameClub" \
                  "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GameClub" \
                  "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GameClub" \
                  "NoRepair"  1

    ; Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Start menu shortcuts
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
        CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
        CreateShortcut  "$SMPROGRAMS\$StartMenuFolder\GameClub.lnk" \
                        "$INSTDIR\GameClub.exe" "" "$INSTDIR\GameClub.exe" 0
        CreateShortcut  "$SMPROGRAMS\$StartMenuFolder\Uninstall GameClub.lnk" \
                        "$INSTDIR\Uninstall.exe"
    !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd

;--------------------------------
; Optional desktop shortcut

Section "Desktop Shortcut" SecDesktop
    CreateShortcut "$DESKTOP\GameClub.lnk" "$INSTDIR\GameClub.exe" "" "$INSTDIR\GameClub.exe" 0
SectionEnd

;--------------------------------
; Section descriptions (shown on hover in component page)

LangString DESC_SecMain    ${LANG_ENGLISH} "GameClub application files (required)."
LangString DESC_SecDesktop ${LANG_ENGLISH} "Add a shortcut to GameClub on your Desktop."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain}    $(DESC_SecMain)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; Uninstaller

Section "Uninstall"

    ; Close GameClub if it's running
    nsExec::Exec 'taskkill /f /im GameClub.exe'

    ; Remove all installed files
    RMDir /r "$INSTDIR"

    ; Remove shortcuts
    !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
    Delete "$SMPROGRAMS\$StartMenuFolder\GameClub.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall GameClub.lnk"
    RMDir  "$SMPROGRAMS\$StartMenuFolder"
    Delete "$DESKTOP\GameClub.lnk"

    ; Stop starting with Windows
    DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "GameClub"
    nsExec::Exec 'schtasks /Delete /TN "GameClub" /F'
    nsExec::Exec 'schtasks /End /TN "GameClub Secure Desktop"'
    nsExec::Exec 'schtasks /Delete /TN "GameClub Secure Desktop" /F'
    ExpandEnvStrings $0 "%ProgramData%"
    RMDir /r "$0\GameClub"          ; UAC / sign-in controller log

    ; Remove registry entries
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GameClub"
    DeleteRegKey HKLM "Software\GameClub"

SectionEnd
