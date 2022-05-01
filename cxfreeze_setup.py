#!/usr/bin/env python3

from cx_Freeze import setup, Executable
import platform

build_exe_options = {'build_exe': "dist"}

base = None
if platform.system() == "Windows":
    base = "Win32GUI"

setup(
    name="lazy-dsi-file-downloader",
    version="3.1.5",
    description="Lazy DSi File Downloader",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)],
)
