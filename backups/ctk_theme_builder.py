import argparse
import tkinter as tk
import customtkinter as ctk
from customtkinter import ThemeManager
from configparser import ConfigParser
import json
import subprocess as sp
from argparse import HelpFormatter
from operator import attrgetter
from PIL import Image, ImageTk
import os
from os.path import exists
import operator
from pathlib import Path
import pyperclip
import shutil
import sys
import textwrap
from tkinter import filedialog
from tkinter.colorchooser import askcolor
from pathlib import Path

HEADING_FONT = 'Roboto 12'
# from multiprocessing.connection import Listener
# from multiprocessing.connection import Client

prog = os.path.basename(__file__)
prog_dir = Path(os.path.dirname(os.path.realpath(__file__)))
assets_dir = prog_dir / 'assets/etc'
home_dir = os.getenv("HOME")
PATH = os.path.dirname(os.path.realpath(__file__))
IMAGES = f'{PATH}/images'

WIDGET_ATTRIBUTES = {'CTk/Toplevel': ['window_bg_color'],
                     'Frame': ['frame_border', 'frame_low', 'frame_high'],
                     'Button': ['button', 'button_hover', 'button_border'],
                     'CheckBox': ['checkbox_border', 'checkmark'],
                     'ComboBox': ['combobox_button_hover', 'dropdown_color', 'dropdown_hover', 'dropdown_text'],
                     'Entry': ['entry', 'entry_border', 'entry_placeholder_text'],
                     'Label': ['label'], 'Text': ['text', 'text_disabled', 'text_button_disabled'],
                     'ProgressBar': ['progressbar', 'progressbar_progress', 'progressbar_border'],
                     'Slider': ['slider', 'slider_progress', 'slider_button', 'slider_button_hover'],
                     'Switch': ['switch', 'switch_progress', 'switch_button', 'switch_button_hover'],
                     'OptionMenu': ['optionmenu_button', 'optionmenu_button_hover', 'combobox_border'],
                     'Scrollbar': ['scrollbar_button', 'scrollbar_button_hover'],
                     'Text': ['text', 'text_disabled', 'text_button_disabled']}


def str_mode_to_int():
    appearance_mode = ctk.get_appearance_mode()
    if appearance_mode == "Light":
        return 0
    return 1


def get_color_from_name(name: str):
    int_mode = str_mode_to_int()
    return ThemeManager.theme["color"][name][int_mode]


class CBtkMessageBox(object):
    """Message box class for customtkinter. Up to 4 buttons are rendered where their respective buttonN_text
    parameter has a value. An integer value us returned, dependant upon the respective button number, of the button
    pressed. """

    def __init__(self, title='CBtkMessageBox',
                 message='',
                 button1_text='OK',
                 button2_text='',
                 button3_text='',
                 button4_text=''):

        # Required Data of Init Function

        self.message = wrap_string(text_string=message, wrap_width=40)  # Is message to display
        self.button1_text = button1_text  # Button 1 (outputs '1')
        self.button2_text = button2_text  # Button 2 (outputs '2')
        self.button3_text = button3_text  # Button 3 (outputs '3')
        self.button4_text = button4_text  # Button 4 (outputs '4')
        self.choice = ''  # it will be the return of messagebox according to button press

        # Create TopLevel dialog for the messagebox
        self.root = ctk.CTkToplevel()
        self.root.title(title)

        # Setting Geometry
        self.root.geometry("320x120")

        # Creating Label For message
        self.message = ctk.CTkLabel(self.root, text=self.message)
        self.message.place(x=15, y=15, height=60, width=250)

        # Create a button, corresponding to button1_text
        self.button1_text = ctk.CTkButton(self.root, text=self.button1_text, command=self.click1)
        self.button1_text.place(x=150, y=90, height=25, width=60)

        # Create a button, corresponding to  button1_text
        self.button1_text.info = self.button1_text.place_info()

        # Create a button, corresponding to  button2_text
        if not button2_text == "":
            self.button2_text = ctk.CTkButton(self.root, text=self.button2_text, command=self.click2)
            self.button2_text.place(x=int(self.button1_text.info['x']) - (70 * 1),
                                    y=int(self.button1_text.info['y']),
                                    height=int(self.button1_text.info['height']),
                                    width=int(self.button1_text.info['width'])
                                    )
        # Create a button, corresponding to  button3_text
        if not button3_text == '':
            self.button3_text = ctk.CTkButton(self.root, text=self.button3_text, command=self.click3)
            self.button3_text.place(x=int(self.button1_text.info['x']) - (70 * 2),
                                    y=int(self.button1_text.info['y']),
                                    height=int(self.button1_text.info['height']),
                                    width=int(self.button1_text.info['width'])
                                    )
        # Create a button, corresponding to button4_text
        if not button4_text == '':
            self.button4_text = ctk.CTkButton(self.root, text=self.button4_text, command=self.click4)
            self.button4_text.place(x=int(self.button1_text.info['x']) - (70 * 3),
                                    y=int(self.button1_text.info['y']),
                                    height=int(self.button1_text.info['height']),
                                    width=int(self.button1_text.info['width'])
                                    )

        # Make the message box visible
        self.root.wait_window()

    # Function on Closing MessageBox
    def closed(self):
        self.root.destroy()  # Destroying Dialogue
        self.choice = 'closed'  # Assigning Value

    # Function on pressing button1_text
    def click1(self):
        self.root.destroy()  # Destroying Dialogue
        self.choice = 1  # Assigning Value

    # Function on pressing button2_text
    def click2(self):
        self.root.destroy()  # Destroying Dialogue
        self.choice = 2  # Assigning Value

    # Function on pressing button3_text
    def click3(self):
        self.root.destroy()  # Destroying Dialogue
        self.choice = 3  # Assigning Value

    # Function on pressing button4_text
    def click4(self):
        self.root.destroy()  # Destroying Dialogue
        self.choice = 4  # Assigning Value


def all_widget_attributes(widget_attributes):
    all_attributes = []
    for value_list in widget_attributes.values():
        all_attributes = all_attributes + value_list
    return all_attributes


def all_widget_categories(widget_attributes):
    categories = []
    for category in widget_attributes:
        categories.append(category)
    categories.sort()
    return categories


def wrap_string(text_string: str, wrap_width=80):
    """Function which takes a string of text and wraps it, at word boundaries, based on a specified width.
    :rtype@ str
    :param@ text_string:
    :param@ wrap_width:
    """
    wrapper = textwrap.TextWrapper(width=wrap_width)
    word_list = wrapper.wrap(text=text_string)
    string = ''
    for element in word_list:
        string = string + element + '\n'
    return string


# Add a category of All to the WIDGET_ATTRIBUTES already defined. This lists every widget property under the one key.
WIDGET_ATTRIBUTES['All'] = all_widget_attributes(WIDGET_ATTRIBUTES)
bespoke_themes = ['oceanix', 'oceanic']


def launch_widget_preview(appearance_mode, theme):
    preview = Preview(appearance_mode=appearance_mode, theme=theme)


class SortingHelpFormatter(HelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


class CBtkStatusBar(tk.Entry):
    """Create a status bar on the parent window. The status bar auto-fits the window width. Messages can be written
    to the status bar using the set_status_text method. The status_text_life can be used to auto-erase the status
    text after the specified number of seconds. The default value, 0, disables this feature. """

    def __init__(self,
                 master,
                 status_text_life=10):
        super().__init__()

        self._message_id = None
        self._master = master
        grid_size = master.grid_size()
        grid_columns = grid_size[0]
        grid_rows = grid_size[1]
        self._master.update_idletasks()
        self._app_width = self._master.winfo_width()
        self._int_mode = self._str_mode_to_int()
        self._status_text_life = status_text_life
        assert isinstance(self._status_text_life, int)

        self._bg_color = self._get_color_from_name('text')

        self._default_fg_color = get_color_from_name('frame_low')
        print(f'Status bar colour: {self._default_fg_color}')

        self._status_bar = ctk.CTkLabel(master, relief=tk.SUNKEN, text='', anchor='w', width=self._app_width,
                                        fg_color=self._default_fg_color)
        # breadcrumb
        self._status_bar.pack(fill="both", expand=0)

        self._orig_app_width = self._master.winfo_width()

    def auto_size_status_bar(self, event):
        # self._master.update_idletasks()
        self._app_width = self._master.winfo_width()
        if self._app_width > self._orig_app_width:
            self._status_bar.configure(width=self._app_width)
            self._master.update_idletasks()

    def clear_status(self):
        self.set_status_text(status_text=' ')

    def set_status_text(self, status_text: str,
                        status_text_life=None):
        message_life = 0
        self._status_bar.configure(text='  ' + status_text)
        if status_text_life is not None:
            message_life = status_text_life
        elif self._status_text_life:
            message_life = self._status_text_life
        else:
            message_life = 0
        if self._status_text_life:
            self._message_id = self.after(message_life * 1000, self.clear_status)

    def set_text_color(self, text_color):
        self._status_bar.configure(text_color=text_color)

    def cancel_message_timer(self):
        """If using the status message timeout feature, it is important to use the cancel_message_timer function,
        immediately prior to closing the window. This prevents the later reference and exception, associated with an
        "after" method resource reference to an object which is destroyed. """
        if hasattr(self, '_message_id'):
            self.after_cancel(id=self._message_id)

    def set_fg_color(self, fg_color):
        self._status_bar.configure(fg_color=fg_color)

    def _str_mode_to_int(self):
        self._appearance_mode = ctk.get_appearance_mode()
        if self._appearance_mode == "Light":
            return 0
        return 1

    def _get_color_from_name(self, name: str):
        return ThemeManager.theme["color"][name][self._int_mode]

    @staticmethod
    def _get_property_by_name(prop_name: str):
        return ThemeManager.theme[prop_name]

    def set_status_text_life(self, status_text_life):
        self._status_text_life = status_text_life


class Controller():
    initial_height = 800
    expanded_height = 800
    initial_width = 180
    expanded_width_small = 540
    expanded_width_large = 540

    def __init__(self):
        self.app = ctk.CTk()

        platform = sys.platform
        if platform == "win32":
            self._platform = "Windows"
        elif platform == "darwin":
            self._platform = "MacOS"
        else:
            self._platform = "Linux"

        if platform == "Windows":
            self._home_dir = os.getenv("UserProfile")
        else:
            self._home_dir = os.getenv("HOME")

        # Initialise class properties
        self._home_dir = Path(self._home_dir)
        self._app_home = self._home_dir / '.ctk_theme_maker'
        self._appearance_mode = 'Light'
        self.process = None
        self.app.protocol("WM_DELETE_WINDOW", self.close_controller)
        self._json_state = 'clean'
        self.widgets = {}

        # If this is the first time the app is run, create an app home directory.
        if not exists(self._app_home):
            print(f'Initialising application: {self._app_home}')
            os.mkdir(self._app_home)

        self._config_file = self._app_home / 'ctk_theme_maker.ini'
        # If we don't have an ini file, create one.
        if not exists(self._config_file):
            self._create_config_file(platform=platform)

        self._json_dir = Path(self._config_property_val('auto_save', 'json_dir'))
        self._temp_dir = Path(self._config_property_val('system', 'temp_dir'))
        winfo_x = self._config_property_val('geometry', 'control_winfo_x')
        winfo_y = self._config_property_val('geometry', 'control_winfo_y')
        self._restore_geometry()

        ctk.set_appearance_mode('Light')
        # self.app.geometry(f'{180}x{Controller.initial_height}+{winfo_x}+{winfo_y}')
        self.app.rowconfigure(2, weight=1)
        self.app.columnconfigure(0, weight=1)

        self.app.title('CTk Theme Builder')

        # Instantiate Frames
        title_frame = ctk.CTkFrame(master=self.app)
        # title_frame.grid(row=0, column=0, columnspan=2, sticky='w', padx=(5, 5), pady=(5, 0))
        title_frame.pack(fill="both", expand=0)

        self._control_frame = ctk.CTkFrame(master=self.app)
        self._control_frame.columnconfigure(1, weight=1)
        self._control_frame.pack(fill="both", expand=1)
        button_frame = ctk.CTkFrame(master=self._control_frame)
        button_frame.grid(row=1, column=0, columnspan=1, sticky='ns', padx=(5, 5), pady=(5, 5))
        self._button_frame = button_frame

        self._widget_frame = ctk.CTkFrame(master=self._control_frame)
        self._widget_frame.grid(row=1, column=1, rowspan=1, sticky='nswe', padx=(0, 5), pady=(5, 5))
        self._status_bar = CBtkStatusBar(master=self.app,
                                         status_text_life=10)
        self.app.bind("<Configure>", self._status_bar.auto_size_status_bar)

        # Populate Frames
        self.lbl_title = ctk.CTkLabel(master=title_frame, text='Control Panel', text_font=HEADING_FONT)
        self.lbl_title.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 5))
        master = title_frame.columnconfigure(0, weight=1)

        self.lbl_theme = ctk.CTkLabel(master=self._button_frame, text='Select Theme:')
        self.lbl_theme.grid(row=1, column=0, sticky='w', pady=(10, 0), padx=(10, 10))

        self._json_files = self._themes_list()
        initial_display = self._themes_list()
        initial_display.insert(0, '-- Select Theme --')
        self.opm_theme = ctk.CTkOptionMenu(master=self._button_frame,
                                           values=initial_display,
                                           command=self._load_theme)
        self.opm_theme.grid(row=3, column=0)

        self.lbl_mode = ctk.CTkLabel(master=self._button_frame, text='Select Mode:')
        self.lbl_mode.grid(row=5, column=0, sticky='w', pady=(10, 0), padx=(10, 10))

        self.opm_mode = ctk.CTkOptionMenu(master=self._button_frame, values=['Dark', 'Light'],
                                          command=self.render_widget_properties_preview,
                                          state=tk.DISABLED)
        self.opm_mode.grid(row=6, column=0)

        self.lbl_filter = ctk.CTkLabel(master=self._button_frame, text='Filter Properties:')
        self.lbl_filter.grid(row=7, column=0, sticky='w', pady=(10, 0), padx=(10, 10))

        widget_categories = all_widget_categories(WIDGET_ATTRIBUTES)
        self.opm_filter = ctk.CTkOptionMenu(master=self._button_frame, values=widget_categories,
                                            command=self.set_filtered_widget_display,
                                            state=tk.DISABLED)
        self.opm_filter.grid(row=8, column=0)

        # btn_launch = ctk.CTkButton(master=frame, text='Close Colours', command=self.remove_colours)
        # btn_launch.grid(row=0, column=1, padx=5, pady=5)

        self._btn_refresh = ctk.CTkButton(master=button_frame, text='Update Preview',
                                          command=self._refresh_preview,
                                          state=tk.DISABLED)
        self._btn_refresh.grid(row=10, column=0, padx=5, pady=(60, 0))
        # We don't render the refresh just yet. This is to replace the preview button once initial preview is elected.

        self._btn_reset = ctk.CTkButton(master=button_frame,
                                        text='Reset',
                                        state=tk.DISABLED,
                                        command=self.reset_theme)
        self._btn_reset.grid(row=12, column=0, padx=5, pady=(60, 5))

        self._btn_create = ctk.CTkButton(master=button_frame,
                                         text='Create',
                                         state=tk.NORMAL,
                                         command=self._create_theme)
        self._btn_create.grid(row=14, column=0, padx=5, pady=(5, 5))

        self._btn_save = ctk.CTkButton(master=button_frame,
                                       text='Save',
                                       state=tk.DISABLED,
                                       command=self._save_json)
        self._btn_save.grid(row=18, column=0, padx=5, pady=(30, 5))

        self._btn_save_as = ctk.CTkButton(master=button_frame,
                                          text='Save As',
                                          state=tk.DISABLED,
                                          command=self._save_theme_as)
        self._btn_save_as.grid(row=20, column=0, padx=5, pady=(5, 5))

        btn_quit = ctk.CTkButton(master=button_frame, text='Quit', command=self.close_controller)
        btn_quit.grid(row=30, column=0, padx=5, pady=(180, 5))

        self._create_menu()

        self.app.mainloop()

    def _appearance_mode_index(self, mode=None):
        if mode is None:
            appearance_mode = ctk.get_appearance_mode()
        else:
            appearance_mode = mode
        if appearance_mode == "Light":
            return 0
        # self.app.geometry = ''
        return 1

    def colour_picker(self, widget_property):
        prev_colour = self.widgets[widget_property]["colour"]
        new_colour = askcolor(master=self.app, title='Pick colour for : ' + widget_property,
                              initialcolor=prev_colour)
        if new_colour[1] is not None:
            new_colour = new_colour[1]
            self.widgets[widget_property]['button'].configure(fg_color=new_colour)
            self.widgets[widget_property]['colour'] = new_colour
            appearance_mode_index = self._appearance_mode_index(self._appearance_mode)
            self.json_data['color'][widget_property][appearance_mode_index] = new_colour
            if prev_colour != new_colour:
                print(prev_colour)
                print(new_colour)
                self._btn_reset.configure(state=tk.NORMAL)
                self._btn_save.configure(state=tk.NORMAL)
                self._json_state = 'dirty'

    def _config_property_val(self, section: str, key: str):
        """Accept a config file section and key then return the associated value last stored in theme_make.ini"""
        config = ConfigParser()
        config.read(self._config_file)
        config_value = config.get(section, key)
        return config_value

    def _create_config_file(self, platform):
        with open(self._config_file, 'w') as f:
            f.write('[system]\n')
            if platform in ['darwin', 'linux']:
                f.write('temp_dir = /tmp\n')
            else:
                f.write(f'temp_dir = {self._home_dir}\AppData\Local\Temp\n')
            f.write('[auto_save]\n')
            f.write('json_dir = .\n')
            f.write('expand_palette = 1\n')
            f.write('render_disabled = 1\n')

    def _create_menu(self):
        # Set up the core of our menu
        des_menu = tk.Menu(self.app)
        foreground = self._get_color_from_name('text')
        background = self._get_color_from_name('frame_low')
        des_menu.config(background=background, foreground=foreground)
        self.app.config(menu=des_menu)

        # Now add a File sub-menu option
        file_menu = tk.Menu(des_menu)
        file_menu.config(background=background, foreground=foreground)
        des_menu.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='Quit', command=self.close_controller)

        # Now add a Tools sub-menu option
        tools_menu = tk.Menu(des_menu)
        tools_menu.config(background=background, foreground=foreground)
        des_menu.add_cascade(label='Tools', menu=tools_menu)
        tools_menu.add_command(label='Preferences', command=self._launch_preferences)

    def _launch_preferences(self):
        top_prefs = ctk.CTkToplevel(master=self.app)
        top_prefs.title('Theme Builder Preferences')
        # Make preferences dialog modal
        top_prefs.grab_set()

        frm_main = ctk.CTkFrame(master=top_prefs)
        frm_main.pack(padx=5, pady=5)

        btn_json_dir = ctk.CTkButton(master=frm_main,
                                     text='Set JSON location',
                                     command=self._preferred_json_location)

        lbl_theme_panel = ctk.CTkLabel(text='Control Panel:', fg_color=("white", "gray75"))
        lbl_theme = ctk.CTkLabel(text='Theme')
        lbl_mode = ctk.CTkLabel(text='Mode')

        opm_controller_theme = ctk.CTkOptionMenu(master=frm_main,
                                                 values=self._themes_list(),
                                                 command=self._preferred_controller_theme)

        self._appearance_mode_var = tk.StringVar(value='Light')
        rdo_light = ctk.CTkRadioButton(master=frm_main, text='Light', variable=self._appearance_mode_var,
                                       value='Light')

        rdo_dark = ctk.CTkRadioButton(master=frm_main, text='Dark', variable=self._appearance_mode_var,
                                      value='Dark')

        btn_json_dir = ctk.CTkButton(master=frm_main, text='Set JSON location', command=self._preferred_json_location)

        btn_close = ctk.CTkButton(master=frm_main, text='Close', command=top_prefs.destroy)
        btn_save = ctk.CTkButton(master=frm_main, text='Save', command=self._save_preferences)

        btn_json_dir.pack(padx=5, pady=5)
        lbl_theme_panel.pack(padx=5, pady=5)
        lbl_theme.pack(padx=5, pady=5)
        opm_controller_theme.pack(padx=5, pady=5, side=tk.RIGHT)
        lbl_mode.pack(padx=5, pady=5)
        rdo_light.pack(padx=5, pady=5, side=tk.RIGHT)
        rdo_dark.pack(padx=5, pady=5, side=tk.RIGHT)

        btn_close.pack(padx=5, pady=5)

        btn_save.pack(padx=5, pady=5)

    def _save_preferences(self):
        # Save JSON Directory:
        self._json_dir = self._new_json_dir
        self._update_config(section='auto_save', option='json_dir', value=self._json_dir)
        self._json_files = self._themes_list()
        self.opm_theme.configure(values=self._json_files)

    def _preferred_controller_theme(self):
        pass

    def _preferred_json_location(self):
        self._new_json_dir = Path(tk.filedialog.askdirectory(initialdir=self._json_dir))

    def _themes_list(self):
        """This method generates a list of theme names, based on the json files found in the themes folder
        (i.e. self._json_dir). These are basically the theme file names, with the .json extension stripped out."""
        json_files = [file for file in os.listdir(self._json_dir) if file.endswith('.json')]
        theme_names = []
        for file in json_files:
            theme_name = os.path.splitext(file)[0]
            theme_names.append(theme_name)
        return theme_names

    @staticmethod
    def _get_color_from_name(name: str):
        mode = ctk.get_appearance_mode()
        if mode == 'Light':
            mode = 0
        else:
            mode = 1
        return ThemeManager.theme["color"][name][mode]

    def _load_theme(self, dummy=None):

        if self._json_state == 'dirty':
            confirm = CBtkMessageBox(title='Confirm Action',
                                     message=f'You have unsaved changes. Are you sure you wish to switch themes?',
                                     button1_text='Yes',
                                     button2_text='No')
            if confirm.choice == 2:
                return

        self._json_state = 'clean'

        if self.opm_theme.get() == '-- Select Theme --':
            return

        self._theme_file = self.opm_theme.get() + '.json'
        self._source_json_file = self._json_dir / self._theme_file
        if self._source_json_file:
            self._wip_json = self._temp_dir / self._theme_file
            shutil.copyfile(self._source_json_file, self._wip_json)
            with open(self._wip_json) as f:
                self.json_data = json.load(f)
            self._update_config(section='auto_save', option='json_dir', value=self._json_dir)
            self.render_widget_properties()
            try:
                self._btn_refresh.configure(state=tk.NORMAL)
            except tk.TclError:
                pass
            # Enable buttons
            self.opm_mode.configure(state=tk.NORMAL)
            self.opm_filter.configure(state=tk.NORMAL)
            self._btn_save_as.configure(state=tk.NORMAL)
            self._btn_reset.configure(state=tk.DISABLED)
            self._btn_save.configure(state=tk.DISABLED)

            self.lbl_title.grid(row=0, column=0, columnspan=2, sticky='ew')
            self.app.geometry(f'{540}x{Controller.expanded_height}')
            self.opm_theme.configure(values=self._json_files)
            self._refresh_preview()
            self._status_bar.set_status_text(status_text=f'Theme file, {self._theme_file}, loaded. ')

    def reset_theme(self):
        confirm = CBtkMessageBox(title='Confirm Action',
                                 message=f'You have unsaved changes. Are you sure you wish to discard them?',
                                 button1_text='Yes',
                                 button2_text='No')
        if confirm.choice == 2:
            return
        self._json_state = 'clean'
        self._load_theme()

    def _create_theme(self):
        source_file = assets_dir / 'default.json'
        dialog = ctk.CTkInputDialog(master=None, text="Enter new theme name:", title="Create New Theme")
        new_theme = dialog.get_input()
        if new_theme:
            # If user has included a ".json" extension, remove it, because we add one below.
            new_theme = os.path.splitext(new_theme)[0]
            new_theme = new_theme + '.json'
            new_theme_path = self._json_dir / new_theme
            shutil.copyfile(source_file, new_theme_path)
            self._json_files = [f for f in os.listdir(self._json_dir) if f.endswith('.json')]
            self.opm_theme.configure(values=self._json_files)
            self.opm_theme.set(new_theme)

    def _save_theme_as(self):
        source_file = self._source_json_file
        dialog = ctk.CTkInputDialog(master=None, text="Enter new theme name:", title="Create New Theme")
        new_theme = dialog.get_input()
        if new_theme:
            # If user has included a ".json" extension, remove it, because we add one below.
            new_theme = os.path.splitext(new_theme)[0]
            new_theme = new_theme + '.json'
            new_theme_path = self._json_dir / new_theme
            shutil.copyfile(source_file, new_theme_path)
            self._json_files = [f for f in os.listdir(self._json_dir) if f.endswith('.json')]
            self.opm_theme.configure(values=self._json_files)
            self.opm_theme.set(new_theme)

    def _update_config(self, section, option, value):
        """Update our config file with the specified value."""
        config = ConfigParser()
        config.read(self._config_file)
        config.set(section=section, option=option, value=str(value))
        with open(self._config_file, 'w') as f:
            config.write(f)

    def set_filtered_widget_display(self, dummy):
        filter = self.opm_filter.get()
        if filter == 'All':
            self.app.geometry(f'{Controller.expanded_width_large}x{Controller.expanded_height}')
        else:
            self.app.geometry(f'{Controller.expanded_width_small}x{Controller.expanded_height}')
        self.render_widget_properties()

    def refresh_widget_properties(self, dummy=None):
        """Here we render the widget properties in the control panel"""
        self.render_widget_properties()
        self._refresh_preview()

    def render_widget_properties_preview(self, dummy=None):
        """Here we render the widget properties in the control panel as well as update the preview panel."""
        self.render_widget_properties()
        self._refresh_preview()

    def render_widget_properties(self, dummy=None):
        """Here we render the widget properties in the control panel"""
        filter_key = self.opm_filter.get()
        self._filter_list = WIDGET_ATTRIBUTES[filter_key]
        self._appearance_mode = self.opm_mode.get()
        js = open(self._wip_json)
        json_text = json.load(js)

        widget_frame = self._widget_frame
        colours = json_text["color"]

        sorted_widget_properties = sorted(colours.items(), key=operator.itemgetter(0))
        row = 1
        # The offset is used to control the column we place the widget details in.
        # We aim to stack them into 2 columns.
        offset = 0
        button_width = 30
        button_height = 30

        for entry in self.widgets.values():
            btn_property = entry['button']
            lbl_property = entry['label']
            btn_property.grid_remove()
            lbl_property.grid_remove()

        appearance_mode_index = self._appearance_mode_index(appearance_mode)
        for key, value in sorted_widget_properties:
            if key not in self._filter_list:
                continue
            colour = value[appearance_mode_index]
            if row > 18:
                offset = 4
                row = 1

            # Light mode colours
            if row == 1:
                pad_y = (10, 0)
            else:
                pad_y = 5
            lbl_property = ctk.CTkLabel(master=widget_frame, text=' ' + key)
            lbl_property.grid(row=row, column=1 + offset, sticky='w', pady=pad_y)
            btn_property = ctk.CTkButton(master=widget_frame,
                                         fg_color=colour,
                                         width=button_width,
                                         height=button_height,
                                         text='',
                                         command=lambda widget_property=key: self.colour_picker(widget_property),
                                         corner_radius=3)
            btn_property.grid(row=row, column=0 + offset, sticky='e', pady=pad_y)
            button_dict = {"button": btn_property, "colour": colour, 'label': lbl_property}
            self.widgets[key] = button_dict
            # lbl_colour_code = ctk.CTkLabel(master=palette_frame, text=colour)
            # lbl_colour_code.grid(row=row, column=2 + offset, sticky='w', pady=pad_y)

            row += 1

    def _refresh_preview(self):
        try:
            if self.process:
                self.process.terminate()
        except NameError:
            pass
        with open(self._wip_json, "w") as f:
            json.dump(self.json_data, f, indent=2)
        self.process = None
        self.launch_preview()

    def close_controller(self):
        if self._json_state == 'dirty':
            confirm = CBtkMessageBox(title='Confirm Action',
                                     message=f'You have unsaved changes. Are you sure you wish to quit?',
                                     button1_text='Yes',
                                     button2_text='No')
            if confirm.choice == 2:
                return
        try:
            if self.process:
                self.process.terminate()
        except AttributeError:
            pass
        self._save_geometry()
        self.app.destroy()

    def launch_preview(self):
        appearance_mode = self.opm_mode.get()
        with open(self._wip_json, "w") as f:
            json.dump(self.json_data, f, indent=2)
        self._btn_refresh.configure(state=tk.NORMAL)
        designer = os.path.basename(__file__)
        if self.process is None:
            program = ['python', designer, '-a', appearance_mode, '-t', self._wip_json]
            self.process = sp.Popen(program)

    def _restore_geometry(self):
        geometry_ini = self._app_home / 'controller.ini'
        try:
            # if the file is there
            # get geometry from file
            ini_file = open(geometry_ini, 'r')
            self.app.geometry(ini_file.read())
            ini_file.close()
            # A bit of a dirty trick here. We are only interested in restoring the
            # window position - not its dimensions, and so we override the dimensions.
            self.app.geometry("173x800")

        except FileNotFoundError:
            # if the file is not there, create the file and use default
            # then use default geometry.
            open(geometry_ini, 'w')
            ini_file = open(geometry_ini, 'w')
            ini_file.close()
            self.app.geometry("173x775+347+93")

    def _save_geometry(self):
        # save current geometry to the ini file
        geometry_ini = self._app_home / 'controller.ini'
        geometry = self.app.geometry()
        with open(geometry_ini, 'w') as ini_file:
            ini_file.write(geometry)
            ini_file.close()

    def _save_json(self):
        shutil.copyfile(self._wip_json, self._source_json_file)
        theme_file = os.path.basename(self._source_json_file)
        self._json_state = 'clean'
        self._status_bar.set_status_text(status_text=f'Theme file, {theme_file}, saved successfully!')


class Preview():
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700

    def __init__(self, theme='green', appearance_mode='Dark'):

        platform = sys.platform
        if platform == "win32":
            self._platform = "Windows"
        elif platform == "darwin":
            self._platform = "MacOS"
        else:
            self._platform = "Linux"

        if platform == "Windows":
            self._home_dir = os.getenv("UserProfile")
        else:
            self._home_dir = os.getenv("HOME")

        # Initialise class properties
        self._home_dir = Path(self._home_dir)
        self._app_home = self._home_dir / '.ctk_theme_maker'
        self._config_file = self._app_home / 'ctk_theme_maker.ini'

        self._render_state = tk.NORMAL

        self._expand_palette = int(self._config_property_val('auto_save', 'expand_palette'))
        self._render_disabled = int(self._config_property_val('auto_save', 'render_disabled'))

        self._appearance_mode = appearance_mode
        self._theme = theme

        self.preview = ctk.CTk()
        self.preview.protocol("WM_DELETE_WINDOW", self.block_closing)

        if theme in bespoke_themes:
            json_home = '/home/clive/PycharmProjects/albert/venv/lib/python3.8/site-packages/customtkinter/assets/themes'
            json_path = f'{json_home}/{theme}.json'
            # ctk.set_default_color_theme(json_path)
        else:
            pass
            # ctk.set_default_color_theme(self._theme)

        themes = ctk.ThemeManager.built_in_themes
        for this_theme in bespoke_themes:
            themes.append(this_theme)
        ctk.set_default_color_theme(self._theme)
        ctk.set_appearance_mode(self._appearance_mode)

        self.preview.geometry(f'{230}x{680}+900+100')
        self.preview.update_idletasks()
        screen_width = self.preview.winfo_width()
        screen_height = self.preview.winfo_height()

        # self.preview.minsize(screen_width, screen_height)
        # self.preview.maxsize(screen_width, screen_height)

        self.left_frame = ctk.CTkFrame(master=self.preview)
        self.left_frame.grid(row=0, column=0, padx=2, pady=2, sticky='ns')

        self.right_frame = ctk.CTkFrame(master=self.preview)
        self.right_frame.grid(row=0, column=1, padx=2, pady=2, sticky='ns')

        self.palette_frame = ctk.CTkFrame(master=self.right_frame)
        self.palette_frame.grid(row=1, column=0, padx=2, pady=5, sticky='ns')
        self.right_frame.rowconfigure(1, weight=1)

        self.control_frame = ctk.CTkFrame(master=self.left_frame)
        self.control_frame.grid(row=0, column=0, padx=5, pady=5, sticky='we')

        self.left_frame.rowconfigure(0, weight=0)
        self.left_frame.rowconfigure(1, weight=1)

        self._widget_frame = ctk.CTkFrame(master=self.left_frame)
        self._widget_frame.grid(row=1, column=0, padx=2, pady=(0, 5))

        lbl_control = ctk.CTkLabel(master=self.control_frame,
                                   text_font=HEADING_FONT,
                                   text='Preview Controls',
                                   justify=tk.CENTER)
        lbl_control.grid(row=0, column=0, padx=(30, 0))

        self._tk_expand_palette = tk.StringVar(master=self.control_frame)
        self._swt_show_palette = ctk.CTkSwitch(master=self.control_frame,
                                               text='Show Palette',
                                               variable=self._tk_expand_palette,
                                               command=self._toggle_palette_display)
        self._swt_show_palette.grid(row=1, column=0, pady=10, padx=10, sticky='w')

        self._swt_render_disabled = ctk.CTkSwitch(master=self.control_frame, text='Render as Disabled',
                                                  # variable=self._render_disabled,
                                                  command=self.toggle_render_disabled)
        self._swt_render_disabled.grid(row=2, column=0, pady=(10, 10), padx=10)

        self.launch_widget_preview()

        if self._expand_palette == 0:
            self._swt_show_palette.deselect()
        else:
            self._swt_show_palette.select()

        if self._render_disabled == 0:
            self._swt_render_disabled.deselect()
        else:
            self._swt_render_disabled.select()

        self.preview.mainloop()

    def _config_property_val(self, section: str, key: str):
        """Accept a config file section and key then return the associated value last stored in theme_make.ini"""
        config = ConfigParser()
        config.read(self._config_file)
        config_value = config.get(section, key)
        return config_value

    def launch_widget_preview(self):
        def button_callback():
            print("Button click", self.combobox_1.get())

        def slider_callback(value):
            self.progressbar_1.set(value)

        js = open(self._theme)
        json_text = json.load(js)

        palette_frame = self.palette_frame
        palette_frame.grid(row=1)

        widget_frame = self._widget_frame

        basename_theme = os.path.basename(theme)
        self.preview.title(f'Theme Preview [ {appearance_mode} / {basename_theme} ]')
        colours = json_text["color"]

        sorted_tuples = sorted(colours.items(), key=operator.itemgetter(0))
        row = 1
        offset = 0
        button_width = 30
        button_height = 30
        self._buttons = {}

        for key, value in sorted_tuples:
            if appearance_mode == 'Light':
                colour = value[0]
            else:
                colour = value[1]
            if row > 18:
                offset = 4
                row = 1

            # Light mode colours
            if row == 1:
                pad_y = (10, 0)
            else:
                pad_y = 5
            cat = ctk.CTkLabel(master=palette_frame, text=key + ': ')
            cat.grid(row=row, column=0 + offset, sticky='e', pady=pad_y)
            self._buttons[key] = ctk.CTkButton(master=palette_frame,
                                               fg_color=colour,
                                               width=button_width,
                                               height=button_height,
                                               text='',
                                               corner_radius=3,
                                               state=self._render_state,
                                               command=lambda colour_code=colour: self.copy_colour_code(colour_code))
            self._buttons[key].grid(row=row, column=1 + offset, sticky='e', pady=pad_y)
            lbl_colour_code = ctk.CTkLabel(master=palette_frame, text=colour)
            lbl_colour_code.grid(row=row, column=2 + offset, sticky='w', pady=pad_y)

            row += 1

        lbl_heading = ctk.CTkLabel(master=widget_frame,
                                   text='Widget Preview',
                                   text_font=HEADING_FONT,
                                   justify=tk.CENTER)

        lbl_heading.pack(pady=12, padx=10)

        label_1 = ctk.CTkLabel(master=widget_frame, justify=tk.LEFT)
        label_1.pack(pady=12, padx=10)

        self.progressbar_1 = ctk.CTkProgressBar(master=widget_frame)
        self.progressbar_1.pack(pady=12, padx=10)

        self.button_1 = ctk.CTkButton(master=widget_frame, command=button_callback)
        self.button_1.pack(pady=12, padx=10)

        self.slider_1 = ctk.CTkSlider(master=widget_frame, command=slider_callback, from_=0, to=1)
        self.slider_1.pack(pady=12, padx=10)
        self.slider_1.set(0.5)

        self.entry_1 = ctk.CTkEntry(master=widget_frame, placeholder_text="CTkEntry")
        self.entry_1.pack(pady=12, padx=10)

        self.entry_2 = ctk.CTkEntry(master=widget_frame, placeholder_text="CTkEntry2")
        self.entry_2.pack(pady=12, padx=10)

        self.optionmenu_1 = ctk.CTkOptionMenu(widget_frame,
                                              values=["Option 1", "Option 2", "CTkOOption 42..."])
        self.optionmenu_1.pack(pady=12, padx=10)
        self.optionmenu_1.set("CTkOptionMenu")

        self.combobox_1 = ctk.CTkComboBox(widget_frame, values=["Option 1", "Option 2", "Option 42..."])
        self.combobox_1.pack(pady=12, padx=10)
        self.combobox_1.set("CTkComboBox")

        self.checkbox_1 = ctk.CTkCheckBox(master=widget_frame)
        self.checkbox_1.pack(pady=12, padx=10)

        self.radiobutton_var = tk.IntVar(value=1)

        self.radiobutton_1 = ctk.CTkRadioButton(master=widget_frame, variable=self.radiobutton_var, value=1)
        self.radiobutton_1.pack(pady=12, padx=10)

        self.radiobutton_2 = ctk.CTkRadioButton(master=widget_frame, variable=self.radiobutton_var, value=2)
        self.radiobutton_2.pack(pady=12, padx=10)

        self.switch_1 = ctk.CTkSwitch(master=widget_frame)
        self.switch_1.pack(pady=12, padx=10)

    def _toggle_palette_display(self):
        show_palette = self._swt_show_palette.get()
        # self.preview.attributes('-zoomed', False)
        if show_palette:
            # self.preview.geometry(f'{950}x{800}-100+100')
            self.preview.geometry(f'{870}x{745}')
        else:
            self.preview.geometry(f'{230}x{745}')
        self._update_config(section='auto_save', option='expand_palette', value=show_palette)

    def toggle_render_disabled(self):
        enable = self._swt_render_disabled.get()
        if enable == 0:
            render_state = tk.NORMAL
        else:
            render_state = tk.DISABLED
        self.button_1.configure(state=render_state)
        self.slider_1.configure(state=render_state)
        self.entry_1.configure(state=render_state)
        self.entry_2.configure(state=render_state)
        self.optionmenu_1.configure(state=render_state)
        self.combobox_1.configure(state=render_state)
        self.checkbox_1.configure(state=render_state)
        self.radiobutton_1.configure(state=render_state)
        self.radiobutton_2.configure(state=render_state)
        self.switch_1.configure(state=render_state)
        self._update_config(section='auto_save', option='render_disabled', value=enable)

    def _update_config(self, section, option, value):
        """Update our config file with the specified value."""
        config = ConfigParser()
        config.read(self._config_file)
        config.set(section=section, option=option, value=str(value))
        with open(self._config_file, 'w') as f:
            config.write(f)

    @staticmethod
    def copy_colour_code(code):
        pyperclip.copy(code)
        print(f'cColour copied: {code}')

    def block_closing(self, event=0):
        pass

    def load_image(self, path, image_size):
        """ load rectangular image with path relative to PATH """
        return ImageTk.PhotoImage(Image.open(PATH + path).resize((image_size, image_size)))

    def _restore_geometry(self):
        geometry_ini = self._app_home / 'controller.ini'
        try:
            # if the file is there
            # get geometry from file
            ini_file = open(geometry_ini, 'r')
            self.app.geometry(ini_file.read())
            ini_file.close()
        except FileNotFoundError:
            # if the file is not there, create the file and use default
            # then use default geometry.
            open(geometry_ini, 'w')
            ini_file = open(geometry_ini, 'w')
            ini_file.close()
            self.preview.geometry("640x400+100+200")

    def _save_geometry(self):
        # save current geometry to the ini file
        geometry_ini = self._app_home / 'controller.ini'

        with open(geometry_ini, 'w') as ini_file:
            ini_file.write(self.preview.geometry())
            ini_file.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(formatter_class=SortingHelpFormatter
                                 , description=f"{prog}: Welcome to CTk Theme Designer, which is designed to help you "
                                               f"design, themes to run with the customkinter framework")

    ap.add_argument("-a", '--set-appearance', required=False, action="store",
                    help="Set the customkinter appearance mode. Used for colour preview only.",
                    dest='appearance_mode', default='Dark')

    ap.add_argument("-t", '--set-theme', required=False, action="store",
                    help="Set the customkinter theme. Used for colour preview only.",
                    dest='theme', default=None)

    args_list = vars(ap.parse_args())
    appearance_mode = args_list["appearance_mode"]
    theme = args_list["theme"]

    # If theme is set, we assume we are running in colour "preview" mode.
    if theme:
        launch_widget_preview(appearance_mode=appearance_mode, theme=theme)
    else:
        controller = Controller()

