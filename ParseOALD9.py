# OALD9 DVD for Windows XML Parser
# 4/9/2019

import os
import re
import shutil
from shutil import copyfile
import glob
from bs4 import BeautifulSoup
#import html5lib
import lxml
import copy
import configparser
import warnings

#inputParser = "html5lib"
inputParser = "lxml"
inputDir = r"C:\OALD9_Out"
outputDir = r"C:\OALD9_Final"
curInputFile = ""
# source https://www.oxfordlearnersdictionaries.com/external/styles/interface.css?version=1.6.51
interfaceCSS = r'styles\interface.css'
# source: https://www.oxfordlearnersdictionaries.com/external/styles/oxford.css?version=1.6.51
oxfordCSS = r'styles\oxford.css'
prettyOutput = True
debugPrintMsg = False
addMsgLogFile = True

desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
customDir = desktop + "\\OALD9\\"
iniPath = customDir + r"config.ini"
logFile = customDir + r"OALD9ParserLog.txt"

config = configparser.ConfigParser()
config.read(iniPath)
if config.has_option('core', 'OALDOutDir'):
    inputDir = config['core']['OALDOutDir']
if config.has_option('core', 'OALDFinalDir'):
    outputDir = config['core']['OALDFinalDir']
if config.has_option('Parser', 'prettyOutput'):
    value = config['Parser']['prettyOutput'].lower()
    prettyOutput = value in ['true', '1']
if config.has_option('Parser', 'debugPrintMsg'):
    value = config['Parser']['debugPrintMsg'].lower()
    debugPrintMsg = value in ['true', '1']
if config.has_option('Parser', 'addMsgLogFile'):
    value = config['Parser']['addMsgLogFile'].lower()
    addMsgLogFile = value in ['true', '1']

def AddLog(text):
    text = curInputFile + ": " + text
    if debugPrintMsg:
        print(text)
    if addMsgLogFile:
        with open(logFile, "a") as file:
            file.write(text + "\r\n")

class OALDEntryParser:
    def __init__(self):
        self._curBlockNum = 0
    
    def _ReplaceSpecialSymbol(self, mo):
        if mo.group(1) == '@':
            symbol_mapping = {'a' : r'\u00E6'}
            return symbol_mapping[mo.group(2)]
        elif mo.group(1) == 's':
            symbol_mapping = {'h' : r'\u2018',  # ‘
                              'i' : r'\u2019',  # ’
                              'n' : r'\u2014',  # —
                              'D' : r'\u00B7',  # ·
                              'L' : r'\u00D7'}  # ×
            return symbol_mapping[mo.group(2)]
        return mo.group()
    
    def _EscapeSpecialText(self, text):
        # decode \@?, \s?
        try:
            text = re.sub(r'\\([@s])(.)', lambda mo: self._ReplaceSpecialSymbol(mo), text)
        except Exception as e:
            AddLog(f"failed to replace special symbol in '{curFileName}'\r\n\t{repr(e)}")
        
        # decode unicode text "\uXXXX"
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            text = text.encode().decode('unicode-escape')
            if len(w):
                AddLog(f"failed to replace unicode in '{curFileName}'\r\n\t{str(w[-1].message)}")
        return text

    def _ParseConvertElem(self, elem, tagName):
        if elem.attrs:
            # preserve the attributes for styling some tags
            # geo for "blue"/"red"
            geo = ""
            if elem.has_attr('geo'):
                geo = elem['geo']
            elem.attrs.clear()
            if geo:
                elem['geo'] = geo
        if elem.name == "ref":
            elem['href'] = f"entry://{elem.string}"
        if (elem.name != tagName):
            elem['class'] = elem.name
            elem.name = tagName
        childCount = len(elem.contents)
        for nn in range(childCount-1, -1, -1):
            child = elem.contents[nn]
            removeChild = False
            newTagName = "span"
            if (child.name is None):
                continue
            elif child.name == 'span':
                pass
            elif (child.name == 'img'):
                newTagName = child.name
            elif child.name == 'top-g':
                self._ParseConvertElem(child, 'span')
                newElem = self._bsOut.new_tag('div')
                newElem['class'] = 'top-container'
                childCopy = copy.copy(child)
                # change it to webtop-g to satisfy CSS
                #if (elem.name == 'ol'):
                #    childCopy['class'] = 'webtop-g'
                newElem.append(childCopy)
                child.replace_with(newElem)
                continue
            elif child.name == 'sn-gs':
                pass
            elif child.name == 'sn-g':
                # because idioms could also contain this tag, we need to exclude that
                if (elem['class'] == 'sn-gs') and (elem.parent.name == 'ol'):
                    newTagName = "li"
            elif child.name == 'def':
                pass
            elif child.name == 'ndv':
                # see "A noun", in the [scale] of C
                pass
            elif child.name == 'cl':
                # see "A noun", [A in/for] Biology
                pass
            elif child.name == 'gl':
                # see "A noun", all through high school
                pass
            elif child.name == 'rx-g':
                # see "A noun", He had straight A's
                pass
            elif child.name == 'xr-gs':
                # see "A noun", SEE ALSO
                pass
            elif child.name == 'esc':
                # see "A noun", SEE ALSO, no example on web
                pass
            elif child.name == 'ref':
                newTagName = "a"
            elif child.name == 'xr-g':
                # in "A noun" see also, link
                pass
            elif child.name == 'xh':
                # in "A noun" see also, link
                pass
            elif child.name == 'xw':
                # in "aback" see also, link
                pass
            elif child.name == "ei":
                # see "a indefinite article", [one] before some numbers
                pass
            elif child.name == "ebi":
                # see "George Abbott ", The Boys from Syracuse
                pass
            elif child.name == 'idm-gs':
                # idioms
                pass
            elif child.name == 'idm-g':
                # idioms
                pass
            elif child.name == 'idm-l':
                # idioms
                pass
            elif child.name == 'idm':
                # idioms
                pass
            elif child.name == 'sn-gs':
                # idioms
                pass
            elif child.name == 'sn-g':
                # idioms
                pass
            elif child.name == 'res-g':
                pass
            elif child.name == 'dis-g':
                pass
            elif child.name == 'dtxt':
                pass
            elif child.name == 'x-gs':
                pass
            elif child.name == 'x-g':
                pass
            elif child.name == 'x':
                pass
            elif child.name == 'xs':
                pass
            elif child.name == 'xw':
                # see "aboard", synonym "on board"
                pass
            elif child.name == 'h':
                newTagName = "h2"
            elif child.name == 'pos-g':
                pass
            elif child.name == 'pos':
                pass
            elif child.name == 'pron-gs':
                newTagName = "div"
            elif child.name == 'pron-g':
                pass
            elif (child.name == 'blue') or (child.name == 'red'):
                prefix = self._bsOut.new_tag("span")
                prefix['class'] = 'prefix'
                child.wrap(prefix)
            elif child.name == 'phon':
                pass
            elif child.name == 'v-gs':
                pass
            elif child.name == 'v-g':
                pass
            elif child.name == 'v':
                pass
            elif child.name == 'st':
                pass
            elif child.name == 'if-gs':
                pass
            elif child.name == 'if-g':
                pass
            elif child.name == 'if':
                pass
            elif child.name == 'un':
                pass
            elif child.name == 'eb':
                pass
            elif child.name == 'label-g':
                pass
            elif child.name == 'reg':
                pass
            elif child.name == 'gram-g':
                pass
            elif child.name == 'gram':
                pass
            elif child.name == 'geo':   # geographic
                pass
            elif child.name == 'ptl':
                pass
            elif child.name == 'subj':
                pass
            elif child.name == 'pv-gs':
                # phrasal verbs
                pass
            elif child.name == 'pv-g':
                # phrasal verbs
                newTagName = "div"
            elif child.name == 'h-l':
                # see -able, "-able, -ible"
                newTagName = "div"
            elif child.name == "use":
                # see -able, "in adjectives"
                pass
            elif child.name == 'or':
                # see abide, "old use or formal"
                removeChild = True
            elif child.name == 'collapse':
                # verb forms heading collapse/expand
                pass
            elif child.name == 'pnc_heading':
                # verb forms heading
                pass
            elif child.name == 'pvp-g':
                # can't find example
                pass
            elif child.name == 'cf':
                # see "acclaim"
                pass
            elif child.name == 'exp':
                # see "acclaim"
                pass
            elif child.name == 'sub':
                # see "acetylene", chemical element symbol subscript
                pass
            elif child.name == 'pv':
                # see phrasal verb "add in"
                newTagName = "h4"
            elif child.name == 'pv-l':
                # appears in phrasal verb "add up" but found no example on web
                pass
            elif child.name == 'z':
                # see phrasal verb "add up"
                pass
            elif child.name == 'hm':
                # see "agape", superscript for words of different meanings
                removeChild = True
            elif child.name == 'audio':
                removeChild = True
            elif child.name == 'topic':
                # see "aardvark"
                removeChild = True
            elif child.name == 'infl-g':
                removeChild = True
            elif child.name == 'cset':
                removeChild = True
            elif child.name == 'pracpron':
                removeChild = True
            elif child.name == 'aref':
                removeChild = True
            elif child.name == 'lg:tabbed':
                removeChild = True
            else:
                AddLog(f"Unexpected tag '{child.name}' in {elem.name} of block {self._curBlockNum}")
                removeChild = True
            if removeChild:
                child.decompose()
            else:
                self._ParseConvertElem(child, newTagName)

    def _ConvertEntry(self, entry):
        #hgs = entry.findAll('h-g')
        hgsCount = 0
        for nn in range(len(entry.contents)-1, -1, -1):
            child = entry.contents[nn]
            if (child.name is None):
                continue
            if (child.name == 'guide_info'):
                child.decompose()
            elif child.name == 'h-g':
                hgsCount += 1
                self._ParseConvertElem(child, "ol")
            else:
                AddLog(f"Unexpected tag '{child.name}' in entry of block {self._curBlockNum}")
                continue
        if hgsCount != 1:
            AddLog(f"Found {hgsCount} h-g in block {self._curBlockNum}")
        return hgsCount == 1
        
    def ConvertBlock(self, block):
        self._curBlockNum = block['num']
        #print(str(block))
        entriesCount = 0
        # in case we miss anything else, use for loop instead
        #entries = block.findAll('entry')
        #entriesCount = len(entries)
        for nn in range(len(block.contents)-1, -1, -1):
            child = block.contents[nn]
            if (child.name is None):
                continue
            if (child.name == 'link'):
                child.decompose()
            elif child.name == 'entry':
                entriesCount += 1
                self._ConvertEntry(child)
            else:
                AddLog(f"Unexpected tag '{child.name}' in block {self._curBlockNum}")
                continue
        if entriesCount > 1:
            AddLog(f"Found {entriesCount} entries in block {self._curBlockNum}")
    
    def Convert(self, contents, fileOut):
        self._bsOut = BeautifulSoup(contents, inputParser)
        with open(fileOut, mode="w", encoding="utf-8") as fOutput:
            for block in self._bsOut.findAll("lg:block"):
                self.ConvertBlock(block)
            head = self._bsOut.new_tag("head")
            meta = self._bsOut.new_tag("meta")
            linkInterfaceCSS = self._bsOut.new_tag("link")
            linkOxfordCSS = self._bsOut.new_tag("link")
            linkInterfaceCSS['rel'] = 'stylesheet'
            linkInterfaceCSS['type'] = 'text/css'
            linkInterfaceCSS['href'] = interfaceCSS.replace('\\', '/')
            linkOxfordCSS['rel'] = 'stylesheet'
            linkOxfordCSS['type'] = 'text/css'
            linkOxfordCSS['href'] = oxfordCSS.replace('\\', '/')
            meta['charset'] = 'UTF-8'
            head.append(meta)
            head.append(linkInterfaceCSS)
            head.append(linkOxfordCSS)
            self._bsOut.body.insert_before(head)
            if prettyOutput:
                text = str(self._bsOut.prettify())
            else:
                text = str(self._bsOut)
            #fOutput.write(str(self._bsOut))
            text = self._EscapeSpecialText(text)
            # remove the redundant number after each list entry
            rep = re.compile(r'sn-g">\s*(\d+)')
            text = rep.sub(r'sn-g">', text)
            fOutput.write(text)

def MakeValidPath(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.mkdir(dir)
    return path

curDir = os.path.dirname(os.path.abspath(__file__))
copyfile(curDir + "\\" + interfaceCSS, MakeValidPath(outputDir + "\\" + interfaceCSS))
copyfile(curDir + "\\" + oxfordCSS, MakeValidPath(outputDir + "\\" + oxfordCSS))

fileCount = 0
if not os.path.exists(outputDir):
    os.mkdir(outputDir)
fList = glob.glob(inputDir + '/*.xml')
totalFileCount = len(fList)
for file in fList:
    with open(file) as fInput:
        fileCount += 1
        curFileName = os.path.basename(file)
        os.system(f"title Parsing {curFileName} ({fileCount}/{totalFileCount}) {float(fileCount)/totalFileCount*100:.1f}%")
        curInputFile = file
        #print(f'File {fileCount}: {file}')
        contents = fInput.read()
        parser = OALDEntryParser()
        fileOut = outputDir + "\\" + curFileName + ".html"
        parser.Convert(contents, fileOut)



