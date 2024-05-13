from cx_Freeze import setup, Executable

# Create Windows installer: python ./setup.py bdist_msi
# Create Mac disk image: python ./setup.py bdist_dmg

# Dependencies are automatically detected, but it might need fine-tuning.
build_options_exe = {'packages': ['PIL', 'cursepy', 'modrinth'], 'include_files': ['icon.png']}
build_options_msi = {'install_icon': 'icon.png', 'target_name': 'Modlist Manager'}
build_options_app = {'iconfile': 'icon.png', 'bundle_name': 'Modlist Manager'}
build_options_dmg = {'applications_shortcut': True, 'volume_label': 'Modlist Manager-0.2-mac'}

base = 'gui'

executables = [
    Executable('main.py', base=base, target_name='Modlist Manager', icon='icon',
               shortcut_name='Modlist Manager', shortcut_dir='ProgramMenuFolder')
]

setup(name='Modlist Manager',
      version='0.2',
      description='Modlist Manager',
      author='Niclas Rogulski',
      url='https://github.com/IronExcavater/Modlist-Manager',
      license='MIT',
      options={'build_exe': build_options_exe,
               'bdist_msi': build_options_msi,
               'bdist_mac': build_options_app,
               'bdist_dmg': build_options_dmg},
      executables=executables)
