#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

; 4/9/2019
; Win+N: Hold down left mouse button
; Win+Q: quit

OALDpid := 0
OALDexe := "C:\OALD9\OALD9.exe"
urlBark := ""

; put this config.ini in your Desktop\OALD9\ folder to custom the above variables, example:
; [core]
; OALDexe=F:\OALD9\OALD9.exe
; [OALDAutoScroll]
; urlBark=https://api.day.app/xxxxxxxxxxxxxxx/

iniPath := A_Desktop . "\OALD9\config.ini"

IniRead, OALDexe, %iniPath%, core, OALDexe, %OALDexe%
IniRead, urlBark, %iniPath%, OALDAutoScroll, urlBark, %urlBark%

checkOALDTimerOn := false

#n::
    if checkOALDTimerOn
    {
        checkOALDTimerOn := false
        SetTimer, CheckOALD, Off
        SetTimer, UpdateOALDEntries, Off
    }
    else
    {
        checkOALDTimerOn := true
        SetTimer, CheckOALD, 3000
        SetTimer, UpdateOALDEntries, 10
    }
return

#q::ExitApp

UpdateOALDEntries:
    ;SendInput, {WheelDown}
    SendInput, {PgDn}
    return

CheckOALD:
    Process, Exist, OALD9.exe
    if ErrorLevel
        return
    ReportError("Process is dead")
    
    if (!LaunchOALD())
        return
return

ReportError(msg)
{
    SendToBark("OALD", msg)
    checkOALDTimerOn := false
    SetTimer, CheckOALD, Off
    SetTimer, UpdateOALDEntries, Off
    return false
}

LaunchOALD()
{
    global OALDexe, OALDpid
    run, %OALDexe%, , , OALDpid
    Sleep, 8000
    Process, Exist, OALD9.exe
    OALDpid := ErrorLevel
    if OALDpid == 0
        return ReportError("failed to launch exe")
    ;WinActivate, ahk_pid %OALDpid%
    
    return true
}

SendToBark(title, body)
{
    global urlBark
    finalURL := urlBark . title . "/" . body . " at " . A_Now
    try
    {
        req := ComObjCreate("WinHttp.WinHttpRequest.5.1")
        req.Open("POST", finalURL)
        req.Send()
    }
    catch e
    {
    }
}
