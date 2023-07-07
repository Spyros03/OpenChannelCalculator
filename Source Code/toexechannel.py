import sys
from cx_Freeze import setup, Executable


# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {"packages": ["os"], "excludes": []}
bdist_msi_options = {"all_users": True}

# base="Win32GUI" should be used only for Windows GUI app
if sys.platform == "win32":
    base = "Win32GUI"
    ico = "icon.png"

else:
    base = None
    ico = "icon.png"



setup(
    name="Open Channel Calculator",
    version="1.0",
    description="This program uses the Mannings equation to Calculate the flow properties of diffrent cross sections",
    options={"build_exe": build_exe_options,
             "bdist_msi": bdist_msi_options
            },
    executables=[Executable("mainwindow.py", base=base, icon=ico),             #Thanasis2017_03_17:http://stackoverflow.com/questions/15117772/icon-not-showing-in-pyqt-application-exe-when-built-using-cx-freeze
                 Executable("mainwindow.py", base=base, icon=ico)
                ],
)
