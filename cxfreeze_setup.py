#!/usr/bin/env python3

from cx_Freeze import setup, Executable


build_exe_options = {'build_exe': "dist", "include_msvcr":True}
base = None

setup(
    name="lazy-dsi-file-downloader",
    version="3.2.2",
    description="Lazy DSi File Downloader",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)],
)
