#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

; 4/9/2019
; Win+N: Hold down left mouse button
; Win+Q: quit

OALDpid := 0
OALDexe := "C:\OALD9\OALD9.exe"
OALDOutDir := "C:\OALD9_Out\"
urlBark := ""

; put this config.ini in your Desktop\OALD9\ folder to custom the above variables, example:
; [core]
; OALDexe=F:\OALD9\OALD9.exe
; [OALDAutoScroll]
; urlBark=https://api.day.app/xxxxxxxxxxxxxxx/

iniPath := A_Desktop . "\OALD9\config.ini"

IniRead, OALDexe, %iniPath%, core, OALDexe, %OALDexe%
IniRead, OALDOutDir, %iniPath%, core, OALDOutDir, %OALDOutDir%
IniRead, urlBark, %iniPath%, OALDAutoScroll, urlBark, %urlBark%

checkOALDTimerOn := false

CheckOutputFileRelaunchOALD()

#n::
    if checkOALDTimerOn
    {
        checkOALDTimerOn := false
        SetTimer, CheckOALD, Off
    }
    else
    {
        checkOALDTimerOn := true
        SetTimer, CheckOALD, 3000
        Click, down
    }
return

#q::ExitApp


CheckOALD:
    Process, Exist, OALD9.exe
    if ErrorLevel
        return
    ReportError("Process is dead")
    
    if (!CheckOutputFileRelaunchOALD())
        return
return

ReportError(msg)
{
    SendToBark("OALD", msg)
    SetTimer, CheckOALD, Off
    return false
}

CheckOutputFileRelaunchOALD()
{
    GetLastEntryInOutput(lastWord)

    if (!LaunchOALD(lastWord))
        return false
    return true
}

CheckLastOutputFile(ByRef path)
{
    global OALDOutDir
    num := 1
    Loop
    {
        pathTemp := OALDOutDir . Format("{:06d}.xml", num)
        if ( !FileExist(pathTemp) )
            break
        ++num
    }
    if num > 1
        path := OALDOutDir . Format("{:06d}.xml", num-1)
    return num-1
}

GetLastEntryInOutput(ByRef word)
{
    num := CheckLastOutputFile(fileLastXML)
    if num <= 0
        return ReportError("failed to find any output file.")
    FileRead, fileText, %fileLastXML%
    lastEntryPos := InStr(fileText, "<lg:block num=", false, -1, 2)
    if lastEntryPos == 0
        return ReportError("failed to find the last entry in output file.")
    posWord := InStr(fileText, "wd=""", false, lastEntryPos)
    if posWord == 0
        return ReportError("failed to find word of the last entry in output file.")
    posWord := posWord + 4
    posWordEnd := InStr(fileText, """", false, posWord)
    word := SubStr(fileText, posWord, posWordEnd-posWord)
    if StrLen(word) == 0
        return ReportError("empty word in the last entry")
    return true
}

LaunchOALD(word)
{
    global OALDexe, OALDpid
    run, %OALDexe%, , , OALDpid
    Sleep, 8000
    Process, Exist, OALD9.exe
    OALDpid := ErrorLevel
    if OALDpid == 0
        return ReportError("failed to launch exe")
    ;WinActivate, ahk_pid %OALDpid%
    ControlSend, LgWndSimpleClass228, %word%, ahk_pid %OALDpid%
    Sleep, 1000
    click, 39, 228
    Sleep, 500
    
    return true
}

SendToBark(title, body)
{
    global urlBark
    finalURL := urlBark . title . "/" . body . " at " . A_Now
    req := ComObjCreate("WinHttp.WinHttpRequest.5.1")
    req.Open("POST", finalURL)
    req.Send()
}
