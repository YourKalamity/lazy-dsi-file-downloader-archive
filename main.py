
import tkinter 
from tkinter import messagebox
from tkinter import filedialog
import os
import platform
import sys
import requests
import json
from pathlib import Path
import shutil
from subprocess import Popen
import zipfile

dsiVersions = ["1.0 - 1.3 (USA, EUR, AUS, JPN)", "1.4 - 1.4.5 (USA, EUR, AUS, JPN)", "All versions (KOR, CHN)"]
memoryPitLinks = ["https://github.com/YourKalamity/just-a-dsi-cfw-installer/raw/master/assets/files/memoryPit/256/pit.bin","https://github.com/YourKalamity/just-a-dsi-cfw-installer/raw/master/assets/files/memoryPit/768_1024/pit.bin"]

window = tkinter.Tk()
window.sourceFolder = ''
window.sourceFile = ''
appTitle = tkinter.Label(text="Lazy DSi file downloader")
appTitle.width = 100
SDlabel = tkinter.Label(text = "SD card directory")
SDlabel.width = 100
SDentry = tkinter.Entry()
SDentry.width = 100

def getLatestTWLmenu():
    release = json.loads(requests.get("https://api.github.com/repos/DS-Homebrew/TWiLightMenu/releases/latest").content)
    url = release["assets"][0]["browser_download_url"]
    return url

def getLatestdumpTool():
    release = json.loads(requests.get("https://api.github.com/repos/zoogie/dumpTool/releases/latest").content)
    url = release["assets"][0]["browser_download_url"]
    return url

def outputbox(message):
    outputBox.configure(state='normal')
    outputBox.insert('end', message)
    outputBox.configure(state='disabled')

def validateDirectory(directory):
        try:
            directory = str(directory)
        except TypeError:
            outputbox("That's not a valid directory")
            return False
        try:
            string = directory + "/test.file"
            with open(string, 'w') as file:
                file.close()
            os.remove(string)
        except FileNotFoundError:
            outputbox("That's not a valid directory")
            outputbox(" or you do not have the")
            outputbox(" permission to write there")
            return False
        except PermissionError:
            outputbox("You do not have write")
            outputbox(" access  to that folder")
            return False
        else:
            return True

def start():
    outputBox.delete(0, tkinter.END)
    sysname = platform.system()
    _7za = os.path.join(sysname, '7za')
    _7z = None
    if sysname == "Windows":
        from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_64KEY
        print('Searching for 7-Zip in the Windows registry...')

        try:
            with OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\7-Zip', 0, KEY_READ | KEY_WOW64_64KEY) as hkey:
                _7z = os.path.join(QueryValueEx(hkey, 'Path')[0], '7z.exe')

                if not os.path.exists(_7z):
                    raise WindowsError
                
                _7za = _7z
        except WindowsError:
            print('Searching for 7-Zip in the 32-bit Windows registry...')

            try:
                with OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\7-Zip') as hkey:
                    _7z = os.path.join(QueryValueEx(hkey, 'Path')[0], '7z.exe')

                    if not os.path.exists(_7z):
                        raise WindowsError

                    _7za = _7z
            except WindowsError:
                print("7-Zip not found, please install it before using")
                outputbox("7-Zip not found")
                return
    print("7-Zip found!")
    outputBox.configure(state='normal')
    outputBox.delete('1.0', tkinter.END)
    outputBox.configure(state='disabled')
    #Variables
    directory = SDentry.get()
    version = firmwareVersion.get()
    unlaunchNeeded = unlaunch.get()
    
    directoryValidated = validateDirectory(directory)
    if directoryValidated == False:
        return
    if dsiVersions.index(version) == 1:
        memoryPitDownload = memoryPitLinks[1]
    elif dsiVersions.index(version) in [0,2]:
        memoryPitDownload = memoryPitLinks[0]

    temp = directory + "/tmp/"
    Path(temp).mkdir(parents=True,exist_ok=True)

    #Download Memory Pit
    memoryPitLocation = directory + "/private/ds/app/484E494A/"
    Path(memoryPitLocation).mkdir(parents=True, exist_ok=True)
    r = requests.get(memoryPitDownload, allow_redirects=True)
    memoryPitLocation = memoryPitLocation + "pit.bin"
    open(memoryPitLocation, 'wb').write(r.content)
    outputbox("Memory Pit Downloaded          ")

    #Download TWiLight Menu
    r = requests.get(getLatestTWLmenu(), allow_redirects=True)
    TWLmenuLocation = temp + "TWiLightMenu.7z"
    open(TWLmenuLocation,'wb').write(r.content)
    outputbox("TWiLight Menu ++ Downloaded    ")

    #Extract TWiLight Menu
    proc = Popen([ _7za, 'x', TWLmenuLocation, '-o' + temp, '_nds', 'DSi - CFW users',
                'DSi&3DS - SD card users', 'roms' ])
    ret_val = proc.wait()

    while True:
        if ret_val  == 0:
            outputbox("TWiLight Menu ++ Extracted     ")
            break
        else:
            continue

    #Move TWiLight Menu
    shutil.copy(temp + "DSi&3DS - SD card users/BOOT.NDS", directory)
    shutil.move(temp + "_nds/" , directory) 
    shutil.move(temp + "DSi - CFW users/SDNAND root/hiya", directory)
    shutil.move(temp + "DSi - CFW users/SDNAND root/title", directory)
    shutil.copy(temp + "DSi&3DS - SD card users/_nds/nds-bootstrap-hb-nightly.nds", directory + "/_nds")
    shutil.copy(temp + "DSi&3DS - SD card users/_nds/nds-bootstrap-hb-release.nds", directory + "/_nds")
    outputbox("TWiLight Menu ++ placed        ")

    #Download dumpTool
    r = requests.get(getLatestdumpTool(), allow_redirects=True)
    dumpToolLocation = directory + "/dumpTool.nds"
    open(dumpToolLocation,'wb').write(r.content)
    outputbox("dumpTool Downloaded            ")

    if unlaunchNeeded == 1 :
        #Download Unlaunch
        url = "https://problemkaputt.de/unlaunch.zip"
        r = requests.get(url, allow_redirects=True)
        unlaunchLocation = temp + "unlaunch.zip"
        open(unlaunchLocation,'wb').write(r.content)
        outputbox("Unlaunch Downloaded            ")

        #Extract Unlaunch
        with zipfile.ZipFile(unlaunchLocation, 'r') as zip_ref:
            zip_ref.extractall(directory)
            zip_ref.close()
        
    
        #Delete tmp folder
        shutil.rmtree(directory + '/tmp')

        outputbox("Done!")
        
        
def chooseDir():
    window.sourceFolder =  filedialog.askdirectory(parent=window, initialdir= "/", title='Please select the directory of your SD card')
    SDentry.delete(0, tkinter.END)
    SDentry.insert(0, window.sourceFolder)


b_chooseDir = tkinter.Button(window, text = "Choose Folder", width = 20, command = chooseDir)
b_chooseDir.width = 100
b_chooseDir.height = 50

firmwareLabel = tkinter.Label(text = "Select your DSi firmware")
firmwareLabel.width = 100

firmwareVersion = tkinter.StringVar(window)
firmwareVersion.set(dsiVersions[0])
selector = tkinter.OptionMenu(window, firmwareVersion, *dsiVersions)
selector.width = 100

unlaunch = tkinter.IntVar(value=1)
unlaunchCheck = tkinter.Checkbutton(window, text = "Download Unlaunch?", variable =unlaunch)

startButton = tkinter.Button(window, text = "Start", width = 20, command = start)
outputLabel = tkinter.Label(text="Output")
outputLabel.width = 100
outputBox = tkinter.Text(window,state='disabled', width = 30, height = 10)

window.title("Lazy DSi file downloader")
window.resizable(0, 0)
appTitle.pack()
SDlabel.pack()
SDentry.pack()
b_chooseDir.pack()
firmwareLabel.pack()
selector.pack()
unlaunchCheck.pack()
startButton.pack()
outputLabel.pack()
outputBox.pack()
window.mainloop()

