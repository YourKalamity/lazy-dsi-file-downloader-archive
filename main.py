
# Created by YourKalamity
#https://github.com/YourKalamity/lazy-dsi-file-downloader    


#Import libraries
import tkinter 
from tkinter import messagebox
from tkinter import filedialog
import tkinter.ttk
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

#Downloader
def downloadFile(link, destination):
    r = requests.get(link, allow_redirects=True)
    if link.find('/'):
        fileName = link.rsplit('/', 1)[1]
    downloadLocation = destination + fileName
    open(downloadLocation, 'wb').write(r.content)
    return downloadLocation
    

#Get link of latest Github Release
def getLatestGitHub(usernamerepo, assetNumber):
    release = json.loads(requests.get("https://api.github.com/repos/"+usernamerepo+"/releases/latest").content)
    url = release["assets"][assetNumber]["browser_download_url"]
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

def unzipper(unzipped, destination):
    with zipfile.ZipFile(unzipped, 'r') as zip_ref:
            zip_ref.extractall(destination)
            zip_ref.close()

def un7zipper(_7za, zipfile, destination):
    proc = Popen([_7za,"x", "-aoa", zipfile, '-o'+destination])

    ret_val = proc.wait()

    while True:
        if ret_val  == 0:
            break



def start():
    
    #Clear outputBox
    outputBox.configure(state='normal')
    outputBox.delete('1.0', tkinter.END)
    outputBox.configure(state='disabled')

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
        downloadFile(memoryPitDownload, memoryPitLocation)
        outputbox("Memory Pit Downloaded          ")
        print("Memory Pit Downloaded")

    if downloadtwlmenu.get() == 1:
        #Download TWiLight Menu
        TWLmenuLocation = downloadFile(getLatestGitHub('DS-Homebrew/TWiLightMenu', 0),cwdtemp)
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
        #Some Homebrew write to the _nds folder so it is better to clear it first
        shutil.rmtree(cwdtemp +"_nds/")
        Path(cwdtemp +"_nds/").mkdir(parents=True,exist_ok=True)

        print("TWiLight  Menu ++ placed in", directory)
        outputbox("TWiLight Menu ++ placed        ")
        
        #Download DeadSkullzJr's Cheat Database
        Path(directory + "/_nds/TWiLightMenu/extras/").mkdir(parents=True,exist_ok=True)
        downloadFile('https://bitbucket.org/DeadSkullzJr/nds-cheat-databases/raw/933c375545d3ff90854d1e210dcf4b3b31d9d585/Cheats/usrcheat.dat', directory + "/_nds/TWiLightMenu/extras/")
        print("DeadSkullzJr's Cheat Database downloaded")
        

    if downloaddumptool.get() == 1:            
        #Download dumpTool
        downloadFile(getLatestGitHub('zoogie/dumpTool', 0), directory)
        print("dumpTool downloaded")
        outputbox("dumpTool Downloaded            ")

    if unlaunchNeeded == 1 :
        #Download Unlaunch
        url = "https://problemkaputt.de/unlaunch.zip"
        unlaunchLocation = downloadFile(url, cwdtemp)
        print("Unlaunch Downloaded")
        outputbox("Unlaunch Downloaded            ")

        #Extract Unlaunch
        unzipper(unlaunchLocation,directory)
    
    

    #Creates roms/nds if it does not exist
    roms = directory +"/roms/nds/"
    Path(roms).mkdir(parents=True,exist_ok=True)

    outputbox("Downloading other homebrew     ")
    print("Downloading other homebrew...")


    for count, item in enumerate(homebrewDB):
        if homebrewList[count].get() == 1:
            print("Downloading "+item["title"])
            if item["github"] == "True":
                downloadlink = getLatestGitHub(item["repo"], int(item["asset"]))
            else: 
                downloadlink = item["link"]
            if item["extension"] == "nds":
                downloadFile(downloadlink, roms)
            elif item["extension"] == "zip":
                downloadLocation = downloadFile(downloadlink, cwdtemp)
                if item["location"]["roms"] == "all":
                    unzipper(downloadLocation, roms)
            elif item["extension"] == "7z":
                downloadLocation = downloadFile(downloadlink, cwdtemp)
                if item["location"]["roms"] == "all":
                    un7zipper(_7za, downloadLocation, roms)
                else:
                    un7zipper(_7za, downloadLocation, cwdtemp)
                    if "root" in item["location"]:
                        Path(directory+(item["location"]["root"].split('/')).pop()).mkdir(parents=True,exist_ok=True)
                        shutil.copy(cwdtemp+item["location"]["root"],directory+((item["location"]["root"].split('/')).pop().pop(0)))
                    if "roms" in item["location"]:
                        shutil.copy(cwdtemp+item["location"]["roms"],roms)
                    
        

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
        
        vscrollbar = tkinter.Scrollbar(homebrewWindow)
        canvas = tkinter.Canvas(homebrewWindow, yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=canvas.yview)
        vscrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y) 

        homebrewFrame = tkinter.Frame(canvas) 
        homebrewWindow.title("Homebrew List")
        homebrewWindow.resizable(0,0)
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window(0,0, window=homebrewFrame, anchor="n")
        for count, x in enumerate(homebrewDB):
            l = tkinter.Checkbutton(homebrewFrame, text=x["title"] + " by " + x["author"], variable=homebrewList[count])
            l.pack(anchor = "w")
       
        frame = tkinter.ttk.Frame(homebrewWindow, relief=tkinter.RAISED, borderwidth=1)
        frame.pack(fill=tkinter.BOTH, expand=True)

        okButton = tkinter.Button(homebrewWindow, text = "OK", font=("Verdana",12,"bold"), command=lambda:okButtonPress(homebrewWindow))
        okButton.pack(side=tkinter.RIGHT, padx=5, pady=5)
        homebrewWindow.update()
        canvas.config(scrollregion=canvas.bbox("all"))

        homebrewWindow.protocol("WM_DELETE_WINDOW",lambda:okButtonPress(homebrewWindow))


        

if(sys.version_info.major < 3):
        print("This program will ONLY work on Python 3 and above")
        sys.exit()

#Create Window
window = tkinter.Tk()
window.sourceFolder = ''
window.sourceFile = ''


#Homebrew Links
#Homebrew Database
homebrewDB = json.loads(requests.get('https://raw.githubusercontent.com/YourKalamity/just-a-dsi-DB/master/just-a-dsi-DB.json').content)
homebrewList = []
for x in homebrewDB:
    homebrewList.append(tkinter.IntVar())

homebrewList[0] = tkinter.IntVar(value=1)

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
