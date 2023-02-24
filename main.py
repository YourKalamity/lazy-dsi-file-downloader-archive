#!/usr/bin/env python3

# Created by YourKalamity
# https://github.com/YourKalamity/lazy-dsi-file-downloader


import tkinter
import tkinter.filedialog
import tkinter.font
import tkinter.ttk
import os
import platform
import sys
import requests
import json
from pathlib import Path
import shutil
import zipfile
import webbrowser
import threading
import py7zr

pageNumber = 0
memoryPitLink = "https://dsi.cfw.guide/assets/files/memory_pit/"
memoryPitLinks = [
    memoryPitLink + "256/pit.bin",
    memoryPitLink + "768_1024/pit.bin"
]


def downloadFile(link, destination):
    try:
        r = requests.get(link, allow_redirects=True)
        if link.find('/'):
            fileName = link.rsplit('/', 1)[1]
        if destination.endswith("/") is False:
            destination = destination + "/"
        downloadLocation = destination + fileName
        open(downloadLocation, 'wb').write(r.content)
        return downloadLocation
    except Exception:
        print("File not available, skipping...")
        return None


def getLatestGitHub(usernamerepo, assetNumber):
    if not isinstance(assetNumber, int):
        return False
    release = json.loads(
        requests.get(
            "https://api.github.com/repos/"+usernamerepo+"/releases/latest"
        ).content)
    url = release["assets"][assetNumber]["browser_download_url"]
    return url


def outputbox(message):
    outputBox.configure(state='normal')
    outputBox.insert('end', message)
    outputBox.see(tkinter.END)
    outputBox.configure(state='disabled')


def validateDirectory(directory):
    if directory == "":
        outputbox("That's not a valid directory \n")
        outputbox("Press the Back button to change the folder\n")
        return False
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
        outputbox("That's not a valid directory or you do not have the\n")
        outputbox("permissions needed to write there\n")
        outputbox("Press the Back button to change the folder\n")
        return False
    except PermissionError:
        outputbox("You do not have write access to that folder\n")
        outputbox("Press the Back button to change the folder\n")
        return False
    else:
        return True


def unzipper(unzipped, destination):
    if not zipfile.is_zipfile(unzipped):
        return False
    try:
        with zipfile.ZipFile(unzipped, 'r') as zip_ref:
            zip_ref.extractall(destination)
            zip_ref.close()
        return True
    except Exception:
        return False


def un7zipper(zipfile, destination, files=None):
    if not py7zr.is_7zfile(zipfile):
        return False
    with py7zr.SevenZipFile(zipfile) as archive:
        if files is None:
            archive.extractall(path=destination)
        else:
            targets = files
            for extractable in archive.getnames():
                for file in files:
                    if extractable != file and extractable.startswith(file):
                        targets.append(extractable)
            archive.extract(path=destination, targets=files)


def download_MemoryPit(directory):
    memoryPitLocation = directory + "/private/ds/app/484E494A/"
    Path(memoryPitLocation).mkdir(parents=True, exist_ok=True)
    outputbox("Downloading Memory Pit\n")
    downloadLocation = downloadFile(memoryPitLinks[facebookIcon.get()], memoryPitLocation)
    if downloadLocation is None:
        outputbox("Memory Pit not found, skipping...\n")
        print("Memory Pit not found, skipping...")
        return False
    outputbox("Memory Pit Downloaded\n")
    print("Memory Pit Downloaded")
    return True


def download_DSJ_cheat_codes(directory):
    outputbox("Downloading DeadSkullzJr's Cheat database\n")
    downloadLocation = downloadFile('https://bitbucket.org/DeadSkullzJr/nds-i-cheat-databases/raw/963fff3858de7539891ef7918d992b8b06972a48/Cheat%20Databases/usrcheat.dat', directory + "/_nds/TWiLightMenu/extras/")

    if downloadLocation is None:
        outputbox("DeadSkullzJr's Cheat database not found, skipping...\n")
        print("DeadSkullzJr's Cheat database not found, skipping...")
        return False

    Path(directory + "/_nds/TWiLightMenu/extras/").mkdir(parents=True, exist_ok=True)
    print("DeadSkullzJr's Cheat Database downloaded")
    outputbox("DeadSkullzJr's Cheat Database downloaded\n")


def download_TWLMenu(directory, cwdtemp):
    # Download TWiLight Menu
    outputbox("Downloading TWiLight Menu ++\n")
    TWLmenuLocation = downloadFile(getLatestGitHub('DS-Homebrew/TWiLightMenu', 1), cwdtemp)

    if TWLmenuLocation is None:
        outputbox("TWiLight Menu not found, skipping...\n")
        print("TWiLight Menu not found, skipping...")
        return False

    outputbox("TWiLight Menu ++ Downloaded\n")
    print("TWiLight Menu ++ Downloaded")

    # Extract TWiLight Menu

    twlfolders = ['_nds', 'hiya', 'roms','title']
    twlfiles = ['BOOT.NDS', 'snemul.cfg']
    if un7zipper(zipfile=TWLmenuLocation, destination=cwdtemp, files=twlfolders + twlfiles) is False:
        outputbox("Failed to extract TWiLight Menu ++\n")
        print("Failed to extract TWiLight Menu ++")
        return False

    outputbox("TWiLight Menu ++ Extracted\n")
    print("TWiLight Menu ++ Extracted to", cwdtemp)

    # Move TWiLight Menu
    for folder in twlfolders:
        shutil.copytree(cwdtemp + folder, directory + "/" + folder + "/", dirs_exist_ok=True)
    for file in twlfiles:
        dest_filepath = os.path.join(directory, file)
        shutil.move(cwdtemp + file, dest_filepath)

    shutil.rmtree(cwdtemp + "_nds/")
    Path(cwdtemp + "_nds/").mkdir(parents=True, exist_ok=True)

    print("TWiLight  Menu ++ placed in", directory)
    outputbox("TWiLight Menu ++ placed on SD card\n")

    # Download DeadSkullzJr's Cheat Database
    download_DSJ_cheat_codes(directory)
    return True


def download_dumpTool(directory):
    outputbox("Downloading dumpTool\n")
    if downloadFile(getLatestGitHub('zoogie/dumpTool', 0), directory) is None:
        outputbox("Failed to download dumpTool\n")
        print("Failed to download dumpTool")
        return False
    print("dumpTool downloaded")
    outputbox("dumpTool Downloaded\n")
    return True


def download_Unlaunch(directory, cwdtemp):
    outputbox("Downloading Unlaunch\n")
    url = "https://web.archive.org/web/20210207235625if_/https://problemkaputt.de/unlaunch.zip"
    unlaunchLocation = downloadFile(url, cwdtemp)
    if unlaunchLocation is None:
        outputbox("Failed to download Unlaunch\n")
        print("Failed to download Unlaunch")
        return False
    print("Unlaunch Downloaded")
    outputbox("Unlaunch Downloaded\n")

    if not unzipper(unlaunchLocation, directory):
        print("Failed to extract Unlaunch")
        outputbox("Failed to extract Unlaunch\n")
        return False

    print("Unlaunch Extracted")
    outputbox("Unlaunch Extracted\n")
    return True


def download_GodMode9i(directory, cwdtemp, roms):
    # Download GodMode9i
    outputbox("Downloading GodMode9i\n")
    downloadLocation = downloadFile(getLatestGitHub('DS-Homebrew/GodMode9i', 0), cwdtemp)
    if downloadLocation is None:
        outputbox("Failed to download GodMode9i\n")
        print("Failed to download GodMode9i")
        return False
    print("GodMode9i downloaded")
    outputbox("GodMode9i Downloaded\n")

    if un7zipper(zipfile=downloadLocation, destination=cwdtemp, files=['GodMode9i/GodMode9i.nds']) is False:
        outputbox("Failed to extract GodMode9i\n")
        print("Failed to extract GodMode9i")
        return False

    shutil.copy(cwdtemp + "GodMode9i/GodMode9i.nds", roms)
    outputbox("GodMode9i Extracted\n")
    print("GodMode9i Extracted to", roms)
    return True


def download_hiyaCFW(directory, cwdtemp):
    # Check if old hiyaCFW insallation exists
    outputbox("Checking for hiyaCFW\n")
    if os.path.isfile(directory+"/hiya.dsi") is False:
        outputbox("hiya.dsi not found, skipping...\n")
        outputbox("Please run the hiyaCFW helper first\n")
        print("hiya.dsi not found, skipping...")
        print("Please run the hiyaCFW helper first")
        return False

    outputbox("hiyaCFW found...\n")
    outputbox("Downloading latest...\n")
    downloadLocation = downloadFile(getLatestGitHub("RocketRobz/hiyaCFW", 0), cwdtemp)
    if downloadLocation is None:
        outputbox("Failed to download hiyaCFW\n")
        print("Failed to download hiyaCFW")
        return False

    outputbox("hiyaCFW.7z downloaded\n")
    os.remove(directory+"/hiya.dsi")
    un7zipper(zipfile=downloadLocation, destination=directory, files=['for SDNAND SD card/hiya.dsi'])
    shutil.move(directory + "/for SDNAND SD card/hiya.dsi", directory + "/hiya.dsi")
    shutil.rmtree(directory + "/for SDNAND SD card/")
    return True


def download_additional_homebrew(directory, cwdtemp, roms):
    for count, item in enumerate(homebrewDB):
        if homebrewList[count].get() == 1:
            print("Downloading "+item["title"])
            outputbox("Downloading "+item["title"]+'\n')
            if item["github"] == "True":
                downloadlink = getLatestGitHub(item["repo"], int(item["asset"]))
            else:
                downloadlink = item["link"]
            if item["extension"] == "nds":
                downloadFile(downloadlink, roms)
                outputbox("Downloaded "+item["title"]+'\n')
            elif item["extension"] == "zip":
                downloadLocation = downloadFile(downloadlink, cwdtemp)
                if downloadLocation is not None:
                    if item["location"]["roms"] == "all":
                        unzipper(downloadLocation, roms)
                        outputbox("Downloaded "+item["title"]+'\n')
            elif item["extension"] == "7z":
                downloadLocation = downloadFile(downloadlink, cwdtemp)
                if downloadLocation is not None:
                    if item["location"]["roms"] == "all":
                        un7zipper(downloadLocation, roms)
                        outputbox("Downloaded "+item["title"]+'\n')
                    else:
                        un7zipper(downloadLocation, cwdtemp)
                        if "root" in item["location"]:
                            Path(directory+(item["location"]["root"].split('/')).pop()).mkdir(parents=True, exist_ok=True)
                            shutil.copy(cwdtemp+item["location"]["root"], directory+((item["location"]["root"].split('/')).pop().pop(0)))
                        if "roms" in item["location"]:
                            shutil.copy(cwdtemp+item["location"]["roms"], roms)
                        outputbox("Downloaded "+item["title"]+'\n')


def clean_up(cwdtemp):
    shutil.rmtree(cwdtemp)
    # Restore button access
    finalnextButton.config(state="normal")
    window.protocol("WM_DELETE_WINDOW", lambda: closeButtonPress(window))
    print("Done!")
    outputbox("Done!\n")
    outputbox("Press the Finish button to continue... \n")


def start():
    # Clear outputBox
    outputBox.configure(state='normal')
    outputBox.delete('1.0', tkinter.END)
    outputBox.configure(state='disabled')

    directory = SDentry
    if directory.endswith("\\") or directory.endswith("/"):
        directory = directory[:-1]
    # Validate directory
    if validateDirectory(directory) is False:
        finalbackButton.configure(state='normal')
        return

    # Creates a temporary directory for the files to be downloaded to
    cwdtemp = os.getcwd() + "/lazy-dsi-file-downloader-tmp/"
    Path(cwdtemp).mkdir(parents=True, exist_ok=True)

    if downloadmemorypit.get() == 1:
        download_MemoryPit(directory)

    if downloadtwlmenu.get() == 1:
        download_TWLMenu(directory, cwdtemp)

    if downloaddumptool.get() == 1:
        download_dumpTool(directory)

    if unlaunch.get() == 1:
        download_Unlaunch(directory, cwdtemp)

    roms = directory + "/roms/nds/"
    Path(roms).mkdir(parents=True, exist_ok=True)

    if godmode9i.get() == 1:
        download_GodMode9i(directory, cwdtemp, roms)

    if updateHiyaCFW.get() == 1:
        download_hiyaCFW(directory, cwdtemp)

    # Download and extract extra homebrew
    outputbox("Downloading other homebrew\n")
    print("Downloading other homebrew...")
    download_additional_homebrew(directory, cwdtemp, roms)

    clean_up(cwdtemp)
    return True


def chooseDir(source, SDentry):
    source.sourceFolder = tkinter.filedialog.askdirectory(
        parent=source, initialdir="/",
        title='Please select the root directory of your SD card')
    SDentry.delete(0, tkinter.END)
    SDentry.insert(0, source.sourceFolder)


def okButtonPress(self, source):
    self.destroy()
    source.deiconify()


def extraHomebrew(source):
    homebrewWindow = tkinter.Toplevel(source)
    homebrewWindow.config(bg="#f0f0f0")
    source.withdraw()
    homebrewWindowLabel = tkinter.Label(homebrewWindow, text="Homebrew List", font=("Segoe UI",12,"bold"), bg="#f0f0f0", fg="#000000")
    homebrewWindowLabel.pack(anchor="w")
    homebrewWindowLabel2 = tkinter.Label(homebrewWindow, text="Select additional homebrew for download then press OK", font=(bodyFont), bg="#f0f0f0", fg="#000000")
    homebrewWindowLabel2.pack(anchor="w")
    vscrollbar = tkinter.Scrollbar(homebrewWindow)
    canvas = tkinter.Canvas(homebrewWindow, yscrollcommand=vscrollbar.set)
    canvas.config(bg="#f0f0f0")
    vscrollbar.config(command=canvas.yview)
    vscrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    homebrewFrame = tkinter.Frame(canvas)
    homebrewFrame.configure(bg="#f0f0f0")
    homebrewWindow.title("Homebrew List")
    homebrewWindow.resizable(0, 0)
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window(0, 0, window=homebrewFrame, anchor="n")
    for count, x in enumerate(homebrewDB):
        homebrewListMenu = tkinter.Checkbutton(homebrewFrame, text=x["title"] + " by " + x["author"], font=(bigListFont), variable=homebrewList[count], bg="#f0f0f0", fg="#000000")
        homebrewListMenu.config(selectcolor="#F0F0F0")
        homebrewListMenu.pack(anchor = "w")
    frame = tkinter.ttk.Frame(homebrewWindow, relief=tkinter.RAISED, borderwidth=1)
    frame.pack(fill=tkinter.BOTH, expand=True)
    okButton = Button(homebrewWindow, text = "OK", font=(buttonFont), command=lambda: okButtonPress(homebrewWindow,source), bg="#f0f0f0", fg="#000000")
    okButton.pack(side=tkinter.RIGHT, padx=5, pady=5)
    homebrewWindow.update()
    canvas.config(scrollregion=canvas.bbox("all"))
    homebrewWindow.protocol("WM_DELETE_WINDOW", lambda: okButtonPress(homebrewWindow, source))


def closeButtonPress(source):
    source.destroy()
    root.destroy()


def nextWindow(windownumbertosummon):
    globals()["summonWindow"+windownumbertosummon]


def donothing():
    return


def summonWindow0():
    window.title("Lazy DSi file Downloader")
    window.resizable(0, 0)
    window.geometry("500x360")
    window.option_add("*Background", backgroundColour)
    window.configure(bg=backgroundColour)
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH, padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X, padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    first = tkinter.Label(topFrame, text="Lazy DSi File Downloader", font=(titleFont), fg=foregroundColour)
    first.grid(column=0, row=0, sticky="w", padx=5)
    bulletpoints = [
        "This program will download all files necessary to run homebrew on your Nintendo DSi.",
        "This is to be used in conjunction with the Nintendo DSi Modding guide by NightScript, emiyl and the rest of the community.",
        "Check it out here: https://dsi.cfw.guide/",
        "By using this application, you don't need to follow any of the 'Preparing SD card' steps.",
        "If you need help, join the Discord server with the button below.",
        "Please proceed by hitting the 'Next' button"
        ]

    for count, x in enumerate(bulletpoints):
        bullet = tkinter.Label(topFrame, text="• "+x, font=(paragraphFont), fg=foregroundColour, justify="left", wraplength=450)
        bullet.grid(column=0, row=count+3, sticky="w", padx=5)
    
    discordButton = Button(bottomFrame, text="DS⁽ⁱ⁾ Mode Hacking Discord server", fg=foregroundColour, bg=buttonColour, font=(buttonFont), command=lambda: webbrowser.open("https://discord.gg/yD3spjv", new=1))
    discordButton.pack(side=tkinter.LEFT, padx="5", pady="5")
    nextButton = Button(bottomFrame, text="Next", width=button_width, fg=foregroundColour, bg=nextButtonColour, font=(buttonFont), command=lambda: [topFrame.destroy(), bottomFrame.destroy(), summonWindow1()])
    nextButton.pack(side=tkinter.RIGHT, padx=5, pady=5)

    window.protocol("WM_DELETE_WINDOW", lambda: closeButtonPress(window))


def summonWindow1():
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH, padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X, padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    first = tkinter.Label(topFrame, text="Memory Pit", font=(titleFont), fg=foregroundColour)
    first.grid(column=0, row=0, sticky="w", padx=5)
    subtitle = tkinter.Label(topFrame, text='thank you, shutterbug2000!', font=(subtitleFont), fg=foregroundColour)
    subtitle.grid(column=0, row=1, sticky="w", padx=5)
    filler = tkinter.Label(topFrame, text=" ")
    filler.grid(column=0, row=3)
    downloadmemorypitCheck = tkinter.Checkbutton(topFrame, text = "Download Memory pit exploit?", font=(buttonFont), fg=foregroundColour, variable = downloadmemorypit)
    downloadmemorypitCheck.grid(column=0, row=2, sticky="w")
    instrctionlabel = tkinter.Label(topFrame, text="Check your DSi Camera Version:", font=(paragraphFont), fg=foregroundColour, wraplength=450)
    instrctionlabel.grid(column=0, row=3, sticky="w", padx=5)
    instructions = [
        "1. Power on your console",
        "2. Open the Nintendo DSi camera app",
        "3. Open the album with the button on the right",
        "4. Check for a Facebook (blue f) icon alongside the star, clubs and hearts icons"
    ]
    for count, instruction in enumerate(instructions):
        instrctionlabel = tkinter.Label(topFrame, text=instruction, font=(instructionFont), fg=foregroundColour, justify="left", wraplength=450)
        instrctionlabel.grid(column=0, row=count+4, sticky="w", padx=5)
    facebookIconCheck = tkinter.Checkbutton(topFrame, text = "Is the Facebook Icon present?", fg=foregroundColour, bg=buttonColour, font=(buttonFont), variable=facebookIcon)
    facebookIconCheck.grid(column=0, row=9, sticky="w")

    if platform.system() == "Darwin":
        macOS_hiddentext = tkinter.Label(topFrame, text = "(Click the area above this text\n if you can't see the drop down menu) ", fg=foregroundColour, font=(bodyFont))
        macOS_hiddentext.grid(column=0, row=6, sticky="w")

    backButton = Button(bottomFrame,text="Back", font=(buttonFont), fg=foregroundColour, bg=backButtonColour, command=lambda: [topFrame.destroy(),bottomFrame.destroy(),summonWindow0()], width=button_width)
    backButton.pack(side=tkinter.LEFT)
    nextButton = Button(bottomFrame, text="Next",width=button_width, fg=foregroundColour, bg=nextButtonColour, font=(buttonFont),command=lambda: [topFrame.destroy(), bottomFrame.destroy(), summonWindow2()])
    nextButton.pack(side=tkinter.RIGHT, padx=5, pady=5)
    window.protocol("WM_DELETE_WINDOW", lambda: closeButtonPress(window))


def summonWindow2():
    topFrame = tkinter.Frame(window)
    topFrame.pack(expand=True, fill=tkinter.BOTH, padx=5)
    topFrame.option_add("*Background", backgroundColour)
    bottomFrame = tkinter.Frame(window)
    bottomFrame.pack(side=tkinter.BOTTOM, fill=tkinter.X,padx=5)
    bottomFrame.option_add("*Background", backgroundColour)
    first = tkinter.Label(topFrame, text="Homebrew Section", font=(titleFont), fg=foregroundColour)
    first.grid(column=0,row=0, sticky="w")
    subtitle = tkinter.Label(topFrame, text='brewed at home', font=(subtitleFont), fg=foregroundColour)
    subtitle.grid(column=0,row=1,sticky="w")
    downloadtwlmenuCheck = tkinter.Checkbutton(topFrame, text = "Download latest TWiLight Menu++ version?",fg=foregroundColour, variable = downloadtwlmenu,font=(buttonFont))
    downloadtwlmenuCheck.grid(column=0,row=2, sticky ="w")
    downloaddumptoolCheck = tkinter.Checkbutton(topFrame, text ="Download latest dumpTool version?", variable=downloaddumptool,fg=foregroundColour,font=(buttonFont))
    downloaddumptoolCheck.grid(column=0,row=3,sticky="w")
    unlaunchCheck = tkinter.Checkbutton(topFrame, text = "Download latest Unlaunch version?", variable =unlaunch, fg=foregroundColour,font=(buttonFont))
    unlaunchCheck.grid(column=0,row=4,sticky="w")
    seperator = tkinter.Label(topFrame, text="───────────────────────────────────────────────────────────", font=(buttonFont), fg=foregroundColour)
    seperator.grid(column=0,row=5,sticky="w")
    GodMode9iCheck = tkinter.Checkbutton(topFrame, text = "Download latest GodMode9i version?", variable =godmode9i, fg=foregroundColour,font=(buttonFont))
    GodMode9iCheck.grid(column=0,row=6,sticky="w")
    updateHiyaCheck = tkinter.Checkbutton(topFrame, text = "Update hiyaCFW? (must have run hiyaHelper once before)", variable =updateHiyaCFW, fg=foregroundColour,font=(buttonFont))
    updateHiyaCheck.grid(column=0,row=7,sticky="w")
    buttonExtraHomebrew = tkinter.Button(topFrame, text = "Click to add Additional homebrew...", command =lambda:[extraHomebrew(window)], fg=foregroundColour,font=(buttonFont),bg=buttonColour)
    buttonExtraHomebrew.grid(column=0,row=8,sticky="w",pady=5)
    backButton = Button(bottomFrame,text="Back", font=(buttonFont),fg=foregroundColour,bg=backButtonColour,command=lambda: [topFrame.destroy(),bottomFrame.destroy(),summonWindow1()], width=button_width)
    backButton.pack(side=tkinter.LEFT)
    nextButton = Button(bottomFrame, text="Next",width=button_width, fg=foregroundColour,bg=nextButtonColour, font=(buttonFont),command=lambda:[topFrame.destroy(),bottomFrame.destroy(),summonWindow3()])
    nextButton.pack(side=tkinter.RIGHT, padx=5, pady=5)
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
    noticeLabel=tkinter.Label(topFrame,text="Plug in your SD card and select the root directory :", fg=foregroundColour, font=(buttonFont))
    noticeLabel.grid(column=0,row=2,sticky="w")
    SDentry = tkinter.Entry(topFrame, fg=foregroundColour,bg=buttonColour,font=(buttonFont),width=35)
    SDentry.grid(column=0, row=3,sticky="w")
    chooseDirButton = Button(topFrame, text = "Click to select folder", command =lambda:chooseDir(topFrame,SDentry),fg=foregroundColour,bg=buttonColour,font=(buttonFont),width=folder_width)
    chooseDirButton.grid(column=0, row=4,sticky="w",pady=5)
    backButton = Button(bottomFrame,text="Back", font=(buttonFont),fg=foregroundColour,bg=backButtonColour,command=lambda: [topFrame.destroy(),bottomFrame.destroy(),summonWindow2()], width=button_width)
    backButton.pack(side=tkinter.LEFT)
    nextButton = Button(bottomFrame, text="Start",width=button_width, fg=foregroundColour,bg=nextButtonColour, font=(buttonFont),command=lambda:[globalify(SDentry.get()),topFrame.destroy(),bottomFrame.destroy(),summonWindow4()])
    nextButton.pack(side=tkinter.RIGHT, padx=5, pady=5)
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
    finalbackButton = Button(bottomFrame,state="disabled",  text="Back", font=(buttonFont),fg=foregroundColour,bg=backButtonColour,command=lambda: [topFrame.destroy(),bottomFrame.destroy(),summonWindow3()], width=button_width)
    finalbackButton.pack(side=tkinter.LEFT)
    global finalnextButton
    finalnextButton = Button(bottomFrame, state="disabled", text="Finish",width=button_width, fg=foregroundColour,bg=nextButtonColour, font=(buttonFont),command=lambda:[topFrame.destroy(),bottomFrame.destroy(),summonWindow5()])
    finalnextButton.pack(side=tkinter.RIGHT, padx=5, pady=5)
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
    label= tkinter.Label(topFrame,text="Your SD card is now ready to run and use Homebrew on your Nintendo DSi.",font=(bodyFont),fg=foregroundColour,wraplength=450,justify="left")
    label.grid(column=0,row=2,sticky="w")
    linktoguide = tkinter.Button(topFrame, text="Return to dsi.cfw.guide", command=lambda: webbrowser.open_new("https://dsi.cfw.guide/launching-the-exploit.html#section-iii-launching-the-exploit="),fg=foregroundColour,bg=buttonColour,font=(buttonFont),width=guidebuttonwidth)
    linktoguide.grid(column=0,row=3,sticky="w")
    label= tkinter.Label(topFrame,text="Rerunning this application will automatically update existing homebrew on the SD card",font=(bodyFont),fg=foregroundColour, wraplength=450,justify="left")
    label.grid(column=0,row=5,sticky="w")
    label= tkinter.Label(topFrame,text="Press the Close button to Exit",font=(bodyFont),fg=foregroundColour)
    label.grid(column=0,row=6,sticky="w")
    finish = Button(bottomFrame, text="Close", width=button_width, fg=foregroundColour, bg=nextButtonColour, font=(buttonFont),command=lambda: [topFrame.destroy(), bottomFrame.destroy(), closeButtonPress(window)])
    finish.pack(side=tkinter.RIGHT, padx=5, pady=5)
    window.protocol("WM_DELETE_WINDOW",lambda:closeButtonPress(window))


if __name__ == "__main__":
    if(sys.version_info.major < 3):
        print("This program will ONLY work on Python 3 and above")
        sys.exit()
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    root = tkinter.Tk()
    window = tkinter.Toplevel(root)
    root.withdraw()

    # Homebrew Database
    homebrewDB = json.loads(requests.get('https://raw.githubusercontent.com/YourKalamity/just-a-dsi-DB/master/just-a-dsi-DB.json').content)
    homebrewList = []
    for x in homebrewDB:
        homebrewList.append(tkinter.IntVar())

    # TKinter Vars
    downloadmemorypit = tkinter.IntVar(value=1)
    facebookIcon = tkinter.IntVar(value=1)
    downloadtwlmenu = tkinter.IntVar(value=1)
    downloaddumptool = tkinter.IntVar(value=1)
    unlaunch = tkinter.IntVar(value=1)
    godmode9i = tkinter.IntVar(value=0)
    updateHiyaCFW = tkinter.IntVar(value=0)

    # Fonts
    titleFont = tkinter.font.Font(
        family="Segoe UI",
        size=15,
        weight="bold"
    )
    subtitleFont = tkinter.font.Font(
        family="Segoe UI",
        size=11,
        slant="italic"
    )
    bodyFont = tkinter.font.Font(
        family="Segoe UI",
        underline=False,
        size=11
    )
    buttonFont = tkinter.font.Font(
        family="Segoe UI",
        underline=False,
        size=11,
        weight="bold"
    )
    bigListFont = tkinter.font.Font(
        family="Segoe UI",
        underline=False,
        size=9
    )
    paragraphFont = tkinter.font.Font(
        family="Segoe UI",
        size=12
    )
    instructionFont = tkinter.font.Font(
        family="Segoe UI",
        size=10
    )

    if platform.system() == "Darwin":
        from tkmacosx import Button
        backgroundColour = "#f0f0f0"
        foregroundColour = "black"
        buttonColour = "#f0f0f0"
        backButtonColour = "#f0f0f0"
        nextButtonColour = "#f0f0f0"
        button_width = 80
        guidebuttonwidth = 200
        folder_width = 350
    else:
        from tkinter import Button
        backgroundColour = "#252a34"
        foregroundColour = "white"
        buttonColour = "#7289DA"
        backButtonColour = "#567487"
        nextButtonColour = "#027b76"
        button_width = 8
        guidebuttonwidth = 20
        folder_width = 35

    summonWindow0()
    root.mainloop()
