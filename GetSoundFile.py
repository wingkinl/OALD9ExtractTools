import os
import os.path
import time
import urllib.request

desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
customDir = desktop + "\\OALD9\\"
soundlistfile = customDir + 'soundfile.txt'

soundDir = customDir + 'sound_download\\'
downloadProgressFile = customDir + 'soundProgress.txt'
startProgress = 0

if os.path.exists(downloadProgressFile):
    with open(downloadProgressFile) as f:
        content = f.read()
        if content:
            startProgress = int(content)

if not os.path.exists(soundDir):
    os.mkdir(soundDir)

#  a#_gb_2
#  uk_pron/a/a__/a__gb/a__gb_2.mp3
#  uk_pron_ogg/a/a__/a__gb/a__gb_2.ogg
# sample:
#  https://www.oxfordlearnersdictionaries.com/media/english/uk_pron_ogg/e/eas/east_/east__gb_1.ogg

UrlUKBase = r'https://www.oxfordlearnersdictionaries.com/media/english/uk_pron_ogg/'
UrlUSBase = r'https://www.oxfordlearnersdictionaries.com/media/english/us_pron_ogg/'

with open(soundlistfile) as f:
    content = f.readlines()
    content = [x.strip() for x in content]
    totalFileCount = len(content)
    for progress in range(startProgress, totalFileCount):
        line = content[progress]
        sep = line.find('#')
        if sep < 0:
            print(f'cannot find # in {line}')
            continue
        isUS = line.find('us', sep) >= 0
        fname = line.replace('#', '_')
        fpath = fname[0] + '/' + f'{fname[0:3]:_<3}' + '/' + f'{fname[0:5]:_<5}' + '/' + fname + '.ogg'
        urlbase = UrlUSBase if isUS else UrlUKBase
        url = urlbase + fpath
        soundFilePath = soundDir + fname + '.ogg'
        fileCount = progress + 1
        os.system(f"title Downloading ({fileCount}/{totalFileCount}) {float(fileCount)/totalFileCount*100:.1f}% {fname}")
        if os.path.isfile(soundFilePath):
            continue
        try:
            urllib.request.urlretrieve(url, soundFilePath)
            with open(downloadProgressFile, 'w') as f:
                startProgress = progress
                f.write(str(startProgress))
        except:
            print(f"Failed to download {line}")
        time.sleep(0.1)
