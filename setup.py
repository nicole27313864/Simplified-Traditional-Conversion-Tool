import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_exe_options = {"packages": ["os", "PySide6", "re", "opencc", "qt_material"], "excludes": ["tkinter"], "include_files": ["fonts/"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="ZH-Document-Conversion-Tool",
    version="1.0",
    description="Convert documents from Simplified Chinese to Traditional Chinese",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)
