# OALD9 DVD for Windows XML Parser
# 4/9/2019

import os
import re
import time
import os.path
#import requests
import urllib.request
import shutil
from shutil import copyfile
from distutils.dir_util import copy_tree
import glob
from bs4 import BeautifulSoup
#import html5lib
import lxml
import copy
import configparser
import warnings
import traceback

#inputParser = "html5lib"
inputParser = "lxml"
inputDir = r"C:\OALD9_Out"
outputDir = r"C:\OALD9_Final"
curInputFile = ""
# source https://www.oxfordlearnersdictionaries.com/external/styles/interface.css?version=1.6.51
interfaceCSS = r'styles\interface.css'
# source: https://www.oxfordlearnersdictionaries.com/external/styles/oxford.css?version=1.6.51
oxfordCSS = r'styles\oxford.css'
entryJS = r'scripts\entry.js'
prettyOutput = True
debugPrintMsg = False
addMsgLogFile = True
parseOnlyNoOutput = False
getSoundFileList = True

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
if config.has_option('Parser', 'parseOnlyNoOutput'):
    value = config['Parser']['parseOnlyNoOutput'].lower()
    parseOnlyNoOutput = value in ['true', '1']
if config.has_option('Parser', 'getSoundFileList'):
    value = config['Parser']['getSoundFileList'].lower()
    getSoundFileList = value in ['true', '1']

globalImgList = set()
globalSoundFileList = set()

def MakeValidPath(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.mkdir(dir)
    return path

if addMsgLogFile:
    MakeValidPath(logFile)

def AddLog(text):
    text = curInputFile + ": " + text
    if debugPrintMsg:
        print(text)
    if addMsgLogFile:
        try:
            with open(logFile, "a") as file:
                file.write(text + "\n")
        except:
            pass


class OALDEntryParser:
    def __init__(self):
        self._curBlockNum = 0
    
    def _ReplaceSpecialSymbol(self, mo):
        if mo.group(1) == '@':
            at_map = {
                'A' : r'\u00C6',  # Æ
                'a' : r'\u00E6',  # æ
                'd' : r'\u00F0',  # ð
                'n' : r'\u014B',  # ŋ
                'o' : r'\u0153',  # œ, see cri de cœur
                'y' : r'\u00FE',  # þ
            }
            return at_map[mo.group(2)]
        elif mo.group(1) == 'g':  # greek alphabet
            g_map = {
                'C' : r'\u0393',  # Γ, see gamma
                'D' : r'\u0394',  # α, see delta
                'H' : r'\u0398',  # Θ, see theta
                'L' : r'\u039B',  # Λ, see lambda
                'P' : r'\u03A0',  # Π, see pi
                'Q' : r'\u039E',  # Ξ, see xi
                'S' : r'\u03A3',  # Σ, see sigma
                'V' : r'\u03A6',  # Φ, see phi
                'Y' : r'\u03A8',  # Φ, see psi
                'Z' : r'\u03A9',  # Ω, see omega
                'a' : r'\u03B1',  # α
                'b' : r'\u03B2',  # β
                'c' : r'\u03B3',  # γ, see caribou
                'd' : r'\u03B4',  # δ, see delta
                'f' : r'\u03B6',  # ζ, see zeta
                'g' : r'\u03B7',  # η, see eta
                'h' : r'\u03B8',  # θ, see theta
                'i' : r'\u03B9',  # ι, see iota
                'k' : r'\u03BA',  # κ, see aphid
                'l' : r'\u03BB',  # λ, see lambda
                'm' : r'\u03BC',  # μ, see microgram
                'n' : r'\u03BD',  # ν, see nu
                'p' : r'\u03C0',  # π, see 'irrational number'
                'q' : r'\u03BE',  # ξ, see equation
                'r' : r'\u03C1',  # ρ, see aphid
                's' : r'\u03C3',  # σ, see sigma
                't' : r'\u03C4',  # τ, see tau
                'u' : r'\u03C5',  # υ, see upsilon
                'x' : r'\u03C7',  # χ, see chi
                'y' : r'\u03C8',  # ψ, see psi
                'z' : r'\u03C9',  # ω, see omega
            }
            return g_map[mo.group(2)]
        elif mo.group(1) == 's':
            s_map = {
                '1' : r'\u00AE',  # ®, see google
                '2' : r'\u00B0',  # °
                'a' : r'\u201A',  # ‚
                'c' : r'\u2026',  # …
                'h' : r'\u2018',  # ‘
                'i' : r'\u2019',  # ’
                'j' : r'\u201C',  # “
                'k' : r'\u201D',  # ”
                'm' : r'\u2013',  # –
                'n' : r'\u2014',  # —
                'o' : r'\u2122',  # ™
                'q' : r'\u00A1',  # ¡, see Hello!
                'r' : r'\u00A2',  # ¢, see dollar
                's' : r'\u00A3',  # £
                'x' : r'\u00A9',  # ©, see C abbreviation
                'D' : r'\u00B7',  # ·
                'H' : r'\u00BC',  # ¼, see mixed number
                'I' : r'\u00BD',  # ½, see bit
                'J' : r'\u00BE',  # ¾, see denominator
                'L' : r'\u00D7',  # ×
                'M' : r'\u00F7',  # ÷, see divide
            }
            return s_map[mo.group(2)]
        elif mo.group(1) == '-':
            dash_map = {
                'E' : r'\u0112',  # Ē, see Easter
                'I' : r'\u012A',  # Ī, see Irish
                'a' : r'\u0101',  # ā
                'e' : r'\u0113',  # ē
                'i' : r'\u012B',  # ī
                'o' : r'\u014D',  # ō
                'u' : r'\u016B',  # ū
            }
            return dash_map[mo.group(2)]
        elif mo.group(1) == '+':
            plus_map = {
                'a' : r'\u0103',  # ă, see chow mein
                'i' : r'\u012D',  # ĭ, see beluga
                'u' : r'\u016D',  # ŭ, see tofu
            }
            return plus_map[mo.group(2)]
        elif mo.group(1) == '_':
            under_map = {
                'l' : r'\u0142',  # ł, see bialy
                'o' : r'\u00F8',  # ø, see bilberry
            }
            return under_map[mo.group(2)]
        elif mo.group(1) == ':':
            colon_map = {
                'A' : r'\u00C4',  # Ä, see ear
                'U' : r'\u00DC',  # Ü, see evil
                'a' : r'\u00E4',  # ä, see aspirin
                'e' : r'\u00EB',  # ë, see Beelzebub
                'i' : r'\u00EF',  # ï
                'o' : r'\u00F6',  # ö, see antibody
                'u' : r'\u00FC',  # ü, see boob
            }
            return colon_map[mo.group(2)]
        elif mo.group(1) == '^':
            a_map = {
                'A' : r'\u00C2',  # Â, see deficit
                'a' : r'\u00E2',  # â, see baton
                'e' : r'\u00EA',  # ê, see arête
                'g' : r'\u011D',  # ĝ, see toboggan
                'i' : r'\u00EE',  # î, see bivouac
                'o' : r'\u00F4',  # ô
                'u' : r'\u00FB',  # û, see crème brûlée 
                'y' : r'\u0177',  # ŷ, see wood
            }
            return a_map[mo.group(2)]
        elif mo.group(1) == '`':
            a2_map = {
                'a' : r'\u00E0',  # à
                'i' : r'\u00EC',  # ì, see chop suey
                'e' : r'\u00E8',  # è, see anther
                'o' : r'\u00F2',  # ò, see Machiavellian
                'u' : r'\u00F9',  # ù, see loop
            }
            return a2_map[mo.group(2)]
        elif mo.group(1) == '~':
            a3_map = {
                'a' : r'\u00E3',  # ã, see caiman
                'i' : r'\u0129',  # ĩ, see capybara
                'n' : r'\u00F1',  # ñ, see canyon
                'u' : r'\u0169',  # ũ, see tank
            }
            return a3_map[mo.group(2)]
        elif mo.group(1) == '\'':
            a4_map = {
                'E' : r'\u00C9',  # É, see gallium
                'S' : r'\u015A',  # Ś, see Shri
                'a' : r'\u00E1',  # á, see afloat
                'e' : r'\u00E9',  # é, see academic
                'i' : r'\u00ED',  # í, see Angostura
                'n' : r'\u0144',  # ń, see origin
                'o' : r'\u00F3',  # ó, see canyon
                's' : r'\u015B',  # ś, see ashram
                'u' : r'\u00FA',  # ú, see bondage
                'y' : r'\u00FD',  # ý, see by-law
            }
            return a4_map[mo.group(2)]
        elif mo.group(1) == '.':
            dot_map = {
                'i' : r'\u0131',  # ı, see raki
            }
            return dot_map[mo.group(2)]
        return mo.group()
    
    def _EscapeSpecialText(self, text):
        #text = text.replace(r'\`a', r'\u00E0')  # à
        text = text.replace(r'\,',  r'\u00E7')  # ç
        # decode \@?, \s?
        try:
            text = re.sub(r'\\([@gs\-:\^`+_~\'\.])(.)', lambda mo: self._ReplaceSpecialSymbol(mo), text)
        except Exception as e:
            AddLog(f"failed to replace special symbol in '{curFileName}'\n\t{traceback.format_exc()}")
        
        # decode unicode text "\uXXXX"
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            text = text.encode().decode('unicode-escape')
            if len(w):
                AddLog(f"failed to replace unicode in '{curFileName}'\n\t{str(w[-1].message)}")
        return text

    def _ParseConvertElem(self, elem, tagName, attrs = ['geo','heading','ox3000']):
        if elem.attrs:
            # preserve the attributes for styling some tags
            # geo for "blue"/"red"
            attrsDict = {}
            if tagName == 'img':
                attrs.append('src')
            for attr in attrs:
                if elem.has_attr(attr):
                    attrsDict[attr] = elem[attr]
            elem.attrs.clear()
            for attrName, attrValue in attrsDict.items():
                elem[attrName] = attrValue
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
            elif child.name == 'wd':
                # the word
                pass
            elif child.name == 'span':
                pass
            elif (child.name == 'img'):
                # handles src='mbx://oup_en-dic/insects'
                if child.has_attr('src') and child['src'][0:3] == 'mbx':
                    newTagName = child.name
                    src = child['src']
                    src = src[len('mbx://oup_en-dic/'):]
                    globalImgList.add(src)
                    child['src'] = './images/fullsize/' + src + '.jpg'
                    #print(curInputFile)
                else:
                    removeChild = True
                #newTagName = child.name
                #src = child['src']
                #if src == 'skin:///xseps':
                #    child['src'] = './images/entry/entry-bullet.png'
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
            elif child.name == 'lg:sound':
                soundFileTag = child.find('lg:sound_file')
                if soundFileTag and getSoundFileList:
                    src = soundFileTag.string
                    test = r'wbx://oup_en-dic/'
                    #if src[0:len(test)] != test:
                    #    AddLog(f'unrecognized sound file {src}')
                    src = src[len(test):]
                    globalSoundFileList.add(src)
                    #print(soundFileTag.string)
                removeChild = True
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
            elif child.name == 'sc':
                # see "carpe diem"
                pass
            elif child.name == 'er':
                # see "clear"
                pass
            elif child.name == 'nil':
                # see "cheap adverb"
                pass
            elif child.name == 'frac-g':
                # see "decimalize"
                pass
            elif child.name == 'den':
                # see "decimalize"
                pass
            elif child.name == 'num':
                # see "decimalize"
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
            elif child.name == 'id':
                # see bat verb, TODO, maybe set attribute psg="tag=id"?
                pass
            elif child.name == "ei":
                # see "a indefinite article", [one] before some numbers
                pass
            elif child.name == "ebi":
                # see "George Abbott", The Boys from Syracuse
                pass
            elif child.name == "esu":
                # see "ye determiner"
                pass
            elif child.name == "ve":
                # see "almond"
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
            elif child.name == 'xhm':
                # see accept
                pass
            elif child.name == 'blockquote':
                # see "Dean Acheson"
                pass
            elif child.name == 'footer':
                # see "Dean Acheson"
                pass
            elif child.name == 'p-g':
                # see "Dean Acheson"
                # TODO, maybe add span 'wrap_open'?
                newTagName = 'div'
            elif child.name == 'sense':
                # see affect
                pass
            elif child.name == 'eph':
                # see affricate
                pass
            elif child.name == 'res-g':
                pass
            elif child.name == 'dis-g':
                pass
            elif child.name == 'sedev':
                # see bloat
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
                if child.has_attr('ox3000') and child['ox3000'] == 'y':
                    newElem = self._bsOut.new_tag('a')
                    newElem['class'] = 'oxford3000'
                    child.insert_before(newElem)
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
                if child.parent.has_attr('ox3000') and child.parent['ox3000'] == 'y':
                    newElem = self._bsOut.new_tag('a')
                    newElem['class'] = 'oxford3000'
                    child.insert_before(newElem)
            elif child.name == 'gram':
                pass
            elif child.name == 'geo':   # geographic
                pass
            elif child.name == 'ptl':
                pass
            elif child.name == 'subj':
                pass
            elif child.name == 'sup':
                # see angstrom
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
                #print(f"{str(elem)}\n--\n")
                if elem['class'] == 'body':
                    removeChild = True
                else:
                    child.name = 'heading'
            elif child.name == 'pvp-g':
                # can't find example
                pass
            elif child.name == 'cf':
                # see "acclaim"
                pass
            elif child.name == 'exp':
                # see "acclaim"
                pass
            elif child.name == 'shcut':
                # see absorb
                pass
            elif child.name == 'deadxref':
                # see absurdly
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
            elif child.name == 'n':
                # see African
                pass
            elif child.name == 'hm':
                # see "agape", superscript for words of different meanings
                removeChild = True
            elif child.name == 'hm-g':
                # see agape1 adjective
                pass
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
                #removeChild = True
                pass
            elif child.name == 'lg_tabbed_head_on':
                # word origin
                removeChild = True
            elif child.name == 'lg_tabbed_head_off':
                # word origin
                removeChild = True
            elif child.name == 'lg:tabbed':
                # word origin
                collapseCount = 0
                collapseElem = None
                for tab in child.children:
                    if tab.name == 'lg:tab':
                        for tabChild in tab.children:
                            if tabChild.name == 'collapse':
                                collapseCount = collapseCount + 1
                                collapseElem = tabChild
                if collapseCount != 1:
                    AddLog(f"lg:tabbed does not contains 1 collapse in block {self._curBlockNum}")
                    pass
                else:
                    unbox = self._bsOut.new_tag('unbox');
                    if collapseElem.unbox != None:
                        # change the original unbox as 'body'
                        collapseElem.unbox.name = 'body'
                        collapseElem.body.wrap(unbox)
                    elif collapseElem.find('vp-gs'):
                        group = collapseElem.find('vp-gs')
                        group.name = 'body'
                        group.wrap(unbox)
                    elif collapseElem.find('x-gs'): # extra examples, see abandon
                        group = collapseElem.find('x-gs')
                        body = self._bsOut.new_tag('body')
                        group.wrap(body)
                        body.wrap(unbox)
                    elif collapseElem.find('wfw-g'):  # word family, see ability
                        group = collapseElem.find('wfw-g')
                        collapseElem.name = 'body'
                        collapseElem.wrap(unbox)
                        collapseElemNew = self._bsOut.new_tag('collapse');
                        collapseElemNew['title'] = collapseElem['title']
                        collapseElem = collapseElemNew
                        unbox.wrap(collapseElem)
                    else:
                        AddLog(f"failed to find body for collapse in block {self._curBlockNum}\n{str(collapseElem)}")
                    collapseElemCopy = copy.copy(collapseElem)
                    headingElem = self._bsOut.new_tag('heading')
                    headingElem.string = collapseElemCopy['title']
                    collapseElemCopy.unbox.body.insert_before(headingElem)
                    child.replace_with(collapseElemCopy)
                    self._ParseConvertElem(collapseElemCopy, 'span')
            elif child.name == 'body':
                pass
            elif child.name == 'heading':
                pass
            elif child.name == 'lg:tab':
                # word origin, child of lg:tabbed
                pass
            elif child.name == 'zp_link':
                # word origin, child of lg:tab
                pass
            elif child.name == 'text':
                # word origin, child of zp_link
                pass
            elif child.name == 'unbox':
                # word origin, child of collapse
                pass
            elif child.name == 'etym_i':
                # word origin
                pass
            elif child.name == 'p':
                # word origin
                pass
            elif child.name == 'qt':
                # word origin
                pass
            elif child.name == 'lang':
                # word origin
                pass
            elif child.name == 'h1':
                # More Like this, see a- prefix
                pass
            elif child.name == 'h2':
                # collocations, see age
                pass
            elif child.name == 'h3':
                # Synonyms
                pass
            elif child.name == 'ul':
                # More Like this, see a- prefix
                pass
            elif child.name == 'li_mlt':
                # More Like this, see a- prefix
                pass
            elif child.name == 'tr':
                # word origin, see "aardvark"
                pass
            elif child.name == 'ff':
                # word origin, see "aardvark"
                pass
            elif child.name == 'xr':
                # word origin, see "aargh"
                pass
            elif child.name == 'li':
                # Synonyms
                pass
            elif child.name == 'vp-gs':
                # Verb Forms
                pass
            elif child.name == 'vp-g':
                # Verb Forms
                pass
            elif child.name == 'vp':
                # Verb Forms
                pass
            elif child.name == 'xg':
                # Word Origin, see "abandon"
                pass
            elif child.name == 'wfw-g':
                # Word Family, see "ability"
                pass
            elif child.name == 'wfw':
                # Word Family, see "ability"
                pass
            elif child.name == 'wfp':
                # Word Family, see "ability"
                pass
            elif child.name == 'wfo':
                # Word Family, see "ability"
                pass
            elif child.name == 'wx':
                # Grammar Point, see "able"
                pass
            elif child.name == 'dh':
                # see Aga™ noun
                pass
            elif child.name == 'def_qt':
                # see Aga™ noun
                pass
            else:
                AddLog(f"Unexpected tag '{child.name}' in {elem.name} of block {self._curBlockNum}")
                AddLog(f"{str(child)}")
                pass
            if removeChild:
                child.decompose()
            else:
                self._ParseConvertElem(child, newTagName)

    def _ConvertEntry(self, entry):
        #hgs = entry.findAll('h-g')
        hgsCount = 0
        for nn in range(len(entry.contents)-1, -1, -1):
            child = entry.contents[nn]
            removeChild = False
            newTagName = "span"
            if (child.name is None):
                continue
            if (child.name == 'guide_info'):
                removeChild = True
            elif child.name == 'h-g':
                hgsCount += 1
                newTagName = "ol"
            elif child.name == 'idm-gs':
                pass
            elif child.name == 'lg:tabbed':
                # see hardly
                pass
            else:
                AddLog(f"Unexpected tag '{child.name}' in entry of block {self._curBlockNum}")
                pass
            if removeChild:
                child.decompose()
            else:
                self._ParseConvertElem(child, newTagName)
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
        if parseOnlyNoOutput:
            for block in self._bsOut.findAll("lg:block"):
                self.ConvertBlock(block)
            return
        with open(fileOut, mode="w", encoding="utf-8") as fOutput:
            for block in self._bsOut.findAll("lg:block"):
                self.ConvertBlock(block)
            head = self._bsOut.new_tag("head")
            meta = self._bsOut.new_tag("meta")
            js = self._bsOut.new_tag("script")
            js['src'] = entryJS.replace('\\', '/')
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
            self._bsOut.body.append(js)
            if prettyOutput:
                text = str(self._bsOut.prettify())
            else:
                text = str(self._bsOut)
            # remove the redundant number after each list entry
            text = re.sub(r'(sn-g"[^>]*>)\s*(\d+)', r'\1', text)
            fOutput.write(text)


curDir = os.path.dirname(os.path.abspath(__file__))
copyfile(curDir + "\\" + interfaceCSS, MakeValidPath(outputDir + "\\" + interfaceCSS))
copyfile(curDir + "\\" + oxfordCSS, MakeValidPath(outputDir + "\\" + oxfordCSS))
copyfile(curDir + "\\" + entryJS, MakeValidPath(outputDir + "\\" + entryJS))

fileCount = 0
if not os.path.exists(outputDir):
    os.mkdir(outputDir)
fList = glob.glob(inputDir + '/*.xml')
totalFileCount = len(fList)
for file in fList:
    with open(file) as fInput:
        fileCount += 1
        curFileName = os.path.basename(file)
        os.system(f"title Parsing ({fileCount}/{totalFileCount}) {float(fileCount)/totalFileCount*100:.1f}% {curFileName}")
        curInputFile = file
        #print(f'File {fileCount}: {file}')
        try:
            contents = fInput.read()
        except Exception as e:
            AddLog(f"failed to read file {curFileName} :\n\t{traceback.format_exc()}")
            continue
        parser = OALDEntryParser()
        fileOut = outputDir + "\\" + curFileName + ".html"
        contents = parser._EscapeSpecialText(contents)
        parser.Convert(contents, fileOut)

if len(globalSoundFileList) > 0:
    with open(customDir + 'soundfile.txt', mode="w") as fSoundFileList:
        for soundFile in globalSoundFileList:
            fSoundFileList.write(soundFile + '\n')

urlbase = 'https://www.oxfordlearnersdictionaries.com/media/english/fullsize/'
imgdir = customDir + 'fullsize_download\\'

if not os.path.exists(imgdir):
    os.mkdir(imgdir)

if len(globalImgList) > 0:
    for imgfname in globalImgList:
        url = urlbase + imgfname[0] + '/' + f'{imgfname[0:3]:_<3}' + '/' + f'{imgfname[0:5]:_<5}' + '/' + imgfname + '.jpg'
        imgfpath = imgdir + imgfname + '.jpg'
        if os.path.isfile(imgfpath):
            continue
        print("img " + url)
        #img_data = requests.get(url, allow_redirects=True).content
        #with open(imgfpath, 'wb') as handler:
        #    handler.write(img_data)
        try:
            urllib.request.urlretrieve(url, imgfpath)
        except:
            AddLog(f"Failed to download {url}")
        time.sleep(1)

try:
    copy_tree(curDir + "\\images\\", outputDir + "\\images\\")
    copy_tree(imgdir, outputDir + "\\images\\fullsize\\")
except Exception as e:
    AddLog(f"failed to copy files:\n\t{traceback.format_exc()}")
