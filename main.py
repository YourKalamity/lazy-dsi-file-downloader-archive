
# Created by YourKalamity
#https://github.com/YourKalamity/lazy-dsi-file-downloader    


#Import libraries
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
import distutils
from distutils import dir_util


#Memory Pit Links - Points to GitHub repo
dsiVersions = ["1.0 - 1.3 (USA, EUR, AUS, JPN)", "1.4 - 1.4.5 (USA, EUR, AUS, JPN)", "All versions (KOR, CHN)"]
memoryPitLinks = ["https://github.com/YourKalamity/just-a-dsi-cfw-installer/raw/master/assets/files/memoryPit/256/pit.bin","https://github.com/YourKalamity/just-a-dsi-cfw-installer/raw/master/assets/files/memoryPit/768_1024/pit.bin"]

#Get link of latest pkmn-chest
def getLatestPKMNchest():
    release = json.loads(requests.get("https://api.github.com/repos/Universal-Team/pkmn-chest/releases/latest").content)
    url = release["assets"][1]["browser_download_url"]
    return url

#Get link of latest DSEins
def getLatestDSEins():
    release = json.loads(requests.get("https://api.github.com/repos/Universal-Team/3DEins/releases/latest").content)
    url = release["assets"][2]["browser_download_url"]
    return url

#Get link of latest Tic-Tac-DS
def getLatestTicTacDS():
    release = json.loads(requests.get("https://api.github.com/repos/Jonatan6/Tic-Tac-DS/releases/latest").content)
    url = release["assets"][0]["browser_download_url"]
    return url

#Get link of latest Relaunch
def getLatestRelaunch():
    release = json.loads(requests.get("https://api.github.com/repos/Universal-Team/Relaunch/releases/latest").content)
    url = release["assets"][0]["browser_download_url"]
    return url

#Get link of latest TWiLight Menu
def getLatestTWLmenu():
    release = json.loads(requests.get("https://api.github.com/repos/DS-Homebrew/TWiLightMenu/releases/latest").content)
    url = release["assets"][0]["browser_download_url"]
    return url

#Get link of latest dumpTool
def getLatestdumpTool():
    release = json.loads(requests.get("https://api.github.com/repos/zoogie/dumpTool/releases/latest").content)
    url = release["assets"][0]["browser_download_url"]
    return url

#Push text to output box
def outputbox(message):
    outputBox.configure(state='normal')
    outputBox.insert('end', message)
    outputBox.configure(state='disabled')

#Check if directory exists and has write permissions
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
    #Locate 7z binary
    _7za = os.path.join(sysname, '7za')
    _7z = None
    if sysname in ["Darwin", "Linux"]:
            #Chmod 7z binary to avoid a permission error
            import stat
            os.chmod(_7za, stat.S_IRWXU)
    if sysname == "Windows":
        #Search for 7z in the 64-bit Windows Registry
        from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_64KEY
        print('Searching for 7-Zip in the Windows registry...')

        try:
            with OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\7-Zip', 0, KEY_READ | KEY_WOW64_64KEY) as hkey:
                _7z = os.path.join(QueryValueEx(hkey, 'Path')[0], '7z.exe')

                if not os.path.exists(_7z):
                    raise WindowsError
                
                _7za = _7z
        except WindowsError:
            #Search for 7z in the 32-bit Windows Registry
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

    #Clear outputBox
    outputBox.configure(state='normal')
    outputBox.delete('1.0', tkinter.END)
    outputBox.configure(state='disabled')
    
    #Variables
    directory = SDentry.get()
    version = firmwareVersion.get()
    unlaunchNeeded = unlaunch.get()

    #Validate directory
    directoryValidated = validateDirectory(directory)
    if directoryValidated == False:
        return
    if dsiVersions.index(version) == 1:
        memoryPitDownload = memoryPitLinks[1]
    elif dsiVersions.index(version) in [0,2]:
        memoryPitDownload = memoryPitLinks[0]

    #Creates a path called "/lazy-dsi-file-downloader-tmp/" if it does not exist
    cwdtemp = os.getcwd() + "/lazy-dsi-file-downloader-tmp/"
    Path(cwdtemp).mkdir(parents=True,exist_ok=True)

    if downloadmemorypit.get() == 1:
        #Download Memory Pit
        memoryPitLocation = directory + "/private/ds/app/484E494A/"
        Path(memoryPitLocation).mkdir(parents=True, exist_ok=True)
        r = requests.get(memoryPitDownload, allow_redirects=True)
        memoryPitLocation = memoryPitLocation + "pit.bin"
        open(memoryPitLocation, 'wb').write(r.content)
        outputbox("Memory Pit Downloaded          ")
        print("Memory Pit Downloaded")

    if downloadtwlmenu.get() == 1:
        #Download TWiLight Menu
        r = requests.get(getLatestTWLmenu(), allow_redirects=True)
        TWLmenuLocation = cwdtemp + "TWiLightMenu.7z"
        open(TWLmenuLocation,'wb').write(r.content)
        outputbox("TWiLight Menu ++ Downloaded    ")
        print("TWiLight Menu ++ Downloaded")

        #Extract TWiLight Menu
        proc = Popen([_7za,"x", "-aoa", TWLmenuLocation, '-o'+cwdtemp, 'DSi - CFW users/SDNAND root/', '_nds', 'DSi&3DS - SD card users', 'roms', 'BOOT.NDS'])
        ret_val = proc.wait()

        while True:
            if ret_val  == 0:
                    outputbox("TWiLight Menu ++ Extracted     ")
                    print("TWiLight Menu ++ Extracted to", cwdtemp)
                    break

        #Move TWiLight Menu
        shutil.copy(cwdtemp + "DSi&3DS - SD card users/BOOT.NDS", directory)
        distutils.dir_util.copy_tree(cwdtemp + "_nds/" , directory +"/_nds/") 
        distutils.dir_util.copy_tree(cwdtemp + "DSi - CFW users/SDNAND root/hiya", directory+"/hiya/")
        distutils.dir_util.copy_tree(cwdtemp + "DSi - CFW users/SDNAND root/title", directory+"/title/")
        shutil.copy(cwdtemp + "DSi&3DS - SD card users/_nds/nds-bootstrap-hb-nightly.nds", directory + "/_nds")
        shutil.copy(cwdtemp + "DSi&3DS - SD card users/_nds/nds-bootstrap-hb-release.nds", directory + "/_nds")
        Path(directory + "/roms/").mkdir(parents=True,exist_ok=True)
        print("TWiLight  Menu ++ placed in", directory)
        outputbox("TWiLight Menu ++ placed        ")
        
        #Download DeadSkullzJr's Cheat Database
        Path(directory + "/_nds/TWiLightMenu/extras/").mkdir(parents=True,exist_ok=True)
        r = requests.get('https://bitbucket.org/DeadSkullzJr/nds-cheat-databases/raw/933c375545d3ff90854d1e210dcf4b3b31d9d585/Cheats/usrcheat.dat', allow_redirects=True)
        downloadLocation = directory + "/_nds/TWiLightMenu/extras/usrcheat.dat"
        open(downloadLocation,'wb').write(r.content)
        print("DeadSkullzJr's Cheat Database downloaded")
        

    if downloaddumptool.get() == 1:            
        #Download dumpTool
        r = requests.get(getLatestdumpTool(), allow_redirects=True)
        dumpToolLocation = directory + "/dumpTool.nds"
        open(dumpToolLocation,'wb').write(r.content)
        print("dumpTool downloaded")
        outputbox("dumpTool Downloaded            ")

    if unlaunchNeeded == 1 :
        #Download Unlaunch
        url = "https://problemkaputt.de/unlaunch.zip"
        r = requests.get(url, allow_redirects=True)
        unlaunchLocation = cwdtemp + "unlaunch.zip"
        open(unlaunchLocation,'wb').write(r.content)
        print("Unlaunch Downloaded")
        outputbox("Unlaunch Downloaded            ")

        #Extract Unlaunch
        with zipfile.ZipFile(unlaunchLocation, 'r') as zip_ref:
            zip_ref.extractall(directory)
            zip_ref.close()
        
    Path(directory +"/roms/nds/").mkdir(parents=True,exist_ok=True)
    outputbox("Downloading other homebrew     ")
    if homebrewlinks[2][0].get() == 1:
        r = requests.get(getLatestPKMNchest(), allow_redirects=True)
        downloadLocation = directory + "/roms/nds/pkmn-chest.nds"
        open(downloadLocation,'wb').write(r.content)
        print("Pokemon Chest downloaded to /roms/nds/")
        
    if homebrewlinks[2][1].get() == 1:
        r = requests.get(homebrewlinks[1][1], allow_redirects=True)
        downloadLocation = cwdtemp + "ASDS.zip"
        open(downloadLocation,'wb').write(r.content)
        print("ASDS.zip downloaded to", cwdtemp)

        with zipfile.ZipFile(downloadLocation, 'r') as zip_ref:
            zip_ref.extractall(directory + "/roms/nds/")
            zip_ref.close()
        os.remove(directory+"/roms/nds/aperturecover.png")
        print("portalDS extracted to /roms/nds/")

        
    if homebrewlinks[2][2].get() == 1:
        r = requests.get(homebrewlinks[1][2], allow_redirects=True)
        downloadLocation = cwdtemp + "CBDS.zip"
        open(downloadLocation,'wb').write(r.content)
        print("CBDS.zip downloaded to", cwdtemp)

        with zipfile.ZipFile(downloadLocation, 'r') as zip_ref:
            zip_ref.extractall(directory + "/roms/nds/")
            zip_ref.close()
        os.remove(directory+"/roms/nds/ComicBookDS.ds.gba")
        os.remove(directory+"/roms/nds/ComicBookDS.sc.nds")
        print("ComicBookDS extacted to /roms/nds/")
        

    if homebrewlinks[2][3].get() == 1:
        r = requests.get(homebrewlinks[1][3], allow_redirects=True)
        downloadLocation = cwdtemp + "DSBible.zip"
        open(downloadLocation,'wb').write(r.content)
        print("DSBible.zip downloaded to", cwdtemp)

        with zipfile.ZipFile(downloadLocation,'r') as zip_ref:
            zip_ref.extractall(directory + "/roms/nds/")
            zip_ref.close()
        os.remove(directory + "/roms/nds/README.txt")
        print("DSBible has been extracted to /roms/nds/")

    if homebrewlinks[2][4].get() == 1:
        r = requests.get(getLatestDSEins(), allow_redirects=True)
        downloadLocation = directory + "/roms/nds/DSEins.nds"
        open(downloadLocation,'wb').write(r.content)
        print("DSEins downloaded to /roms/nds/")


    if homebrewlinks[2][5].get() == 1:
        r = requests.get(homebrewlinks[1][5], allow_redirects=True)
        downloadLocation = directory + "/roms/nds/DSDoom.nds"
        open(downloadLocation,'wb').write(r.content)

        print("DSDoom has been downloaded to /roms/nds")

    if homebrewlinks[2][6].get() == 1:
        r = requests.get(homebrewlinks[1][6], allow_redirects=True)
        downloadLocation = cwdtemp + "DSFTP.zip"
        open(downloadLocation,'wb').write(r.content)

        with zipfile.ZipFile(downloadLocation, 'r') as zip_ref:
            zip_ref.extractall(directory + "/roms/nds/")
            zip_ref.close()
        print("DSFTP has been placed in /roms/nds/DSFTP")

    
    
    if homebrewlinks[2][7].get() == 1:
        r = requests.get(homebrewlinks[1][7], allow_redirects=True)
        downloadLocation = cwdtemp + "EverlastingTH.zip"
        open(downloadLocation,'wb').write(r.content)

        with zipfile.ZipFile(downloadLocation, 'r') as zip_ref:
            zip_ref.extractall(directory + "/roms/nds/")
            zip_ref.close()

        print("EverlastingTH.nds downloaded in /roms/nds/")

    if homebrewlinks[2][8].get() == 1:
        r = requests.get(homebrewlinks[1][8], allow_redirects=True)
        downloadLocation = cwdtemp + "NetHackDS-3.4.3r2.zip"
        open(downloadLocation,'wb').write(r.content)

        with zipfile.ZipFile(downloadLocation, 'r') as zip_ref:
            zip_ref.extractall(directory + "/roms/nds/")
            zip_ref.close()

    if homebrewlinks[2][9].get() == 1:
        r = requests.get(homebrewlinks[1][9], allow_redirects=True)
        downloadLocation = cwdtemp + "NitroTracker-v0.4.zip"
        open(downloadLocation,'wb').write(r.content)

        with zipfile.ZipFile(downloadLocation, 'r') as zip_ref:
            zip_ref.extractall(directory + "/roms/nds/")
            zip_ref.close()

    if homebrewlinks[2][10].get() == 1:
        r = requests.get(getLatestRelaunch(), allow_redirects=True)
        downloadLocation = cwdtemp + "Relaunch.7z"
        open(downloadLocation,'wb').write(r.content)

        proc = Popen([_7za,"x", "-aoa", downloadLocation, '-o'+cwdtemp])

        ret_val = proc.wait()

        while True:
            if ret_val  == 0:
                    print("Relaunch Extracted to", cwdtemp)
                    break
        distutils.dir_util.copy_tree(cwdtemp + "Relaunch/_nds/" , directory +"/_nds/")
        shutil.copy(cwdtemp + "Relaunch/Relaunch.nds", directory+"/roms/nds/")
        

    if homebrewlinks[2][11].get() == 1:
        r = requests.get(getLatestTicTacDS(), allow_redirects=True)
        downloadLocation = directory + "/roms/nds/tic-tac-ds.nds"
        open(downloadLocation,'wb').write(r.content)
        print("Tic-Tac-DS downloaded to /roms/nds/")
            

    #Delete tmp folder
    shutil.rmtree(cwdtemp)
    
    print("Done!")
    outputbox("Done!")

        
def chooseDir():
    window.sourceFolder =  filedialog.askdirectory(parent=window, initialdir= "/", title='Please select the directory of your SD card')
    SDentry.delete(0, tkinter.END)
    SDentry.insert(0, window.sourceFolder)


def okButtonPress(self):
    self.destroy()
    window.deiconify()

def extraHomebrew():
        homebrewWindow = tkinter.Toplevel(window)
        window.withdraw()
        homebrewWindowLabel = tkinter.Label(homebrewWindow, text="Homebrew List",font=("Verdana",12,"bold"))
        homebrewWindowLabel.pack(anchor = "w")
        homebrewWindowLabel2 = tkinter.Label(homebrewWindow, text="Select additional homebrew for download then press OK")
        homebrewWindowLabel2.pack(anchor = "w")
        
        for x in range(len(homebrewlinks[0])):
            l = tkinter.Checkbutton(homebrewWindow, text=homebrewlinks[0][x], variable=homebrewlinks[2][x])
            l.pack(anchor = "w")

        okButton = tkinter.Button(homebrewWindow, text = "OK", font=("Verdana",12,"bold"), command=lambda:okButtonPress(homebrewWindow))
        okButton.pack()
        homebrewWindow.protocol("WM_DELETE_WINDOW",lambda:okButtonPress(homebrewWindow))
        

if(sys.version_info.major < 3):
        print("This program will ONLY work on Python 3 and above")
        sys.exit()

#Create Window
window = tkinter.Tk()
window.sourceFolder = ''
window.sourceFile = ''


#Homebrew Links

homebrewlinks = [
        ['Pokémon-Chest','Aperture Science DS (portalDS)', 'ComicBookDS','DSBible','DSEins','DSDoom','DSFTP v2.6','Everlasting Love : Tomorrow Hill','NetHackDS',
         'NitroTrackerDS','Relaunch','Tic-Tac-DS'],
        ['','https://github.com/smealum/portalDS/releases/download/r1/ASDS_r1.zip','http://cbds.free.fr/Softwares/ComicBookDS/Fichiers/ComicBookDS_V3.0.zip',
         'https://www.gamebrew.org/images/a/ac/Dsbible251.zip',
         '','https://github.com/RocketRobz/dsdoom/releases/download/1.2.1-fix/dsdoom.nds','https://www.gamebrew.org/images/5/50/DSFTP26.zip',
         'http://beyondds.free.fr/projects/Everlasting/EverlastingTH.zip','https://github.com/fancypantalons/nethackds/releases/download/3.4.3r2/NetHackDS-3.4.3r2.zip',
         'http://web.archive.org/web/20190122024458/http://nitrotracker.tobw.net/NitroTracker-v0.4.zip','',''],
        [tkinter.IntVar(value=0),tkinter.IntVar(value=0),tkinter.IntVar(value=0),tkinter.IntVar(value=0),tkinter.IntVar(value=0),tkinter.IntVar(value=0),tkinter.IntVar(value=0),tkinter.IntVar(value=0),tkinter.IntVar(value=0),tkinter.IntVar(value=0),tkinter.IntVar(value=0),tkinter.IntVar(value=1)]
        ]


# Title and Author
appTitle = tkinter.Label(text="Lazy DSi file downloader",font=('Verdana', 14), fg="white", bg="black")
appTitle.width = 100
appAuthor = tkinter.Label(text="by YourKalamity",font=('Verdana', 10, 'italic'), anchor="w")
appAuthor.width = 100

#SD Directory entry
SDlabel = tkinter.Label(text = "Enter your SD card's directory")
SDlabel.width = 100
SDentry = tkinter.Entry(width=30)
SDentry.width = 100
#Button to select folder
b_chooseDir = tkinter.Button(window, text = "Click to select folder", width = 25, command = chooseDir)
b_chooseDir.width = 100
b_chooseDir.height = 50

#Checkbox for Memory Pit
downloadmemorypit = tkinter.IntVar(value=1)
downloadmemorypitCheck = tkinter.Checkbutton(window, text = "Download Memory pit exploit?", variable = downloadmemorypit)


#DSi Firmware selector
firmwareLabel = tkinter.Label(text = "Select your DSi firmware : ")
firmwareLabel.width = 100
firmwareVersion = tkinter.StringVar(window)
firmwareVersion.set(dsiVersions[0])
selector = tkinter.OptionMenu(window, firmwareVersion, *dsiVersions)
selector.width = 100

#Checkbox for TWiLight Menu ++
downloadtwlmenu = tkinter.IntVar(value=1)
downloadtwlmenuCheck = tkinter.Checkbutton(window, text = "Download / Update TWiLight menu?", variable = downloadtwlmenu)

#Checkbox for dumpTool
downloaddumptool = tkinter.IntVar(value=1)
downloaddumptoolCheck = tkinter.Checkbutton(window, text ="Download dumpTool?", variable=downloaddumptool)

#Checkbox for Unlaunch
unlaunch = tkinter.IntVar(value=1)
unlaunchCheck = tkinter.Checkbutton(window, text = "Download Unlaunch?", variable =unlaunch)

#Button to launch Additional Homebrew box
buttonExtraHomebrew = tkinter.Button(window, text = "Additional homebrew...", width = 25, command = extraHomebrew)
buttonExtraHomebrew.width = 100
buttonExtraHomebrew.height = 50

#Start button and Output box
startButton = tkinter.Button(window, text = "Start", font = ("TkDefaultFont",12,'bold'), width = 25, command = start)
outputLabel = tkinter.Label(text="Output")
outputLabel.width = 100
outputBox = tkinter.Text(window,state='disabled', width = 30, height = 10)

#Pack everything in to window
window.title("Lazy DSi file downloader")
window.resizable(0, 0)
appTitle.pack()
appAuthor.pack()
SDlabel.pack()
SDentry.pack()
b_chooseDir.pack()
downloadmemorypitCheck.pack()
firmwareLabel.pack()
selector.pack()
downloadtwlmenuCheck.pack()
downloaddumptoolCheck.pack()
unlaunchCheck.pack()
buttonExtraHomebrew.pack()
startButton.pack()
outputLabel.pack()
outputBox.pack()
window.mainloop()
