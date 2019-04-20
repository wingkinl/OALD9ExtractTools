# OALD9ExtractTools
Some tools for extracting OALD 9 DVD for PC

![Final result](docs/images/6.png?raw=true)

## Steps to extract
1. Dumping XML from OALD9.exe. 
Run OALD9.exe and open the process in Cheat Engine, then open the OALD9.CT, enable the 'AutoDumpXML' script
![Dump XML by Cheat Engine](docs/images/1.png?raw=true)

2. Scroll down on OALD9 program so that Cheat Engine dumps the XML to your output folder (default path: C:\OALD9_Out)
Note: you can also run the AutoHotkey script (OALD9AutoScroll.ahk), click inside the main display area of OALD9 program to make sure it is currently activated, then press Win+N, AHK script will automatically keep scrolling (press it again to pause). You can also press Win+Q to exit the script.
![XML result](docs/images/2.png?raw=true)

3. Run ParseOALD9.py to convert the XML as MDict format text files or HTML files. This can be controled by preparing an ini file on your {Desktop}\OALD9\config.ini with the following format:
```
[core]
    OALDexe=C:\OALD9\OALD9.exe
    OALDOutDir=C:\OALD9_Out\
    OALDFinalDir=C:\OALD9_Final
[Parser]
    prettyOutput=1
    debugPrintMsg=1
    addMsgLogFile=0
    parseOnlyNoOutput=0
    makeMDictFormat=1
```
![Converting](docs/images/5.png?raw=true)
![MDict result](docs/images/3.png?raw=true)

4. Make MDX/MDD with MdxBuilder

![MdxBuilder](docs/images/4.png?raw=true)
