from cx_Freeze import setup, Executable

# Create Windows installer: python ./setup.py bdist_msi
# Create Mac disk image: python ./setup.py bdist_dmg --applications-shortcut

# Dependencies are automatically detected, but it might need fine-tuning.
build_options_exe = {'packages': ['PIL', 'cursepy', 'modrinth'], 'include_files': ['icon.png']}
build_options_msi = {'install_icon': 'icon.png', 'target_name': 'Modlist Manager v0.2.msi'}
build_options_app = {'iconfile': 'icon.png', 'bundle_name': 'Modlist Manager'}
build_options_dmg = {'applications_shortcut': True, 'volume_label': 'Modlist Manager v0.2'}

base = 'gui'

executables = [
    Executable('main.py', base=base, target_name='Modlist Manager', icon='icon.png')
]

setup(name='Modlist Manager',
      version='0.2',
      description='Automatically maintain and download your custom Minecraft mods',
      options={'build_exe': build_options_exe,
               'bdist_msi': build_options_msi,
               'bdist_mac': build_options_app,
               'bdist_dmg': build_options_dmg},
      executables=executables)
