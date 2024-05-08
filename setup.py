from cx_Freeze import setup, Executable

# To create a new windows build: python ./setup.py bdist_msi

# Dependencies are automatically detected, but it might need fine tuning.
build_options = {'packages': ['tkinter', 'PIL', 'modrinth'], 'include_files': ['icon.png']}

base = 'gui'

executables = [
    Executable('main.py', base=base, target_name='Modlist Manager')
]

setup(name='Modlist Manager',
      version='0.1',
      description='Automatically maintain and download your custom Minecraft mods',
      options={'build_exe': build_options},
      executables=executables)
