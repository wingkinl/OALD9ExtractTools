# OALD9 DVD for Windows XML Parser
# 4/8/2019

import os
import glob
from bs4 import BeautifulSoup
#import html5lib
import lxml
import copy

#inputParser = "html5lib"
inputParser = "lxml"
inputDir = r"C:\OALD9_Out"
outputDir = r"C:\OALD9_Final"
logFile = r"OALD9ParserLog.txt"
curInputFile = ""

def AddLog(text):
    text = curInputFile + ": " + text
    print(text)
    #with open(logFile, "a") as file:
    #    file.write(text)

class OALDEntryParser:
    def __init__(self):
        self._curBlockNum = 0
    
    def _AddOutputElemEx(self, container, tag, class_name = ""):
        if container is None:
            print(f"invalid container for tag {tag} class {class_name}!")
            return None
        newElem = self._bsOut.new_tag(tag)
        if class_name:
            newElem['class'] = class_name
        container.append(newElem)
        return newElem

    def _ParseConvertElem(self, elem, tagName):
        if elem.attrs:
            elem.attrs.clear()
        if elem.name == "ref":
            elem['href'] = f"entry://{elem.string}"
        if (elem.name != tagName):
            elem['class'] = elem.name
            elem.name = tagName
        for nn in range(len(elem.contents)-1, -1, -1):
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
                newElem.append(copy.copy(child))
                child.replace_with(newElem)
                continue
            elif child.name == 'sn-gs':
                pass
            elif child.name == 'sn-g':
                newTagName = "li"
            elif child.name == 'def':
                pass
            elif child.name == 'ndv':
                # see "A noun", in the [scale] of C
                pass
            elif child.name == 'cl':
                # see "A noun", [A in/for] Biology
                # TODO, set as "strong" in CSS
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
                # TODO make text capitalize in CSS
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
                # TODO, wrap, see "abbreviated"
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
                pass
            elif child.name == 'phon':
                pass
            elif child.name == 'v-gs':
                # TODO, wrap
                pass
            elif child.name == 'v-g':
                pass
            elif child.name == 'v':
                # TODO make text capitalize in CSS
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
        with open(fileOut, "w") as fOutput:
            for block in self._bsOut.findAll("lg:block"):
                self.ConvertBlock(block)
            fOutput.write(str(self._bsOut))

fileCount = 0
if not os.path.exists(outputDir):
    os.mkdir(outputDir)
fList = glob.glob(inputDir + '/*.xml')
totalFileCount = len(fList)
for file in fList:
    with open(file) as fInput:
        fileCount += 1
        fileName = os.path.basename(file)
        os.system(f"title Parsing {fileName} ({fileCount}/{totalFileCount}) {float(fileCount)/totalFileCount*100:.1f}%")
        curInputFile = file
        #print(f'File {fileCount}: {file}')
        contents = fInput.read()
        parser = OALDEntryParser()
        fileOut = outputDir + "\\" + fileName + ".html"
        parser.Convert(contents, fileOut)



