import sys
from typing import Type
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtUiTools import QUiLoader
import resources
import requests
import json
import os
import platform
from subprocess import Popen
import distutils
from distutils import dir_util
import shutil
from pathlib import Path
import zipfile
import threading

dsiVersions = [
    "1.0 - 1.3 (USA, EUR, AUS, JPN)",
    "1.4 - 1.4.5 (USA, EUR, AUS, JPN)",
    "All versions (KOR, CHN)"
]

linkToRepo = "https://github.com/YourKalamity/lazy-dsi-file-downloader"

memoryPitLinks = [
    linkToRepo + "/raw/master/assets/files/memoryPit/256/pit.bin",
    linkToRepo + "/raw/master/assets/files/memoryPit/768_1024/pit.bin"
]


def current_operation_output(widget, message):
    widget.current_operation.setText(message)
    print(message)
    return


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
    except requests.exceptions.ConnectionError:
        current_operation_output(widget, "File not available, skipping...")
        return None


def getLatestGitHub(usernamerepo, assetNumber):
    release = json.loads(
        requests.get(
            "https://api.github.com/repos/"+usernamerepo+"/releases/latest"
        ).content)
    url = release["assets"][assetNumber]["browser_download_url"]
    return url


def unzipper(unzipped, destination):
    with zipfile.ZipFile(unzipped, 'r') as zip_ref:
        zip_ref.extractall(destination)
        zip_ref.close()


def un7zipper(_7za, zipfile, destination):
    un7zipper = Popen([_7za, "x", "-aoa", zipfile, '-o'+destination])
    un7zipper.wait()


def validate_directory(directory):
    try:
        directory = str(directory)
        string = directory + "/test.file"
        with open(string, 'w') as file:
            file.close()
        os.remove(string)
    except TypeError or FileNotFoundError:
        current_operation_output(widget, "That's not a valid directory!")
        return False
    except PermissionError:
        current_operation_output(widget, "You don't have permission to access that directory!")
        return False
    return True


def get_root(path):
    if os.name == 'nt':
        path = path[:3]
        path = path.replace('\\', '/')
    else:
        temp = path
        orig_dev = os.stat(temp).st_dev
        while temp != '/':
            direc = os.path.dirname(temp)
            if os.stat(direc).st_dev != orig_dev:
                break
            temp = direc
        path = temp
    return path


def change_locked_state(widget, state):
    if state == "locked":
        for tab in range(0, widget.tabWidget.count() - 1):
            widget.tabWidget.setTabEnabled(tab, False)
        widget.previous_page3.setEnabled(False)
        widget.Finish.setEnabled(False)
    elif state == "unlocked":
        for tab in range(0, widget.tabWidget.count()):
            widget.tabWidget.setTabEnabled(tab, True)
        widget.previous_page3.setEnabled(True)
        widget.Finish.setEnabled(False)
    elif state == "finished":
        widget.Finish.setEnabled(True)

def get_num_steps(widget):
    steps = 2
    if widget.MemoryPitCheckBox.isChecked():
        steps += 1
    if widget.TWLMenuCheckBox.isChecked():
        steps += 1
    if widget.dumpToolCheckBox.isChecked():
        steps += 1
    if widget.UnlaunchCheckBox.isChecked():
        steps += 1
    if widget.GodMode9iCheckBox.isChecked():
        steps += 1
    if widget.hiyaCheckBox.isChecked():
        steps += 1
    for count, item in enumerate(homebrewDB):
        if homebrewlist[count].isChecked():
            steps += 1
    return steps


def update_step_count(widget, steps, original_steps):
    widget.step_counter.setText("Step " + str(steps) + " of " + str(original_steps))


def start(widget):
    original_steps = get_num_steps(widget)
    steps = 0
    update_step_count(widget, steps, original_steps)
    widget.tabWidget.setTabEnabled(5, True)
    change_page(widget, "forward")
    change_locked_state(widget, "locked")
    current_operation_output(widget, "Searching for 7-Zip...")
    sysname = platform.system()
    _7za = os.path.join(sysname, '7za')
    _7z = None
    if sysname in ["Darwin", "Linux"]:
        # Chmod 7z binary to avoid a permission error
        import stat
        os.chmod(_7za, stat.S_IRWXU)
    if sysname == "Windows":
        # Search for 7z in the 64-bit Windows Registry
        import winreg
        current_operation_output(widget, 'Searching for 7-Zip in the Windows registry...')
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                'SOFTWARE\\7-Zip', 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY
            ) as hkey:
                _7z = os.path.join(winreg.QueryValueEx(
                    hkey, 'Path')[0], '7z.exe')

                if not os.path.exists(_7z):
                    raise WindowsError
                _7za = _7z
        except WindowsError:
            # Search for 7z in the 32-bit Windows Registry
            current_operation_output(widget, 'Searching for 7-Zip in the 32-bit Windows registry...')

            try:
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\7-Zip'
                ) as hkey:
                    _7z = os.path.join(winreg.QueryValueEx(hkey, 'Path')[0], '7z.exe')

                    if not os.path.exists(_7z):
                        raise WindowsError
                    _7za = _7z
            except WindowsError:
                current_operation_output(widget, "7-Zip not found, please install it before using")
                change_locked_state(widget, "unlocked")
                return
    steps += 1
    update_step_count(widget, steps, original_steps)
    current_operation_output(widget, "7-Zip found!")

    current_operation_output(widget, "Checking SD Directory...")
    if not validate_directory(widget.SDDirectoryInput.text()):
        change_locked_state(widget, "unlocked")
        return

    cwd_temp = os.getcwd() + "/lazy-dsi-file-downloader-tmp/"
    try:
        Path(cwd_temp).mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass
    except PermissionError:
        current_operation_output(widget, "Please run this program from a different location")
        change_locked_state(widget, "unlocked")
        return

    current_operation_output(widget, "Finding SD root...")
    sd_path = get_root(widget.SDDirectoryInput.text())
    current_operation_output(widget, "SD root found!")

    steps += 1
    update_step_count(widget, steps, original_steps)

    if widget.MemoryPitCheckBox.isChecked():
        current_operation_output(widget, "Downloading Memory Pit...")
        if widget.fwComboBox.currentIndex() == 1:
            memoryPitDownload = memoryPitLinks[1]
        else:
            memoryPitDownload = memoryPitLinks[0]
        memoryPitLocation = sd_path + "/private/ds/app/484E494A/"
        Path(memoryPitLocation).mkdir(parents=True, exist_ok=True)
        downloadLocation = downloadFile(memoryPitDownload, memoryPitLocation)
        if downloadLocation is not None:
            current_operation_output(widget, "Memory Pit downloaded!")
        steps += 1
        update_step_count(widget, steps, original_steps)
    
    if widget.TWLMenuCheckBox.isChecked():
        current_operation_output(widget, "Downloading TWiLight Menu ++...")
        TWLmenuLocation = downloadFile(getLatestGitHub('DS-Homebrew/TWiLightMenu', 1), cwd_temp)
        if TWLmenuLocation is not None:
            current_operation_output(widget, "TWiLight Menu ++ downloaded!")
            current_operation_output(widget, "Extracting...")
            proc = Popen([_7za,"x", "-aoa", TWLmenuLocation, '-o'+cwd_temp, '_nds', 'hiya', 'roms','title', 'BOOT.NDS','snemul.cfg'])
            proc.wait()
            current_operation_output(widget, "TWiLight Menu ++ extracted!")
            
            current_operation_output(widget, "Copying TWiLight Menu ++...")
            shutil.copy(cwd_temp + "BOOT.NDS", sd_path)
            distutils.dir_util.copy_tree(cwd_temp + "_nds/", sd_path + "/_nds/")
            distutils.dir_util.copy_tree(cwd_temp + "hiya", sd_path + "/hiya/")
            distutils.dir_util.copy_tree(cwd_temp + "title", sd_path + "/title/")
            distutils.dir_util.copy_tree(cwd_temp + "roms", sd_path + "/roms/")
            shutil.rmtree(cwd_temp+"_nds/")
            Path(cwd_temp + "_nds/").mkdir(parents=True, exist_ok=True)
            current_operation_output(widget, "TWiLight Menu ++ copied!")

            Path(sd_path + "/_nds/TWiLightMenu/extras/").mkdir(parents=True, exist_ok=True)
            current_operation_output(widget, "Downloading DeadSkullzJr's Cheat Database")
            downloadLocation = downloadFile('https://bitbucket.org/DeadSkullzJr/nds-cheat-databases/raw/933c375545d3ff90854d1e210dcf4b3b31d9d585/Cheats/usrcheat.dat', sd_path + "/_nds/TWiLightMenu/extras/")
            if downloadLocation is not None:
                current_operation_output(widget, "DeadSkullzJr's Cheat Database downloaded!")
            steps += 1
            update_step_count(widget, steps, original_steps)

    if widget.dumpToolCheckBox.isChecked():
        current_operation_output(widget, "Downloading dumpTool...")
        downloadLocation = downloadFile(getLatestGitHub('zoogie/dumpTool', 0), sd_path)
        if downloadLocation is not None:
            current_operation_output(widget, "dumpTool downloaded!")
        steps += 1
        update_step_count(widget, steps, original_steps)
    
    if widget.UnlaunchCheckBox.isChecked():
        url = "https://web.archive.org/web/20210207235625if_/https://problemkaputt.de/unlaunch.zip"
        current_operation_output(widget, "Downloading Unlaunch...")
        unlaunchLocation = downloadFile(url, cwd_temp)
        if unlaunchLocation is not None:
            current_operation_output(widget, "Unlaunch downloaded!")
            current_operation_output(widget, "Extracting...")
            unzipper(unlaunchLocation, sd_path)
            current_operation_output(widget, "Unlaunch extracted!")
        steps += 1
        update_step_count(widget, steps, original_steps)

    roms = sd_path + "/roms/nds/"
    Path(roms).mkdir(parents=True, exist_ok=True)

    if widget.GodMode9iCheckBox.isChecked():
        current_operation_output(widget, "Downloading GodMode9i...")
        downloadLocation = downloadFile(getLatestGitHub('DS-Homebrew/GodMode9i', 0), cwd_temp)
        if downloadLocation is not None:
            current_operation_output(widget, "GodMode9i downloaded!")
            current_operation_output(widget, "Extracting...")
            proc = Popen([_7za,"x", "-aoa", downloadLocation, '-o'+roms, 'GodMode9i.nds'])
            proc.wait()
            current_operation_output(widget, "GodMode9i extracted!")
        steps += 1
        update_step_count(widget, steps, original_steps)

    if widget.hiyaCheckBox.isChecked():
        current_operation_output(widget, "Checking for hiyaCFW...")
        if os.path.exists(sd_path + "/hiya.dsi"):
            current_operation_output(widget, "hiyaCFW found!")
            current_operation_output(widget, "Downloading latest hiyaCFW...")
            downloadLocation = downloadFile(getLatestGitHub("RocketRobz/hiyaCFW", 0), cwd_temp)
            if downloadLocation is not None:
                current_operation_output(widget, "hiyaCFW downloaded!")
                os.remove(sd_path+"/hiya.dsi")
                current_operation_output(widget, "Extracting...")
                proc = Popen([_7za,"x","-aoa",downloadLocation, "-o" + sd_path ,"for SDNAND SD card\hiya.dsi"])
                proc.wait()
                shutil.move(sd_path + "/for SDNAND SD card/hiya.dsi", sd_path + "/hiya.dsi")
                shutil.rmtree(sd_path + "/for SDNAND SD card/")
                current_operation_output(widget, "hiyaCFW extracted!")
        else:
            current_operation_output(widget, "hiyaCFW not found!")
            current_operation_output(widget, "Please run hiyaCFW helper first!")
        steps += 1
        update_step_count(widget, steps, original_steps)

    current_operation_output(widget, "Downloading Extra Homebrew...")
    for count, item in enumerate(homebrewDB):
        if homebrewlist[count].isChecked():
            current_operation_output(widget, "Downloading " + item["title"] + "...")
            if item["github"] == "True":
                downloadlink = getLatestGitHub(item["repo"], int(item["asset"]))
            else:
                downloadlink = item["link"]
            if item["extension"] == "nds":
                downloadFile(downloadlink, roms)
                current_operation_output(widget, "Downloaded " + item["title"] + "!")
            elif item["extension"] == "zip":
                downloadLocation = downloadFile(downloadlink, cwd_temp)
                if downloadLocation is not None:
                    current_operation_output(widget, "Downloaded " + item["title"] + "!")
                    current_operation_output(widget, "Extracting...")
                    unzipper(downloadLocation, roms)
                    current_operation_output(widget, "Extracted " + item["title"] + "!")
            elif item["extension"] == "7z":
                downloadLocation = downloadFile(downloadlink, cwd_temp)
                if downloadLocation is not None:
                    current_operation_output(widget, "Downloaded " + item["title"] + "!")
                    if item["location"]["roms"] == "all":
                        un7zipper(_7za, downloadLocation, roms)
                        current_operation_output(widget, "Extracted " + item["title"] + "!")
                    else:
                        un7zipper(_7za, downloadLocation, roms + cwd_temp)
                        current_operation_output(widget, "Extracted " + item["title"] + "!")
                        if "root" in item["location"]:
                            Path(sd_path+(item["location"]["root"].split('/')).pop()).mkdir(parents=True, exist_ok=True)
                            shutil.copy(cwd_temp+item["location"]["root"], sd_path+((item["location"]["root"].split('/')).pop().pop(0)))
                        if "roms" in item["location"]:
                            shutil.copy(cwd_temp+item["location"]["roms"], roms)
                        current_operation_output(widget, "Copied " + item["title"] + "!")
            steps += 1
            update_step_count(widget, steps, original_steps)

    shutil.rmtree(cwd_temp)
    current_operation_output(widget, "Done! Press Finish to exit.")
    change_locked_state(widget, "finished")


def change_page(widget, direction):
    if direction == "forward":
        widget.tabWidget.setCurrentIndex(widget.tabWidget.currentIndex() + 1)
    elif direction == "backward":
        widget.tabWidget.setCurrentIndex(widget.tabWidget.currentIndex() - 1)


def start_thread(widget):
    thread = threading.Thread(target=start, args=(widget,))
    thread.start()


def set_up(widget):
    widget.next_page0.clicked.connect(lambda: change_page(widget, "forward"))
    widget.next_page1.clicked.connect(lambda: change_page(widget, "forward"))
    widget.next_page2.clicked.connect(lambda: change_page(widget, "forward"))
    widget.StartButton.clicked.connect(lambda: start_thread(widget))
    widget.next_page4.clicked.connect(lambda: change_page(widget, "forward"))
    widget.previous_page0.clicked.connect(lambda: change_page(widget, "backward"))
    widget.previous_page1.clicked.connect(lambda: change_page(widget, "backward"))
    widget.previous_page2.clicked.connect(lambda: change_page(widget, "backward"))
    widget.previous_page3.clicked.connect(lambda: change_page(widget, "backward"))
    widget.previous_page4.clicked.connect(lambda: change_page(widget, "backward"))
    widget.FileDialogOpenButton.clicked.connect(lambda: get_SD_path(widget))
    widget.Finish.clicked.connect(lambda: sys.exit(app.exec()))
    widget.tabWidget.setTabEnabled(5, False)


def add_item_to_additional_homebrew(widget, item):
    checkbox = QtWidgets.QCheckBox(item)
    checkbox.resize(checkbox.sizeHint())
    widget.scrollAreaWidgetContents.layout().addWidget(checkbox)
    checkbox.setMinimumHeight(30)
    return checkbox


def add_homebrew_to_list(widget):
    homebrewDB = json.loads(
        requests.get(
            'https://raw.githubusercontent.com/YourKalamity/just-a-dsi-DB/master/just-a-dsi-DB.json'
            ).content)
    homebrewList = []
    for count, item in enumerate(homebrewDB):
        homebrewList.append(
            add_item_to_additional_homebrew(
                widget, f"{item['title']} - {item['author']}"
                ))
    return homebrewList, homebrewDB


def get_SD_path(widget):
    path = QtWidgets.QFileDialog().getExistingDirectory(
        widget, "Select SD card path")
    path = get_root(path)
    widget.SDDirectoryInput.setText(path)


if __name__ == "__main__":
    loader = QUiLoader()
    app = QtWidgets.QApplication(sys.argv)
    widget = loader.load("gui.ui")
    homebrewlist, homebrewDB = add_homebrew_to_list(widget)
    set_up(widget)
    widget.show()
    sys.exit(app.exec())
