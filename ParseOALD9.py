# OALD9 DVD for Windows XML Parser
# 4/8/2019

import os
import glob
from bs4 import BeautifulSoup
#import html5lib
import lxml

#inputParser = "html5lib"
inputParser = "lxml"
outputParser = "lxml"
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
        self.result = ""
        self._curBlockNum = 0
        self._bsOut = BeautifulSoup(features=outputParser)
    
    def _AddOutputElemEx(self, out_container, tag, class_name = ""):
        if out_container is None:
            print(f"invalid out_container for tag {tag} class {class_name}!")
            return None
        newElem = self._bsOut.new_tag(tag)
        if class_name:
            newElem['class'] = class_name
        out_container.append(newElem)
        return newElem

    def _ParseAddOutputElem(self, elem, out_container, tagName, useClassName = True):
        newElem = self._AddOutputElemEx(out_container, tagName, elem.name if useClassName else "")
        if elem.string is not None:
            newElem.string = elem.string
        newContainer = newElem
        newTagName = "span"
        for child in elem.children:
            if child.name == 'span':
                newTagName = "span"
            elif child.name == 'img':
                newElem = self._AddOutputElemEx(newContainer, child.name)
                newElem.attrs = child.attrs
                continue
            elif child.name == 'top-g':
                top_container = self._AddOutputElemEx(newContainer, 'div', 'top-container')
                newContainer = top_container
            elif child.name == 'sn-gs':
                #todo
                continue
            elif child.name == 'idm-gs':
                #todo
                continue
            elif child.name == 'res-g':
                #todo
                continue
            elif child.name == 'x-gs':
                newTagName = "span"
            elif child.name == 'x-g':
                newTagName = "span"
            elif child.name == 'x':
                newTagName = "span"
            elif child.name == 'h':
                newTagName = "h2"
            elif child.name == 'pos-g':
                newTagName = "span"
            elif child.name == 'pos':
                newTagName = "span"
            elif child.name == 'pron-gs':
                newTagName = "div"
            elif child.name == 'pron-g':
                newTagName = "span"
            elif (child.name == 'blue') or (child.name == 'red'):
                newTagName = "span"
            elif child.name == 'phon':
                newTagName = "span"
            elif child.name == 'v-gs':
                newTagName = "span"
            elif child.name == 'v-g':
                newTagName = "span"
            elif child.name == 'v':
                newContainer = self._AddOutputElemEx(newContainer, 'span', child.name)
                newTagName = "strong"
                useClassName = False
            elif child.name == 'st':
                newTagName = "span"
            elif child.name == 'if-gs':
                newTagName = "span"
            elif child.name == 'if-g':
                newTagName = "span"
            elif child.name == 'if':
                newTagName = "span"
            elif child.name == 'un':
                newTagName = "span"
            elif child.name == 'eb':
                newTagName = "span"
            elif child.name == 'label-g':
                newTagName = "span"
            elif child.name == 'reg':
                newTagName = "span"
            elif child.name == 'gram-g':
                newTagName = "span"
            elif child.name == 'gram':
                newTagName = "span"
            elif child.name == 'geo':   # geographic
                newTagName = "span"
            elif child.name == 'ptl':
                newTagName = "span"
            elif child.name == 'subj':
                newTagName = "span"
            elif child.name == 'pv-gs':
                # phrasal verbs
                newTagName = "span"
            elif child.name == 'pv-g':
                # phrasal verbs
                newTagName = "div"
            elif child.name == 'h-l':
                # see -able, "-able, -ible"
                newTagName = "div"
            elif child.name == "use":
                # see -able, "in adjectives"
                newTagName = "span"
            elif child.name == 'or':
                # see abide, "old use or formal"
                continue
            elif child.name == 'collapse':
                # verb forms heading collapse/expand
                newTagName = "span"
            elif child.name == 'pnc_heading':
                # verb forms heading
                continue
            elif child.name == 'pvp-g':
                # can't find example
                newTagName = "div"
            elif child.name == 'cf':
                # see "acclaim"
                newTagName = "span"
            elif child.name == 'exp':
                # see "acclaim"
                newTagName = "span"
            elif child.name == 'sub':
                # see "acetylene", chemical element symbol subscript
                newTagName = "span"
            elif child.name == 'pv':
                # see phrasal verb "add in"
                newTagName = "h4"
            elif child.name == 'pv-l':
                # appears in phrasal verb "add up" but found no example on web
                newTagName = "div"
            elif child.name == 'z':
                # see phrasal verb "add up"
                newTagName = "span"
            elif child.name == 'hm':
                # see "agape", superscript for words of different meanings
                continue
            elif child.name == 'infl-g':
                continue
            elif child.name == 'cset':
                continue
            elif child.name == 'pracpron':
                continue
            elif child.name == 'aref':
                continue
            elif child.name == 'lg:tabbed':
                continue
            elif child.name is None:
                continue
            else:
                AddLog(f"Unexpected tag '{child.name}' in {elem.name} of block {self._curBlockNum}")
                continue
            self._ParseAddOutputElem(child, newContainer, newTagName, useClassName)
        return newElem

    def _ParseEntry(self, entry):
        #hgs = entry.findAll('h-g')
        hgsCount = 0
        for child in entry.children:
            if (child.name == 'guide_info') or (child.name is None):
                continue
            elif child.name == 'h-g':
                hgsCount += 1
                self._ParseAddOutputElem(child, self._bsOut, "ol")
            else:
                AddLog(f"Unexpected tag '{child.name}' in entry of block {self._curBlockNum}")
                continue
        if hgsCount != 1:
            AddLog(f"Found {hgsCount} h-g in block {self._curBlockNum}")
        return hgsCount == 1
        
    def Convert(self, block):
        self._curBlockNum = block['num']
        #print(str(block))
        entriesCount = 0
        self.result = ""
        # in case we miss anything else, use for loop instead
        #entries = block.findAll('entry')
        #entriesCount = len(entries)
        for child in block.children:
            if (child.name == 'link') or (child.name is None):
                continue
            elif child.name == 'entry':
                entriesCount += 1
                self._ParseEntry(child)
            else:
                AddLog(f"Unexpected tag '{child.name}' in block {self._curBlockNum}")
                continue
        if entriesCount != 1:
            AddLog(f"Found {entriesCount} entries in block {self._curBlockNum}")
        self.result = str(self._bsOut)
        return entriesCount == 1


fileCount = 0
if not os.path.exists(outputDir):
    os.mkdir(outputDir)
fList = glob.glob(inputDir + '/*.xml')
totalFileCount = len(fList)
for file in fList:
    with open(file) as fInput:
        fileCount += 1
        os.system(f"title Parsing {os.path.basename(file)} progress {float(fileCount)/totalFileCount*100:.1f}%")
        curInputFile = file
        #print(f'File {fileCount}: {file}')
        contents = fInput.read()
        soup = BeautifulSoup(contents, inputParser)
        with open(outputDir + "\\" + os.path.basename(file), "w") as fOutput:
            for block in soup.findAll("lg:block"):
                if len(block.contents) > 0:
                    parser = OALDEntryParser()
                    if parser.Convert(block):
                        fOutput.write(parser.result)
                        continue

