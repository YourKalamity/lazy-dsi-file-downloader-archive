#!/usr/bin/env python3
import sys
from cx_Freeze import setup, Executable

include_files = ["README.md", "LICENSE", "resources.qrc", "gui.ui", "lazy.ico"]
build_exe_options = {'build_exe': "dist", "include_files": include_files}

base = None
if sys.platform == 'win32':
    base = "Win32GUI"

setup(
    name="lazy-dsi-file-downloader",
    version="3.1.3",
    description="Lazy DSi File Downloader",
    author="YourKalamity",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)],
)
