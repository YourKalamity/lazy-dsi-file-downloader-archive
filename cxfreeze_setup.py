#!/usr/bin/env python3

from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {'build_exe': "dist"}

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI"

setup(
    name="lazy-dsi-file-downloader",
    version="3.1.3",
    description="Lazy DSi File Downloader",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)],
)
