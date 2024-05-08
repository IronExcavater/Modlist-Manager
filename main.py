import os
import sys
import re
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import sv_ttk
import webbrowser
from urllib.request import *
from urllib.error import *
from bs4 import BeautifulSoup
from PIL import Image, ImageTk

mcversions = (
    '1.20.5', '1.20.4', '1.20.3', '1.20.2', '1.20.1', '1.20',
    '1.19.4', '1.19.3', '1.19.2', '1.19.1', '1.19',
    '1.18.2', '1.18.1', '1.18',
    '1.17.1', '1.17',
    '1.16.5', '1.16.4', '1.16.3', '1.16.2', '1.16.1', '1.16',
    '1.15.2', '1.15.1', '1.15',
    '1.14.4', '1.14.3', '1.14.2', '1.14.1', '1.14',
    '1.13.2', '1.13.1', '1.13',
    '1.12.2', '1.12.1', '1.12',
    '1.11.2', '1.11.1', '1.11',
    '1.10.2', '1.10.1', '1.10',
    '1.9.4', '1.9.3', '1.9.2', '1.9',
    '1.8.9', '1.8.8', '1.8.7', '1.8.6', '1.8.5', '1.8.4', '1.8.3', '1.8.2', '1.8.1', '1.8',
    '1.7.10', '1.7.9', '1.7.8', '1.7.7', '1.7.6', '1.7.5', '1.7.4', '1.7.2',
    '1.6.4', '1.6.2', '1.6.1',
    '1.5.2', '1.5.1', '1.5',
    '1.4.7', '1.4.6', '1.4.5', '1.4.4', '1.4.2',
    '1.3.2', '1.3.1',
    '1.2.5', '1.2.4', '1.2.3', '1.2.2', '1.2.1',
    '1.1',
    '1.0.1', '1.0.0'
)

modloaders = (
    'Fabric', 'Forge', 'Quilt', 'NeoForge'
)

requestheader = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 '
                  'Safari/537.36 OPR/107.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'
}

if sys.platform == 'darwin':
    pointerhand = 'pointinghand'
else:
    pointerhand = 'hand2'

modlists_directory = Path('modlists')
icons_directory = Path('icons')

if not os.path.exists(modlists_directory):
    os.mkdir(modlists_directory)

if not os.path.exists(icons_directory):
    os.mkdir(icons_directory)


def get_modrinth_page(url_name):
    page = urlopen(Request(f'https://modrinth.com/mod/{url_name}', headers=requestheader))
    return BeautifulSoup(page, 'html.parser')


def get_mod_name(soup) -> str:
    return soup.find('h1', class_='title').text


def get_mod_icon(soup, name):
    img_tag = soup.find('img', class_='avatar')
    if not os.path.exists(icons_directory / 'mods'):
        os.mkdir(icons_directory / 'mods')
    urlretrieve(img_tag.get('src'), icons_directory / 'mods' / f'{name}.png')
    img_small = Image.open(icons_directory / 'mods' / f'{name}.png')
    img_small = img_small.resize((70, 70))
    img_small.save(icons_directory / 'mods' / f'{name}.png')


class App(tk.Tk):
    def __init__(self, title: str, size: tuple):
        # main setup
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(size[0], size[1])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        icon = tk.PhotoImage(file=icons_directory / 'icon.png')
        self.wm_iconphoto(True, icon)
        self.protocol('WM_DELETE_WINDOW', self.on_exit)

        # theme styling
        sv_ttk.set_theme('light')

        self.modlist = []
        self.unsaved_changes = False

        # menu widget
        self.menu = Menu(self)
        self.config(menu=self.menu)

        # widgets
        self.heading = Heading(self)
        self.tools = Tools(self)
        self.container = Container(self)
        self.footer = Footer(self)

        # run
        self.mainloop()

    def on_exit(self):
        if self.unsaved_changes:
            exit_dialog = messagebox.askyesnocancel('Unsaved Changes', 'Do you want to save changes before continuing?')
            if exit_dialog:
                if not save_list(self):
                    return
            elif exit_dialog is None:
                return
        self.destroy()

    def update_heading(self, new_heading: str):
        self.heading.delete(0, 'end')
        self.heading.insert(0, new_heading)

    def add_new_mod(self, url_name):
        for mod in self.modlist:
            if mod.url_name == url_name:
                messagebox.showerror('Mod Already Exists', 'Mod already exists in modlist')
                return

        soup = get_modrinth_page(url_name)
        mod_name = get_mod_name(soup)

        if not os.path.exists(icons_directory / f'{mod_name}.png'):
            get_mod_icon(soup, mod_name)

        self.modlist.append(Mod(self.container.list, mod_name, url_name, len(self.modlist)))
        sort(self, self.tools.cbx_sort.get())

        self.unsaved_changes = True

    def add_cached_mod(self, name, url_name):
        if not os.path.exists(icons_directory / 'mods' / f'{name}.png'):
            soup = get_modrinth_page(url_name)
            get_mod_icon(soup, name)

        self.modlist.append(Mod(self.container.list, name, url_name, len(self.modlist)))

    def call_select_change(self):
        self.tools.select_change(self)


def new_list(master):
    if master.unsaved_changes:
        exit_dialog = messagebox.askyesnocancel('Unsaved Changes', 'Do you want to save changes before continuing?')
        if exit_dialog:
            save_list(master)
        elif exit_dialog is None:
            return
    clear_list(master)
    master.update_heading('Untitled Modlist')


def open_list(master):
    if master.unsaved_changes:
        exit_dialog = messagebox.askyesnocancel('Unsaved Changes', 'Do you want to save changes before continuing?')
        if exit_dialog:
            save_list(master)
        elif exit_dialog is None:
            return

    filepath = filedialog.askopenfilename(initialdir=modlists_directory, title='Open Modlist',
                                          filetypes=(('Text files', '*.txt'), ('All files', '*.*')))
    if not filepath:
        return
    with open(filepath, 'r') as f:
        clear_list(master)
        master.update_heading(filepath.split('/')[-1].split('.')[0])
        for i, line in enumerate(f):
            line = line.strip().split(', ')
            master.add_cached_mod(line[0], line[1])


def clear_list(master):
    for mod in master.modlist:
        mod.destroy()
    master.modlist.clear()


def save_list(master):
    if len(master.modlist) == 0:
        messagebox.showerror('Empty Modlist', 'The modlist is empty, add a mod first to be able to save.')
        return

    if master.heading.get() == 'Untitled Modlist':
        if not messagebox.askokcancel('Untitled Modlist', 'You haven\'t specified a title for the '
                                                          'modlist.\nDo you want to continue?'):
            return False

    list_name = master.heading.get()
    if os.path.exists(modlists_directory / f'{list_name}.txt'):
        if not messagebox.askokcancel('Existing Modlist', 'An existing modlist has the same title!\nDo '
                                                          'you want to override the existing modlist?'):
            return
        os.remove(modlists_directory / f'{list_name}.txt')
    with open(modlists_directory / f'{list_name}.txt', 'a') as f:
        master.modlist.sort(key=lambda args: args.name)
        for mod in master.modlist:
            f.write(mod.name + ', ' + mod.url_name + '\n')

    messagebox.showinfo('Save Complete',
                        f'{list_name} Modlist successfully saved to {modlists_directory / f'{list_name}.txt'}!')
    master.unsaved_changes = False


class Menu(tk.Menu):
    def __init__(self, master):
        super().__init__(master)
        self.create_menus(master)

    def create_menus(self, master):
        # file menu
        mnu_file = tk.Menu(self, tearoff=0)
        mnu_file.add_command(label='New List', command=lambda: new_list(master))
        mnu_file.add_command(label='Open List', command=lambda: open_list(master))
        mnu_file.add_command(label='Save List', command=lambda: save_list(master))
        mnu_file.add_separator()
        mnu_file.add_command(label='Quit', command=lambda: master.on_exit())
        self.add_cascade(label='File', menu=mnu_file)

        # tools menu
        mnu_tools = tk.Menu(self, tearoff=0)
        mnu_tools.add_command(label='Add Mod', command=lambda: open_window(master))
        mnu_tools.add_separator()
        mnu_tools.add_command(label='Select All', command=lambda: menu_set_selection(master, False))
        mnu_tools.add_command(label='Deselect All', command=lambda: menu_set_selection(master, True))
        mnu_tools.add_command(label='Delete Selected', command=lambda: delete(master, True))
        mnu_tools.add_separator()
        mnu_tools.add_command(label='Find...', command=lambda: menu_set_find(master))
        mnu_sort = tk.Menu(self, tearoff=0)
        mnu_sort.add_command(label='A to Z', command=lambda: menu_set_sort(master, 0))
        mnu_sort.add_command(label='Z to A', command=lambda: menu_set_sort(master, 1))
        mnu_tools.add_cascade(label='Sort', menu=mnu_sort)
        self.add_cascade(label='Tools', menu=mnu_tools)

        # actions menu
        mnu_actions = tk.Menu(self, tearoff=0)
        mnu_actions.add_command(label='Download Modlist',
                                command=lambda: download(master, master.footer.cbx_version.get(),
                                                         master.footer.cbx_loader.get()))
        mnu_actions.add_command(label='Check Compatibility',
                                command=lambda: compatible(master, master.footer.cbx_version.get(),
                                                           master.footer.cbx_loader.get()))
        self.add_cascade(label='Actions', menu=mnu_actions)


class Heading(ttk.Entry):
    def __init__(self, master):
        super().__init__(master)
        self['font'] = ('Helvetica', 30)
        self['justify'] = 'center'
        self.insert(0, 'Untitled Modlist')
        self.grid(row=0, sticky='ew', padx=10, pady=10)
        self.bind('<FocusIn>', lambda args: self.get() == 'Untitled Modlist' and self.selection_range(0, tk.END))
        self.bind('<FocusOut>', lambda args: self.selection_clear())
        self.bind('<Return>', lambda args: master.focus_set())


def open_window(master):
    Window(master, 'Enter Modrinth URL', (1000, 50))


def close_window(window, url: str):
    try:
        urlopen(Request(url, headers=requestheader))
        if url[:25] != 'https://modrinth.com/mod/':
            messagebox.showerror(title='URL Error', message=f'URL isn\'t Modrinth')
            return

        url_name = url[25:].split('/', 1)[0]
        window.master.add_new_mod(url_name)
        window.destroy()
    except HTTPError as e:
        messagebox.showerror(title='HTTP Error', message=f'Cannot access page!\n{e}')
    except URLError as e:
        messagebox.showerror(title='URL Error', message=f'Modrinth page not found!\n{e}')
    except ValueError as e:
        messagebox.showerror(title='Unknown URL Type', message=f'Input cannot be parsed as URL!\n{e}')


def menu_set_find(master):
    dialog = simpledialog.askstring(title='Input Text', prompt='Search for specific mods by name.')
    if dialog is None or dialog.strip() == '':
        return
    master.tools.ent_find.delete(0, 'end')
    master.tools.ent_find.insert(0, dialog)
    find(master, dialog)


def menu_set_selection(master, select_mode):
    if len(master.modlist) == 0:
        return
    master.tools.change_select_all_text(select_mode)
    update_selection(master, select_mode)
    num_selected = count_selected(master)
    master.tools.delete_change(master, num_selected)


def menu_set_sort(master, cbx_index: int):
    master.tools.cbx_sort.current(cbx_index)
    sort(master, master.tools.cbx_sort.get())


def width_configure(string) -> int:
    return len(string)


def sort(master, sorting: str):
    if len(master.modlist) == 1:
        return
    reverse = False
    if sorting == 'Z to A':
        reverse = True
    master.modlist.sort(key=lambda args: args.name, reverse=reverse)
    for i, mod in enumerate(master.modlist):
        mod.grid(row=i, sticky='ew', pady=5)


def find_enter(master):
    master.focus_set()


def find(master, string: str):
    for i, mod in enumerate(master.modlist):
        if re.search(string.lower(), mod.name.lower()):
            mod.grid(row=i, sticky='ew', pady=5)
        else:
            mod.grid_forget()


def count_selected(master) -> int:
    num_selected = 0
    for mod in master.modlist:
        if mod.selected.get() == 1:
            num_selected += 1
    return num_selected


def delete(master, select_mode):
    if len(master.modlist) == 0:
        return
    # if selection is greater than 50% then ask for confirmation
    if select_mode:
        if not messagebox.askokcancel('Confirmation', 'Are you sure you want to delete?'):
            return

    for mod in master.modlist:
        if mod.selected.get() == 1:
            master.modlist.remove(mod)
            mod.destroy()

    if len(master.modlist) == 0:
        num_selected = count_selected(master)
        new_select_mode = master.tools.check_selection_mode(master, num_selected)
        master.tools.change_select_all_text(new_select_mode)

    master.unsaved_changes = True


class Tools(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self['relief'] = 'raise'
        self['borderwidth'] = 3
        self.grid(row=1, sticky='ew', padx=10, pady=10)

        self.create_tools(master)

    def create_tools(self, master):
        # add tool
        ttk.Frame(self, width=10).pack(side='left', pady=5)
        btn_add = ttk.Button(self, text='Add Mod', command=lambda: open_window(master), cursor=pointerhand)
        btn_add.pack(side='left', padx=10, pady=5)

        # find tool
        self.ent_find = ttk.Entry(self, width=10, cursor=pointerhand)
        self.ent_find.insert(0, 'Find...')
        self.ent_find.bind('<FocusIn>',
                           lambda args: self.ent_find.get() == 'Find...' and self.ent_find.delete(0, 'end'))
        self.ent_find.bind('<FocusOut>',
                           lambda args: self.ent_find.get() == '' and self.ent_find.insert(0, 'Find...'))
        self.ent_find.bind('<KeyRelease>', lambda args: find(master, self.ent_find.get()))
        self.ent_find.bind('<Return>', lambda args: find_enter(master))
        self.ent_find.pack(side='left', padx=10, pady=5)

        # select all tool
        self.select_mode = False
        self.btn_selectall = ttk.Button(self, text='Select All', cursor=pointerhand)
        self.btn_selectall.bind('<ButtonRelease>', lambda args: self.btn_select_all(master))
        self.btn_selectall.pack(side='left', padx=5, pady=5)

        # delete tool
        self.delete_show = False

        # sort tool
        ttk.Frame(self, width=10).pack(side='right', padx=5, pady=5)
        self.cbx_sort = ttk.Combobox(self, state='readonly', values=('A to Z', 'Z to A'), cursor=pointerhand)
        self.cbx_sort.current(0)
        self.cbx_sort['width'] = width_configure(max(self.cbx_sort.cget('values'), key=len))
        self.cbx_sort.bind('<<ComboboxSelected>>', lambda args: sort(master, self.cbx_sort.get()))
        self.cbx_sort.bind('<FocusOut>', lambda args: self.selection_clear())
        self.cbx_sort.pack(side='right', pady=5)
        lbl_sort = ttk.Label(self, text='Sort:')
        lbl_sort.pack(side='right', padx=10, pady=5)

    def check_selection_mode(self, master, num_selected: int):
        if len(master.modlist) == 0:
            self.select_mode = True
        else:
            if num_selected / len(master.modlist) >= 0.5:
                self.select_mode = True
            else:
                self.select_mode = False
        return self.select_mode

    def change_select_all_text(self, select_mode: bool):
        if select_mode:
            self.btn_selectall['text'] = 'Select All'
        else:
            self.btn_selectall['text'] = 'Deselect All'

    def btn_select_all(self, master):
        if len(master.modlist) == 0:
            return

        num_selected = count_selected(master)
        self.check_selection_mode(master, num_selected)

        update_selection(master, self.select_mode)

        num_selected = count_selected(master)
        self.delete_change(master, num_selected)

        self.change_select_all_text(self.select_mode)

    def select_change(self, master):
        num_selected = count_selected(master)
        self.check_selection_mode(master, num_selected)
        self.delete_change(master, num_selected)

        if self.select_mode:
            self.btn_selectall['text'] = 'Deselect All'
        else:
            self.btn_selectall['text'] = 'Select All'

    def delete_change(self, master, num_selected: int):
        if num_selected == 0:
            if self.delete_show:
                self.btn_delete.destroy()
            self.delete_show = False
        elif num_selected > 0:
            if not self.delete_show:
                self.btn_delete = ttk.Button(self, text='Delete Mod', command=lambda: delete(master, self.select_mode),
                                             cursor=pointerhand)
                self.delete_show = True

            self.btn_delete['text'] = 'Delete Mod' if num_selected == 1 else 'Delete Mods'
            self.btn_delete.pack(side='right', padx=10, pady=5)


def update_selection(master, select_mode):
    for mod in master.modlist:
        if select_mode:
            mod.selected.set(0)
        else:
            mod.selected.set(1)


def get_mod_directory(master, mcversion: str, modloader: str):
    mods_directory = ''
    if sys.platform == 'win32':
        mods_directory = Path(os.environ['APPDATA']) / '.minecraft'
    elif sys.platform == 'darwin':
        mods_directory = Path(os.environ['HOME']) / 'Library' / 'Application Support' / 'minecraft'
    elif sys.platform == 'linux':
        mods_directory = Path(os.environ['HOME']) / '.minecraft'

    if not os.path.exists(mods_directory):
        messagebox.showerror(title='Where\'s Minecraft?', message='Minecraft directory not found, install minecraft!')
        return

    mods_directory = mods_directory / 'mods'
    if not os.path.exists(mods_directory):
        messagebox.showinfo('Missing Mods Directory', 'Creating the mods directory ...')
        os.mkdir(mods_directory)

    mods_directory = mods_directory / f'{master.heading.get()} [{modloader}] {mcversion}'
    if not os.path.exists(mods_directory):
        os.mkdir(mods_directory)

    return mods_directory


def scrape_desired_version(soup):
    desired_version = soup.find_all('a', class_='download-button')
    return desired_version[0] if len(desired_version) > 0 else None


def scrape_available_version(soup, mod, mcversion: str, modloader: str):
    first_version_marker = None
    same_modloader_marker = None

    available_versions = soup.find_all('div', class_='featured-version')
    if len(available_versions) == 0:
        messagebox.showerror(title='Mod Download Unavailable',
                             message='No available versions found of \'{mod.name}\' on modrinth.')
        return

    for version in available_versions:
        # [0] is modloader and [1] is mcversion
        version_info = version.findNext('div', class_='game-version').text
        mcversion_info = str(re.match(r'(\d+)\.(\d+)\.(\d+)$', version_info))
        print(mcversion_info)
        # Available mod version must be equal or older in mc version, inverted due to newest mc version
        # starting at index 0. If not, remove from list
        if mcversions.index(mcversion_info) > mcversions.index(mcversion) and version.find('span',
                                                                                           class_='type--release'):
            if first_version_marker is None:
                first_version_marker = {'mcversion': mcversion_info, 'webscrap': version}

            if same_modloader_marker is None:
                if re.match(modloader, version_info, re.IGNORECASE):
                    same_modloader_marker = {'mcversion': mcversion_info, 'webscrap': version}

    # If the same modloader version has a less than three mcversion difference from the first version, then
    # the same modloader version is the best version, else first version is the best version.
    if same_modloader_marker is not None and abs(mcversions.index(same_modloader_marker['mcversion'])
                                                 - mcversions.index(first_version_marker['mcversion'])) < 3:
        best_available_version = same_modloader_marker['webscrap']
    else:
        best_available_version = first_version_marker['webscrap']

    # Get remaining information of the best available version
    version_info = best_available_version.findNext('div', class_='game-version')
    version_name = best_available_version.findNext('a', class_='top')
    version_url = version_name['href']
    messagebox.showwarning(title='Mod Download Unavailable',
                           message=f'No desired version found of \'{mod.name}\' on modrinth!'
                                   f'\n\nFound an available version:\n{version_info}'
                                   f'\n\nhttps://modrinth.com/mods{version_url}')


def download_file(desired_version, mod, mods_directory):
    list_mods = os.listdir(mods_directory)
    file_url = desired_version['href']
    file_version = (desired_version.findNextSibling('div', class_='version__metadata')
                    .findNext('span', class_='version_number').text)
    file_name = mod.name + ' ' + file_version + '.jar'

    same_mods = list(filter(lambda x: re.match(f'{mod.name}+', x), list_mods))
    first_duplicate = True
    for mod in same_mods:
        if mod == file_name:
            if first_duplicate:
                first_duplicate = False
                continue
            else:
                os.remove(mods_directory / mod)
        else:
            os.remove(mods_directory / mod)

    urlretrieve(file_url, mods_directory / file_name)


def compatible(master, mcversion: str, modloader: str):
    if len(master.modlist) == 0:
        return

    incompatible_mods = []

    for mod in master.modlist:
        try:
            soup = get_modrinth_page(
                mod.url_name + '/versions?l=' + modloader.lower() + '&g=' + mcversion)
            desired_version = scrape_desired_version(soup)
            if desired_version is None:
                incompatible_mods.append(mod)
        except URLError as e:
            messagebox.showerror(title='URL Error', message=f'Modrinth page not found for mod {mod.name}!\n{e}')

    if len(incompatible_mods) > 0:
        messagebox.showinfo(title='Some Mods Incompatible',
                            message=f'No compatible mod versions found for: '
                                    f'{", ".join(mod.name for mod in incompatible_mods)}')
    else:
        messagebox.showinfo(title='All Mods Compatible',
                            message='All mods are compatible for specified minecraft version and mod loader!')


def download(master, mcversion: str, modloader: str):
    if len(master.modlist) == 0:
        return

    mods_directory = get_mod_directory(master, mcversion, modloader)
    for mod in master.modlist:
        time.sleep(0.5)  # Temporary solution to HTTP Error: Too Many Requests
        try:
            soup = get_modrinth_page(mod.url_name + '/versions?l=' + modloader.lower() + '&g=' + mcversion)
            desired_version = scrape_desired_version(soup)
            if desired_version is None:
                scrape_available_version(soup, mod, mcversion, modloader)
            else:
                download_file(desired_version, mod, mods_directory)
        except HTTPError as e:
            header = e.headers  # Todo: Extract HTTP header check if Too Many Requests and then get time to wait
        except URLError as e:
            messagebox.showerror(title='URL Error', message=f'Modrinth page not found for mod {mod.name}!\n{e}')

    messagebox.showinfo('Download Complete',
                        f'Mods downloaded successfully into your minecraft mods directory! Files can be found '
                        f'in:\n\n{mods_directory}')


class Footer(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self['relief'] = 'raise'
        self['borderwidth'] = 3
        self.grid(row=3, sticky='ew', padx=10, pady=10)

        self.create_widgets(master)

    def create_widgets(self, master):
        # minecraft version filter
        ttk.Frame(self, width=10).pack(side='left', pady=5)
        lbl_version = ttk.Label(self, text='Minecraft Version:')
        lbl_version.pack(side='left', padx=10, pady=5)
        self.cbx_version = ttk.Combobox(self, state='readonly', values=mcversions, cursor=pointerhand)
        self.cbx_version.current(0)
        self.cbx_version['width'] = width_configure(max(self.cbx_version.cget('values'), key=len))
        self.cbx_version.bind('<FocusOut>', lambda args: self.selection_clear())
        self.cbx_version.pack(side='left', pady=5)

        # mod loader filter
        ttk.Frame(self, width=10).pack(side='left', padx=5, pady=5)
        lbl_loader = ttk.Label(self, text='Mod Loader:')
        lbl_loader.pack(side='left', padx=10, pady=5)
        self.cbx_loader = ttk.Combobox(self, state='readonly', values=modloaders, cursor=pointerhand)
        self.cbx_loader.current(0)
        self.cbx_loader['width'] = width_configure(max(self.cbx_loader.cget('values'), key=len))
        self.cbx_loader.bind('<FocusOut>', lambda args: self.selection_clear())
        self.cbx_loader.pack(side='left', pady=5)

        # download button
        ttk.Frame(self, width=10).pack(side='right', padx=2, pady=5)
        btn_download = ttk.Button(self, text='DOWNLOAD', cursor=pointerhand,
                                  command=lambda: download(master, self.cbx_version.get(), self.cbx_loader.get()))
        btn_download.pack(side='right', padx=5, pady=5)
        btn_check = ttk.Button(self, text='CHECK', cursor=pointerhand,
                               command=lambda: compatible(master, self.cbx_version.get(), self.cbx_loader.get()))
        btn_check.pack(side='right', padx=10, pady=5)


class Container(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid(row=2, column=0, sticky='nsew', padx=10)

        self.create_widgets()

    def create_widgets(self):
        # canvas
        self.canvas = tk.Canvas(self)
        self.canvas.columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        # scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky='ns')

        # list
        self.list = ttk.Frame(self.canvas)
        self.list.columnconfigure(0, weight=1)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.list, anchor='nw')
        self.list.bind('<Configure>', lambda args: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda args: self.canvas.itemconfig(self.canvas_frame, width=args.width - 10))
        self.list.bind('<Enter>', self.bind_mousewheel)
        self.list.bind('<Leave>', self.unbind_mousewheel)

    def bind_mousewheel(self, event):
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)

    def unbind_mousewheel(self, event):
        self.canvas.unbind_all('<MouseWheel>')

    def on_mousewheel(self, event):
        if sys.platform == 'win32':
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        else:
            self.canvas.yview_scroll(int(-1 * event.delta), 'units')


class Mod(ttk.Frame):
    def __init__(self, master, name: str, url_name: str, row):
        super().__init__(master)
        self['relief'] = 'ridge'
        self['borderwidth'] = 5
        self.grid(row=row, sticky='ew', pady=5)
        self.columnconfigure(1, weight=1)

        self.name = name
        self.url_name = url_name
        self.selected = tk.IntVar()

        self.create_widgets(master)

    def create_widgets(self, master):
        # mod icon
        self.img = Image.open(icons_directory / 'mods' / f'{self.name}.png')
        self.img = self.img.resize((70, 70))
        self.img = ImageTk.PhotoImage(self.img)
        lbl_icon = ttk.Label(self, image=self.img, cursor=pointerhand)
        lbl_icon.bind('<Button-1>', lambda args: open_webview(f'mod/{self.url_name}'))
        lbl_icon.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # mod name
        lbl_name = tk.Label(self, text=self.name, font=('Helvetica', 30))
        lbl_name.grid(row=0, column=1, sticky='w', padx=30)

        # select button
        chk_select = ttk.Checkbutton(self, variable=self.selected, cursor=pointerhand,
                                     command=master.master.master.master.call_select_change)
        chk_select.grid(row=0, column=2, sticky='e', padx=20)


def open_webview(url_extension):
    webbrowser.open(f'https://modrinth.com/{url_extension}')


class Window(tk.Toplevel):
    def __init__(self, master, title: str, size: tuple):
        # main setup
        super().__init__(master)
        self.url_name = None
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(size[0], size[1])
        self.maxsize(size[0], size[1])
        self.bell()

        self.create_widgets()

        self.grab_set()
        self.transient(master)
        master.wait_window(self)

    def create_widgets(self):
        # mod webview button
        btn_webview = ttk.Button(self, text='Open Modrinth', command=lambda: open_webview('mods'))
        btn_webview.pack(side='left', padx=20, pady=5)
        # mod url entry
        ent_url = ttk.Entry(self, width=100, font=('Helvetica', 20))
        ent_url.insert(0, 'Enter Modrinth URL for Mod...')
        ent_url.bind('<FocusIn>',
                     lambda args: ent_url.get() == 'Enter Modrinth URL for Mod...' and ent_url.delete(0, 'end'))
        ent_url.bind('<FocusOut>',
                     lambda args: ent_url.get() == '' and ent_url.insert(0, 'Enter Modrinth URL for Mod...'))
        ent_url.bind('<Return>', lambda args: close_window(self, ent_url.get()))
        ent_url.bind('<BackSpace>', lambda args: ent_url.delete(0, 'end'))
        ent_url.pack(side='left', pady=5)


app = App('Modlist Manager', (800, 500))
