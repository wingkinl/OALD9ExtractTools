# OALD9ExtractTools
Some tools for extracting OALD 9 DVD for PC
一些提取 OALD 9 Windows 光盘版数据的工具

![Final result](docs/images/6.png?raw=true)

## Steps to extract
### 1. Dumping XML from OALD9.exe. 从 OALD9.exe 提取 XML
Run OALD9.exe and open the process in Cheat Engine, then open the OALD9.CT, enable the 'AutoDumpXML' script
运行 OALD9.exe，然后在 Cheat Engine 中打开这个进程，打开 OALD9.CT，启用 AutoDumpXML 这个脚本
![Dump XML by Cheat Engine](docs/images/1.png?raw=true)

2. Scroll down on OALD9 program so that Cheat Engine dumps the XML to your output folder (default path: C:\OALD9_Out) 在 OALD9 的查词主界面滚动时前面 CE 的脚本会自动把 XML 写入指定的文件夹（默认是 C:\OALD9_Out）
Note: you can also run the AutoHotkey script (OALD9AutoScroll.ahk), click inside the main display area of OALD9 program to make sure it is currently activated, then press Win+N, AHK script will automatically keep scrolling (press it again to pause). You can also press Win+Q to exit the script.
If OALD9.exe crashes, AHK script will try to relaunch it, the progress (entry ID) will be saved as lastEntry.txt in the output folder. You will need to repeat the process from step 1, the CE script automatically continue with the last progress.
如果嫌手动滚动太麻烦，可以试试看用 AutoHotkey 运行 OALD9AutoScroll.ahk，回到 OALD 主界面点一下中间区域（以确保它是当前窗口），然后按 Win+N 就会自动滚动了。按下 Win+Q 就会自动退出这个 AHK 脚本。
万一 OALD9.exe 闪退，AHK 脚本会尝试自动重新运行它，这时你需要重复一遍前面的步骤，闪退之前的进度会保存，所以继续滚动即可接着原本的进度。
![XML result](docs/images/2.png?raw=true)

There will be 4,124 XML files in total when it finishes (the last one should be 061845.xml), you may need to manually stop the script and Cheat Engine.

全部提取出来会有4124个XML文件，最后一个文件名应该是 061845.xml。完成后自己退出所有的脚本和 Cheat Engine 即可。

3. Run ParseOALD9.py to convert the XML as MDict format text files or HTML files. This can be controled by preparing an ini file on your {Desktop}\OALD9\config.ini with the following format:
运行 ParseOALD9.py，把所有 XML 文件转换成 MDict 或者 HTML 格式。你也可以在桌面的 OALD9 文件夹下放一个 config.ini 来修改一些参数。
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
用 MdxBuilder 制作 MDX/MDD 词典
![MdxBuilder](docs/images/4.png?raw=true)
