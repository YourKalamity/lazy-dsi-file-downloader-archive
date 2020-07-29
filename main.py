
# Created by YourKalamity
#https://github.com/YourKalamity/lazy-dsi-file-downloader    


#Import libraries
import tkinter 
from tkinter import messagebox
from tkinter import filedialog
import tkinter.font
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
import webbrowser
import threading
from requests.exceptions import ConnectionError
import hashlib

pageNumber = 0

#Memory Pit Links - Points to GitHub repo
dsiVersions = ["1.0 - 1.3 (USA, EUR, AUS, JPN)", "1.4 - 1.4.5 (USA, EUR, AUS, JPN)", "All versions (KOR, CHN)"]
memoryPitLinks = ["https://github.com/YourKalamity/just-a-dsi-cfw-installer/raw/master/assets/files/memoryPit/256/pit.bin","https://github.com/YourKalamity/just-a-dsi-cfw-installer/raw/master/assets/files/memoryPit/768_1024/pit.bin"]

#Downloader
def downloadFile(link, destination):
    try:
        r = requests.get(link, allow_redirects=True)
        if link.find('/'):
            fileName = link.rsplit('/', 1)[1]
        downloadLocation = destination + fileName
        open(downloadLocation, 'wb').write(r.content)
        return downloadLocation
    except ConnectionError:
        print("File not available, skipping...")
        return None
    
def hashcreator(filetobechecked):
    string = hashlib.blake2b(open(filetobechecked,'rb').read()).hexdigest()
    return string

#Get link of latest Github Release
def getLatestGitHub(usernamerepo, assetNumber):
    release = json.loads(requests.get("https://api.github.com/repos/"+usernamerepo+"/releases/latest").content)
    url = release["assets"][assetNumber]["browser_download_url"]
    return url

#Push text to output box
def outputbox(message):
    outputBox.configure(state='normal')
    outputBox.insert('end', message)
    outputBox.see(tkinter.END)
    outputBox.configure(state='disabled')

#Check if directory exists and has write permissions
def validateDirectory(directory):
        try:
            directory = str(directory)
        except TypeError:
            outputbox("That's not a valid directory \n")
            outputbox("Press the Back button to change the folder\n")
            return False
        try:
            string = directory + "/test.file"
            with open(string, 'w') as file:
                file.close()
            os.remove(string)
        except FileNotFoundError:
            outputbox("That's not a valid directory")
            outputbox("or you do not have the")
            outputbox(" permission to write there")
            outputbox("Press the Back button to change the folder\n")
            return False
        except PermissionError:
            outputbox("You do not have write access  to that folder\n")
            outputbox("Press the Back button to change the folder\n")
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
                outputbox("7-Zip not found \n")
                finalbackButton.configure(state='normal')
                return
    print("7-Zip found!")

    lineCounter = 0
    
    #Variables
    directory = SDentry
    version = firmwareVersion.get()
    unlaunchNeeded = unlaunch.get()

    #Validate directory
    directoryValidated = validateDirectory(directory)
    if directoryValidated == False:
        finalbackButton.configure(state='normal')
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
        outputbox("Downloading Memory Pit\n")
        downloadLocation = downloadFile(memoryPitDownload, memoryPitLocation)
        if downloadLocation != None:
            outputbox("Memory Pit Downloaded\n")
            print("Memory Pit Downloaded")

    if downloadtwlmenu.get() == 1:
        #Download TWiLight Menu
        outputbox("Downloading TWiLight Menu ++\n")
        TWLmenuLocation = downloadFile(getLatestGitHub('DS-Homebrew/TWiLightMenu', 3),cwdtemp)
        if TWLmenuLocation != None:
            outputbox("TWiLight Menu ++ Downloaded\n")
            print("TWiLight Menu ++ Downloaded")

            #Extract TWiLight Menu
            proc = Popen([_7za,"x", "-aoa", TWLmenuLocation, '-o'+cwdtemp, 'DSi - CFW users/SDNAND root/', '_nds', 'DSi&3DS - SD card users', 'roms', 'BOOT.NDS'])
            ret_val = proc.wait()

            while True:
                if ret_val  == 0:
                    outputbox("TWiLight Menu ++ Extracted\n")
                    print("TWiLight Menu ++ Extracted to", cwdtemp)
                    break
            originalHash = hashcreator(cwdtemp + "DSi&3DS - SD card users/BOOT.NDS")

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
            comparedHash = hashcreator(directory+"/BOOT.NDS")
            if originalHash == comparedHash:
                print("TWiLight  Menu ++ placed in", directory)
                outputbox("TWiLight Menu ++ placed on SD \n")
            
        
        #Download DeadSkullzJr's Cheat Database
        Path(directory + "/_nds/TWiLightMenu/extras/").mkdir(parents=True,exist_ok=True)
        outputbox("Downloading DeadSkullzJr's Cheat database\n")
        downloadLocation = downloadFile('https://bitbucket.org/DeadSkullzJr/nds-cheat-databases/raw/933c375545d3ff90854d1e210dcf4b3b31d9d585/Cheats/usrcheat.dat', directory + "/_nds/TWiLightMenu/extras/")
        if downloadLocation != None:
            print("DeadSkullzJr's Cheat Database downloaded")
            outputbox("DeadSkullzJr's Cheat Database downloaded\n")
        

    if downloaddumptool.get() == 1:            
        #Download dumpTool
        outputbox("Downloading dumpTool\n")
        downloadLocation = downloadFile(getLatestGitHub('zoogie/dumpTool', 0), directory)
        if downloadLocation != None:
            print("dumpTool downloaded")
            outputbox("dumpTool Downloaded\n")
            lineCounter = lineCounter + 1

    if unlaunchNeeded == 1 :
        #Download Unlaunch
        url = "https://problemkaputt.de/unlaunch.zip"
        outputbox("Downloading Unlaunch\n")
        unlaunchLocation = downloadFile(url, cwdtemp)
        if unlaunchLocation != None:
            print("Unlaunch Downloaded")
            outputbox("Unlaunch Downloaded\n")
            lineCounter = lineCounter + 1

        #Extract Unlaunch
        unzipper(unlaunchLocation,directory)
    
    

    #Creates roms/nds if it does not exist
    roms = directory +"/roms/nds/"
    Path(roms).mkdir(parents=True,exist_ok=True)

    outputbox("Downloading other homebrew\n")
    lineCounter = lineCounter + 1
    print("Downloading other homebrew...")


    for count, item in enumerate(homebrewDB):
        if homebrewList[count].get() == 1:
            print("Downloading "+item["title"])
            outputbox("Downloading "+item["title"]+'\n')
            lineCounter = lineCounter + 1
            if item["github"] == "True":
                downloadlink = getLatestGitHub(item["repo"], int(item["asset"]))
            else: 
                downloadlink = item["link"]
            if item["extension"] == "nds":
                downloadFile(downloadlink, roms)
                outputbox("Downloaded "+item["title"]+'\n')
            elif item["extension"] == "zip":
                downloadLocation = downloadFile(downloadlink, cwdtemp)
                if downloadLocation != None:
                    if item["location"]["roms"] == "all":
                        unzipper(downloadLocation, roms)
                        outputbox("Downloaded "+item["title"]+'\n')
            elif item["extension"] == "7z":
                downloadLocation = downloadFile(downloadlink, cwdtemp)
                if downloadLocation != None:
                    if item["location"]["roms"] == "all":
                        un7zipper(_7za, downloadLocation, roms)
                        outputbox("Downloaded "+item["title"]+'\n')
                    else:
                        un7zipper(_7za, downloadLocation, cwdtemp)
                        if "root" in item["location"]:
                            Path(directory+(item["location"]["root"].split('/')).pop()).mkdir(parents=True,exist_ok=True)
                            shutil.copy(cwdtemp+item["location"]["root"],directory+((item["location"]["root"].split('/')).pop().pop(0)))
                        if "roms" in item["location"]:
                            shutil.copy(cwdtemp+item["location"]["roms"],roms)
                        outputbox("Downloaded "+item["title"]+'\n')
                    
        

    #Delete tmp folder
    shutil.rmtree(cwdtemp)

    #Restore button access
    finalnextButton.config(state="normal")
    window.protocol("WM_DELETE_WINDOW",lambda:closeButtonPress(window))

    print("Done!")
    outputbox("Done!\n")
    outputbox("Press the Finish button to continue... \n")

        
def chooseDir(source,SDentry):
    source.sourceFolder =  filedialog.askdirectory(parent=source, initialdir= "/", title='Please select the directory of your SD card')
    SDentry.delete(0, tkinter.END)
    SDentry.insert(0, source.sourceFolder)


def okButtonPress(self,source):
    self.destroy()
    source.deiconify()

def extraHomebrew(source):
        homebrewWindow = tkinter.Toplevel(source)
        homebrewWindow.config(bg="#f0f0f0")
        source.withdraw()
        homebrewWindowLabel = tkinter.Label(homebrewWindow, text="Homebrew List",font=("Segoe UI",12,"bold"),bg="#f0f0f0")
        homebrewWindowLabel.pack(anchor = "w")
        homebrewWindowLabel2 = tkinter.Label(homebrewWindow, text="Select additional homebrew for download then press OK", font=(bodyFont),bg="#f0f0f0")
        homebrewWindowLabel2.pack(anchor = "w")
        
        vscrollbar = tkinter.Scrollbar(homebrewWindow)
        canvas = tkinter.Canvas(homebrewWindow, yscrollcommand=vscrollbar.set)
        canvas.config(bg="#f0f0f0")
        vscrollbar.config(command=canvas.yview)
        vscrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y) 

        homebrewFrame = tkinter.Frame(canvas) 
        homebrewFrame.configure(bg="#f0f0f0")

        homebrewWindow.title("Homebrew List")
        homebrewWindow.resizable(0,0)
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window(0,0, window=homebrewFrame, anchor="n")
        for count, x in enumerate(homebrewDB):
            l = tkinter.Checkbutton(homebrewFrame, text=x["title"] + " by " + x["author"],font=(bigListFont), variable=homebrewList[count],bg="#f0f0f0")
            l.config(selectcolor="#F0F0F0")
            l.pack(anchor = "w")
       
        frame = tkinter.ttk.Frame(homebrewWindow, relief=tkinter.RAISED, borderwidth=1)
        frame.pack(fill=tkinter.BOTH, expand=True)


        okButton = tkinter.Button(homebrewWindow, text = "OK", font=(buttonFont), command=lambda:okButtonPress(homebrewWindow,source),bg="#f0f0f0")
        okButton.pack(side=tkinter.RIGHT, padx=5, pady=5)
        homebrewWindow.update()
        canvas.config(scrollregion=canvas.bbox("all"))

        homebrewWindow.protocol("WM_DELETE_WINDOW",lambda:okButtonPress(homebrewWindow,source))

def closeButtonPress(source):
    source.destroy()
    root.destroy()

def nextWindow(windownumbertosummon):
    globals()["summonWindow"+windownumbertosummon]

def donothing():
    return

def summonWindow0():
    window.title("Lazy DSi file Downloader")
    window.resizable(0,0)
    window.geometry("500x360")
    window.option_add("*Background", backgroundColour)
    window.configure(bg=backgroundColour)
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH,padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X,padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    first = tkinter.Label(topFrame, text="Welcome to the Lazy DSi File Downloader", font=(titleFont), fg=foregroundColour)
    first.grid(column=0,row=0, sticky="w",padx=5)
    
    bulletpoints = [
        "This is an application made by Your Kalamity that downloads and place files for homebrew'ing your Nintendo DSi in the correct location. If you have already installed homebrew, this can also update the one you have.",
        "This is to be used in conjunction with the Nintendo DSi Modding guide by NightScript and emiyl",
        "Check it out here: https://dsi.cfw.guide/",
        "By using this application, you do not need to follow any of the 'Preparing SD card' steps.",
        "This application is to be given for free. If you have paid to receive this, contact the person that sold you this application; you have been scammed.",
        "You may use any part of this application for your own purposes as long as credit is given.",
        "Please proceed by hitting the 'Next' button"
        ]
    
    for count, x in enumerate(bulletpoints):
        bullet = tkinter.Label(topFrame, text=x, font=(paragraphFont),fg=foregroundColour,wraplength=450, justify="left")
        bullet.grid(column=0,row=count+3, sticky="w", padx=5)
    
    discordButton = tkinter.Button(bottomFrame, text="DS⁽ⁱ⁾ Mode Hacking Discord server", fg=foregroundColour,bg=buttonColour, font=(buttonFont),command=lambda:webbrowser.open("https://discord.gg/yD3spjv",new=1))
    discordButton.pack(side=tkinter.LEFT, padx="5", pady="5")
    nextButton = tkinter.Button(bottomFrame, text="Next",width="8", fg=foregroundColour,bg=nextButtonColour, font=(buttonFont),command=lambda:[topFrame.destroy(),bottomFrame.destroy(),summonWindow1()])
    nextButton.pack(side=tkinter.RIGHT, padx="5", pady="5")

    window.protocol("WM_DELETE_WINDOW",lambda:closeButtonPress(window))
    

def summonWindow1():
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH,padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X,padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    first = tkinter.Label(topFrame, text="Memory Pit", font=(titleFont), fg=foregroundColour)
    first.grid(column=0,row=0, sticky="w",padx=5)
    subtitle = tkinter.Label(topFrame, text='thank you, shutterbug2000!', font=(subtitleFont), fg=foregroundColour)
    subtitle.grid(column=0,row=1, sticky="w",padx=5)
    filler = tkinter.Label(topFrame, text=" ")
    filler.grid(column=0,row=3)
    downloadmemorypitCheck = tkinter.Checkbutton(topFrame, text = "Download Memory pit exploit?",font=(buttonFont),fg=foregroundColour, variable = downloadmemorypit)
    downloadmemorypitCheck.grid(column=0,row=2, sticky="w")
    firmwareLabel = tkinter.Label(topFrame, text = "Select your DSi firmware : ",fg=foregroundColour,font=(buttonFont))
    firmwareLabel.grid(column=0,row=4, sticky="w")
    selector = tkinter.OptionMenu(topFrame, firmwareVersion, *dsiVersions)
    selector.config(bg=buttonColour,fg=foregroundColour,font=(buttonFont))
    selector["menu"].config(bg=buttonColour,fg=foregroundColour,font=(buttonFont))
    selector.grid(column=0,row=5,sticky="w")

    backButton = tkinter.Button(bottomFrame,text="Back", font=(buttonFont),fg=foregroundColour,bg=backButtonColour,command=lambda: [topFrame.destroy(),bottomFrame.destroy(),summonWindow0()], width="8")
    backButton.pack(side=tkinter.LEFT)
    nextButton = tkinter.Button(bottomFrame, text="Next",width="8", fg=foregroundColour,bg=nextButtonColour, font=(buttonFont),command=lambda:[topFrame.destroy(),bottomFrame.destroy(),summonWindow2()])
    nextButton.pack(side=tkinter.RIGHT, padx="5", pady="5")
    window.protocol("WM_DELETE_WINDOW",lambda:closeButtonPress(window))


def summonWindow2():

    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH,padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X,padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    first = tkinter.Label(topFrame, text="Homebrew Section", font=(titleFont), fg=foregroundColour)
    first.grid(column=0,row=0, sticky="w")
    subtitle = tkinter.Label(topFrame, text='brewed at home', font=(subtitleFont), fg=foregroundColour)
    subtitle.grid(column=0,row=1,sticky="w")
    downloadtwlmenuCheck = tkinter.Checkbutton(topFrame, text = "Download or Update TWiLight menu?",fg=foregroundColour, variable = downloadtwlmenu,font=(buttonFont))
    downloadtwlmenuCheck.grid(column=0,row=2, sticky ="w")
    downloaddumptoolCheck = tkinter.Checkbutton(topFrame, text ="Download dumpTool?", variable=downloaddumptool,fg=foregroundColour,font=(buttonFont))
    downloaddumptoolCheck.grid(column=0,row=3,sticky="w")
    unlaunchCheck = tkinter.Checkbutton(topFrame, text = "Download Unlaunch?", variable =unlaunch, fg=foregroundColour,font=(buttonFont))
    unlaunchCheck.grid(column=0,row=4,sticky="w")
    buttonExtraHomebrew = tkinter.Button(topFrame, text = "Additional homebrew...", command =lambda:[extraHomebrew(window)], fg=foregroundColour,font=(buttonFont),bg=buttonColour)
    buttonExtraHomebrew.grid(column=0,row=5,sticky="w",pady=5)
    backButton = tkinter.Button(bottomFrame,text="Back", font=(buttonFont),fg=foregroundColour,bg=backButtonColour,command=lambda: [topFrame.destroy(),bottomFrame.destroy(),summonWindow1()], width="8")
    backButton.pack(side=tkinter.LEFT)
    nextButton = tkinter.Button(bottomFrame, text="Next",width="8", fg=foregroundColour,bg=nextButtonColour, font=(buttonFont),command=lambda:[topFrame.destroy(),bottomFrame.destroy(),summonWindow3()])
    nextButton.pack(side=tkinter.RIGHT, padx="5", pady="5")
    window.protocol("WM_DELETE_WINDOW",lambda:closeButtonPress(window))

def summonWindow3():
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH,padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X,padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    first = tkinter.Label(topFrame, text="Select SD Card", font=(titleFont), fg=foregroundColour)
    first.grid(column=0,row=0, sticky="w")
    subtitle = tkinter.Label(topFrame, text='ready to download?', font=(subtitleFont), fg=foregroundColour)
    subtitle.grid(column=0,row=1,sticky="w")
    noticeLabel=tkinter.Label(topFrame,text="Plug in your SD card and choose the directory", fg=foregroundColour, font=(bodyFont))
    noticeLabel.grid(column=0,row=2,sticky="w")
    SDentry = tkinter.Entry(topFrame, fg=foregroundColour,bg=buttonColour,font=(buttonFont),width=25)
    SDentry.grid(column=0, row=3,sticky="w")
    chooseDirButton = tkinter.Button(topFrame, text = "Click to select folder", command =lambda:chooseDir(topFrame,SDentry),fg=foregroundColour,bg=buttonColour,font=(buttonFont),width=25)
    chooseDirButton.grid(column=0, row=4,sticky="w",pady=5)
    backButton = tkinter.Button(bottomFrame,text="Back", font=(buttonFont),fg=foregroundColour,bg=backButtonColour,command=lambda: [topFrame.destroy(),bottomFrame.destroy(),summonWindow2()], width="8")
    backButton.pack(side=tkinter.LEFT)
    nextButton = tkinter.Button(bottomFrame, text="Start",width="8", fg=foregroundColour,bg=nextButtonColour, font=(buttonFont),command=lambda:[globalify(SDentry.get()),topFrame.destroy(),bottomFrame.destroy(),summonWindow4()])
    nextButton.pack(side=tkinter.RIGHT, padx="5", pady="5")
    window.protocol("WM_DELETE_WINDOW",lambda:closeButtonPress(window))

def globalify(value):
    global SDentry
    SDentry = value

def summonWindow4():
    startThread = threading.Thread(target=start, daemon=True)
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH,padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X,padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    first = tkinter.Label(topFrame, text="Download Screen", font=(titleFont), fg=foregroundColour)
    first.grid(column=0,row=0, sticky="w")
    subtitle = tkinter.Label(topFrame, text='please wait...', font=(subtitleFont), fg=foregroundColour)
    subtitle.grid(column=0,row=1,sticky="w")
    global outputBox
    outputBox = tkinter.Text(topFrame,state='disabled', width = 60, height = 15, bg="black", fg="white")
    outputBox.grid(column=0,row=2,sticky="w")
    startThread.start()
    global finalbackButton
    finalbackButton = tkinter.Button(bottomFrame,state="disabled",  text="Back", font=(buttonFont),fg=foregroundColour,bg=backButtonColour,command=lambda: [topFrame.destroy(),bottomFrame.destroy(),summonWindow3()], width="8")
    finalbackButton.pack(side=tkinter.LEFT)
    global finalnextButton
    finalnextButton = tkinter.Button(bottomFrame, state="disabled", text="Finish",width="8", fg=foregroundColour,bg=nextButtonColour, font=(buttonFont),command=lambda:[topFrame.destroy(),bottomFrame.destroy(),summonWindow5()])
    finalnextButton.pack(side=tkinter.RIGHT, padx="5", pady="5")
    window.protocol("WM_DELETE_WINDOW",lambda:donothing)

def summonWindow5():

    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH,padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X,padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    first = tkinter.Label(topFrame, text="Completed", font=(titleFont), fg=foregroundColour)
    first.grid(column=0,row=0, sticky="w")
    subtitle = tkinter.Label(topFrame, text='all done!', font=(subtitleFont), fg=foregroundColour)
    subtitle.grid(column=0,row=1,sticky="w")
    label= tkinter.Label(topFrame,text="Your SD card is now ready to run and use Homebrew on your Nintendo DSi.",font=(bodyFont),fg=foregroundColour,wraplength=450,justify="left")
    label.grid(column=0,row=2,sticky="w")
    labellink= tkinter.Label(topFrame,text="You can now eject your SD card and follow the steps of https://dsi.cfw.guide/",font=(bodyFont),fg=foregroundColour,wraplength=450,justify="left")
    labellink.grid(column=0,row=3,sticky="w")
    labellink.bind("<Button-1>", lambda e: webbrowser.open_new("https://dsi.cfw.guide/"))
    label= tkinter.Label(topFrame,text="Credits to",font=(bodyFont),fg=foregroundColour)
    label.grid(column=0,row=4,sticky="w")
    bulletpoints = ["YourKalamity - Creator","NightScript - Idea & writer of dsi.cfw.guide","Emiyl - Writer of dsi.cfw.guide","SNBeast - Testing and pointing out errors","Everybody that helped create the homebrew downloaded by this app","Kaisaan - Yes"]
    w = 5
    for x in bulletpoints:
        label = tkinter.Label(topFrame,text=x,font=(bigListFont),fg=foregroundColour)
        label.grid(column=0,row=w,sticky="w")
        w = w + 1
    label= tkinter.Label(topFrame,text="Press the Close button to Exit",font=(bodyFont),fg=foregroundColour)
    label.grid(column=0,row=w+1,sticky="w")
    finish = tkinter.Button(bottomFrame, text="Close",width="8", fg=foregroundColour,bg=nextButtonColour, font=(buttonFont),command=lambda:[topFrame.destroy(),bottomFrame.destroy(),closeButtonPress(window)])
    finish.pack(side=tkinter.RIGHT, padx="5", pady="5")
    window.protocol("WM_DELETE_WINDOW",lambda:closeButtonPress(window))


if(sys.version_info.major < 3):
        print("This program will ONLY work on Python 3 and above")
        sys.exit()

root = tkinter.Tk()
window = tkinter.Toplevel(root)
root.withdraw()

#Homebrew Database
homebrewDB = json.loads(requests.get('https://raw.githubusercontent.com/YourKalamity/just-a-dsi-DB/master/just-a-dsi-DB.json').content)
homebrewList = []
for x in homebrewDB:
    homebrewList.append(tkinter.IntVar())
homebrewList[0] = tkinter.IntVar(value=1)

#TKinter Vars
downloadmemorypit = tkinter.IntVar(value=1)
firmwareVersion = tkinter.StringVar()
firmwareVersion.set(dsiVersions[0])
downloadtwlmenu = tkinter.IntVar(value=1)
downloaddumptool = tkinter.IntVar(value=1)
unlaunch = tkinter.IntVar(value=0)


#Fonts
titleFont = tkinter.font.Font( 
    family= "Segoe UI",
    size= 15,
    weight= "bold"
    )
subtitleFont = tkinter.font.Font(
    family= "Segoe UI",
    size= 11,
    slant= "italic"
)
    
bodyFont = tkinter.font.Font(
    family= "Segoe UI",
    underline= False,
    size = 11
    )
buttonFont = tkinter.font.Font(
    family="Segoe UI",
    underline=False,
    size = 11,
    weight = "bold"
)

bigListFont = tkinter.font.Font(
    family="Segoe UI",
    underline=False,
    size=9
)

paragraphFont = tkinter.font.Font(
    family="Segoe UI",
    size=10
)

if platform.system() == "Darwin":    #Why is macOS so difficult...
    backgroundColour = "#f0f0f0"     #How dull and boring
    foregroundColour = "black"    
    buttonColour = "#f0f0f0"
    backButtonColour = "#f0f0f0"
    nextButtonColour = "#f0f0f0"
else: #Non Jeve Stobs worshippers
    backgroundColour = "#252a34"
    foregroundColour = "white"
    buttonColour = "#7289DA"
    backButtonColour = "#567487"
    nextButtonColour = "#027b76"


summonWindow0()
root.mainloop()
