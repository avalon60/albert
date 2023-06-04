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
assets_dir = prog_dir / 'assets'
etc_dir = assets_dir / 'etc'
views_dir = assets_dir / 'views'

home_dir = os.getenv("HOME")

PATH = os.path.dirname(os.path.realpath(__file__))
IMAGES = Path(f'{PATH}/assets/images')

default_view_file = views_dir / 'Text.json'
with open(default_view_file) as f:
    WIDGET_ATTRIBUTES = json.load(f)


def str_mode_to_int():
    appearance_mode = ctk.get_appearance_mode()
    if appearance_mode == "Light":
        return 0
    return 1


def get_color_from_name(name: str):
    int_mode = str_mode_to_int()
    return ThemeManager.theme["color"][name][int_mode]


def load_image(path, image_size):
    """ load rectangular image with path relative to PATH """
    return ImageTk.PhotoImage(Image.open(path).resize((image_size, image_size)))


class CBtkMessageBox(object):
    """Message box class for customtkinter. Up to 4 buttons are rendered where their respective buttonN_text
    parameter has a value. An integer value us returned, dependant upon the respective button number, of the button
    pressed. """

    def __init__(self, title='CBtkMessageBox',
                 message='',
                 button_height=2,
                 button1_text='OK',
                 button2_text='',
                 button3_text='',
                 button4_text=''):

        button_width = 100
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
        self.frm_main = ctk.CTkFrame(master=self.root)
        self.frm_main.pack(fill=tk.BOTH)
        self.frm_main.configure(corner_radius=0)
        # self.frm_main.columnconfigure(0, weight=1)
        # self.root.rowconfigure(0, weight=1)
        # self.frm_main.rowconfigure(0, weight=1)

        self.frm_message = ctk.CTkFrame(master=self.frm_main)
        self.frm_message.pack(expand=True, fill=tk.BOTH)
        self.frm_message.configure(corner_radius=0)

        self.frm_buttons = ctk.CTkFrame(master=self.frm_main, corner_radius=0)
        self.frm_buttons.pack(side=tk.BOTTOM, fill=tk.X, ipady=20)
        self.frm_buttons.configure(corner_radius=0)
        # self.frm_main.rowconfigure(1, weight=0)

        # Creating Label For message
        self.lbl_message = ctk.CTkLabel(self.frm_message, text=self.message)
        self.lbl_message.pack(fill=tk.BOTH, padx=10, pady=(20, 10))

        button_count = 2
        buttons_width = button_count * button_width
        # self.root.update_idletasks()
        # width = self.frm_buttons.winfo_width()
        button_count = 1
        if button2_text:
            button_count += 1
        if button3_text:
            button_count += 1
        if button4_text:
            button_count += 1

        if button_count == 1:
            pad_x = 50
            self.root.geometry("320x120")
        elif button_count == 2:
            pad_x = 30
            self.root.geometry("320x120")
        elif button_count == 3:
            pad_x = 20
            self.root.geometry("420x120")
        else:
            self.root.geometry("440x120")
            pad_x = 5

        pad_y = (10, 0)

        # Create a button, corresponding to button1_text
        self.button1_text = ctk.CTkButton(self.frm_buttons,
                                          text=self.button1_text,
                                          command=self.click1,
                                          width=button_width,
                                          height=button_height)
        self.button1_text.grid(row=0, column=0, padx=pad_x, pady=pad_y)

        # Create a button, corresponding to  button1_text
        # self.button1_text.info = self.button1_text.place_info()

        # Create a button, corresponding to  button2_text
        if button2_text:
            self.button2_text = ctk.CTkButton(self.frm_buttons,
                                              text=self.button2_text,
                                              command=self.click2,
                                              width=button_width,
                                              height=button_height)
            self.button2_text.grid(row=0, column=1, padx=pad_x, pady=pad_y)
        # Create a button, corresponding to  button3_text
        if button3_text:
            self.button3_text = ctk.CTkButton(self.frm_buttons,
                                              text=self.button3_text,
                                              command=self.click3,
                                              width=button_width,
                                              height=button_height)
            self.button3_text.grid(row=0, column=2, padx=pad_x, pady=pad_y)
        # Create a button, corresponding to button4_text
        if button4_text:
            self.button4_text = ctk.CTkButton(self.frm_buttons,
                                              text=self.button4_text,
                                              command=self.click4,
                                              width=button_width,
                                              height=button_height)
            self.button4_text.grid(row=0, column=3, padx=pad_x, pady=pad_y)

        # Make the message box visible
        self.frm_main.update_idletasks()
        width = self.frm_main.winfo_width()
        height = self.frm_main.winfo_height()

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


def launch_preview_panel(appearance_mode, theme):
    preview_panel = PreviewPanel(appearance_mode=appearance_mode, theme=theme)


class SortingHelpFormatter(HelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


class CBtkToolTip(object):
    """
    Create a tooltip for a given widget.
    """

    def __init__(self, widget, text='widget info', bg_colour='#777777'):
        self._bg_colour = bg_colour
        self._wait_time = 400  # milli-seconds
        self._wrap_length = 300  # pixels
        self._widget = widget
        self._text = text
        self._widget.bind("<Enter>", self.enter)
        self._widget.bind("<Leave>", self.leave)
        self._widget.bind("<ButtonPress>", self.leave)
        self._id = None
        self._tw = None

    def enter(self, event=None):
        self._schedule()

    def leave(self, event=None):
        self._unschedule()
        self.hide_tooltip()

    def _schedule(self):
        self._unschedule()
        self._id = self._widget.after(self._wait_time, self.show_tooltip)

    def _unschedule(self):
        id = self._id
        self._id = None
        if id:
            self._widget.after_cancel(id)

    def show_tooltip(self, event=None):
        x = y = 0
        x, y, cx, cy = self._widget.bbox("insert")
        x += self._widget.winfo_rootx() + 40
        y += self._widget.winfo_rooty() + 20
        # creates a toplevel window
        self._tw = tk.Toplevel(self._widget)
        # Leaves only the label and removes the app window
        self._tw.wm_overrideredirect(True)
        self._tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self._tw, text=self._text, justify='left',
                         background=self._bg_colour, relief='solid', borderwidth=1,
                         wraplength=self._wrap_length)
        label.pack(ipadx=1)

    def hide_tooltip(self):
        tw = self._tw
        self._tw = None
        if tw:
            tw.destroy()


class CBtkStatusBar(tk.Entry):
    """Create a status bar on the parent window. Messages can be writtento the status bar using the set_status_text
    method. The status_text_life can be used to auto-erase the status text after the specified number of seconds. The
    default value, 0, disables the auto-erase feature."""

    def __init__(self,
                 master,
                 status_text_life=10,
                 use_grid=True):
        super().__init__()

        self._message_id = None
        self._master = master
        grid_size = master.grid_size()
        grid_columns = grid_size[0]
        grid_rows = grid_size[1]
        self._master.update_idletasks()
        self._app_width = self._master.winfo_width()
        self._status_text_life = status_text_life
        assert isinstance(self._status_text_life, int)

        self._default_fg_color = get_color_from_name('frame_low')

        self._status_bar = ctk.CTkLabel(master, relief=tk.SUNKEN, text='', anchor='w', width=self._app_width,
                                        fg_color=self._default_fg_color)
        # breadcrumb
        if use_grid:
            self._status_bar.grid(row=grid_rows + 1, column=0, padx=0, pady=0, columnspan=grid_columns, sticky='ew')
        else:
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

    @staticmethod
    def _get_property_by_name(prop_name: str):
        return ThemeManager.theme[prop_name]

    def set_status_text_life(self, status_text_life):
        self._status_text_life = status_text_life


class ControlPanel:
    initial_height = 840
    expanded_height = initial_height
    # initial_width = 180
    initial_width = 555
    expanded_width_small = 555
    expanded_width_large = 555

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
            self.user_name = os.getenv("LOGNAME")
        else:
            self.user_name = os.getenv("USER")
            self._home_dir = os.getenv("HOME")

        # Initialise class properties
        self._home_dir = Path(self._home_dir)
        self._app_home = self._home_dir / '.ctk_theme_maker'
        self._appearance_mode = 'Light'
        self.process = None
        self.app.protocol("WM_DELETE_WINDOW", self._close_panels)
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

        self._enable_tooltips = int(self._config_property_val('preferences', 'enable_tooltips'))
        self._theme_json_dir = Path(self._config_property_val('preferences', 'theme_json_dir'))
        control_panel_theme = self._config_property_val('preferences', 'control_panel_theme')
        control_panel_theme = control_panel_theme + '.json'

        self._control_panel_theme = str(self._theme_json_dir / control_panel_theme)
        # The control_panel_mode holds the  customtkinter appearance mode (Dark / Light)
        self._control_panel_mode = self._config_property_val('preferences', 'control_panel_mode')
        self._temp_dir = Path(self._config_property_val('system', 'temp_dir'))
        self._tooltips_enabled_setting = self._config_property_val('preferences', 'enable_tooltips')

        try:
            ctk.set_default_color_theme(self._control_panel_theme)
        except FileNotFoundError:
            ctk.set_default_color_theme('blue')
            print(f'Preferred Control Panel, theme file not found. Falling back to "blue" theme.')
        ctk.set_appearance_mode(self._control_panel_mode)

        self._restore_controller_geometry()

        # self.app.geometry(f'{180}x{ControlPanel.initial_height}+{winfo_x}+{winfo_y}')
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
        self._control_frame.rowconfigure(1, weight=1)
        self._button_frame = ctk.CTkFrame(master=self._control_frame)
        button_frame = self._button_frame
        button_frame.grid(row=1, column=0, columnspan=1, sticky='ns', padx=(5, 5), pady=(5, 5))

        self._widget_frame = ctk.CTkFrame(master=self._control_frame)
        self._widget_frame.grid(row=1, column=1, rowspan=1, sticky='nswe', padx=(0, 5), pady=(5, 5))
        self._status_bar = CBtkStatusBar(master=self.app,
                                         status_text_life=10,
                                         use_grid=False)
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

        self.lbl_filter_view = ctk.CTkLabel(master=self._button_frame,
                                            text='Properties View:')
        self.lbl_filter_view.grid(row=7, column=0, sticky='w', pady=(10, 0), padx=(10, 10))

        widget_categories = all_widget_categories(WIDGET_ATTRIBUTES)
        views_list = self._view_list()
        self.tk_filter_view = tk.StringVar(value='Default')
        self.opm_filter_view = ctk.CTkOptionMenu(master=self._button_frame,
                                                 # command=self.set_filter_display,
                                                 variable=self.tk_filter_view,
                                                 values=views_list,
                                                 state=tk.DISABLED)
        self.opm_filter_view.grid(row=8, column=0)

        self.lbl_filter = ctk.CTkLabel(master=self._button_frame, text='Filter Properties:')
        self.lbl_filter.grid(row=9, column=0, sticky='w', pady=(10, 0), padx=(10, 10))

        widget_categories = all_widget_categories(WIDGET_ATTRIBUTES)
        self.tk_filter = tk.StringVar()
        self.opm_filter = ctk.CTkOptionMenu(master=self._button_frame, values=widget_categories,
                                            variable=self.tk_filter,
                                            command=lambda: self._set_filtered_widget_display(self.tk_filter),
                                            state=tk.DISABLED)
        self.opm_filter.grid(row=10, column=0)

        # btn_launch = ctk.CTkButton(master=frame, text='Close Colours', command=self.remove_colours)
        # btn_launch.grid(row=0, column=1, padx=5, pady=5)

        self._btn_refresh = ctk.CTkButton(master=button_frame, text='Update Preview',
                                          command=self._refresh_preview,
                                          state=tk.DISABLED)
        self._btn_refresh.grid(row=11, column=0, padx=5, pady=(60, 0))
        # We don't render the refresh just yet. This is to replace the preview button once initial preview is elected.

        self._btn_reset = ctk.CTkButton(master=button_frame,
                                        text='Reset',
                                        state=tk.DISABLED,
                                        command=self.reset_theme)
        self._btn_reset.grid(row=12, column=0, padx=5, pady=(60, 5))

        self._btn_create = ctk.CTkButton(master=button_frame,
                                         text='Create',
                                         command=self._create_theme)
        self._btn_create.grid(row=14, column=0, padx=5, pady=(5, 5))

        self._btn_mirror = ctk.CTkButton(master=button_frame,
                                         text='Mirror Mode',
                                         state=tk.DISABLED,
                                         command=self._mirror_appearance_mode)
        self._btn_mirror.grid(row=15, column=0, padx=5, pady=(5, 5))

        self._btn_save = ctk.CTkButton(master=button_frame,
                                       text='Save',
                                       state=tk.DISABLED,
                                       command=self._save_theme)
        self._btn_save.grid(row=18, column=0, padx=5, pady=(30, 5))

        self._btn_save_as = ctk.CTkButton(master=button_frame,
                                          text='Save As',
                                          state=tk.DISABLED,
                                          command=self._save_theme_as)
        self._btn_save_as.grid(row=20, column=0, padx=5, pady=(5, 5))

        btn_quit = ctk.CTkButton(master=button_frame, text='Quit', command=self._close_panels)
        btn_quit.grid(row=30, column=0, padx=5, pady=(60, 5))

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
                self._btn_reset.configure(state=tk.NORMAL)
                self._btn_save.configure(state=tk.NORMAL)
                self._btn_save_as.configure(state=tk.NORMAL)
                self._btn_mirror.configure(state=tk.NORMAL)
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
            f.write('expand_palette = 1\n')
            f.write('render_disabled = 1\n')
            f.write('[preferences]\n')
            f.write(f'theme_author = {self.user_name}\n')
            f.write('control_panel_theme = oceanix\n')
            f.write('control_panel_mode = Dark\n')
            f.write(f'theme_json_dir = {assets_dir}/themes\n')
            f.write(f'enable_tooltips = 1\n')

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
        file_menu.add_command(label='Quit', command=self._close_panels)

        # Now add a Tools sub-menu option
        tools_menu = tk.Menu(des_menu)
        tools_menu.config(background=background, foreground=foreground)
        des_menu.add_cascade(label='Tools', menu=tools_menu)
        tools_menu.add_command(label='Preferences', command=self._launch_preferences)

    def _launch_preferences(self):
        self._top_prefs = ctk.CTkToplevel(master=self.app)
        self._top_prefs.title('Theme Builder Preferences')
        # Make preferences dialog modal
        self._top_prefs.grab_set()
        self._top_prefs.rowconfigure(0, weight=1)
        self._top_prefs.rowconfigure(1, weight=0)
        self._top_prefs.columnconfigure(0, weight=1)

        self._new_theme_json_dir = None

        frm_main = ctk.CTkFrame(master=self._top_prefs, corner_radius=0)
        frm_main.grid(column=0, row=0, sticky='ew')

        frm_widgets = ctk.CTkFrame(master=frm_main, corner_radius=0)
        frm_widgets.grid(column=0, row=0, padx=5, pady=5, sticky='ew')

        frm_buttons = ctk.CTkFrame(master=frm_main, corner_radius=0)
        frm_buttons.grid(column=0, row=1, padx=5, pady=(5, 0), sticky='ew')

        widget_start_row = 0
        lbl_author_name = ctk.CTkLabel(master=frm_widgets, text='Author')
        lbl_author_name.grid(row=widget_start_row, column=0, padx=(80, 0), pady=(0, 5), sticky='w')

        self.tk_author_name = tk.StringVar(value=self.user_name)
        self.ent_author_name = ctk.CTkEntry(master=frm_widgets,
                                            textvariable=self.tk_author_name,
                                            width=160)
        self.ent_author_name.grid(row=widget_start_row, column=1, sticky='w')

        widget_start_row += 1
        lbl_theme = ctk.CTkLabel(master=frm_widgets, text='Control Panel Theme')
        lbl_theme.grid(row=widget_start_row, column=0, pady=(0, 5))

        control_panel_theme = os.path.splitext(self._control_panel_theme)[0]
        control_panel_theme = os.path.basename(control_panel_theme)
        self._tk_control_panel_theme = tk.StringVar(value=control_panel_theme)
        self._opm_control_panel_theme = ctk.CTkOptionMenu(master=frm_widgets,
                                                          variable=self._tk_control_panel_theme,
                                                          values=self._themes_list())
        self._opm_control_panel_theme.grid(row=widget_start_row, column=1, pady=5, sticky='w')
        widget_start_row += 1

        lbl_mode = ctk.CTkLabel(master=frm_widgets, text='Appearance Mode')
        lbl_mode.grid(row=widget_start_row, column=0, padx=(25, 0), sticky='w')

        # The control_panel_mode holds the  customtkinter appearance mode (Dark / Light)
        self._tk_appearance_mode_var = tk.StringVar(value=self._control_panel_mode)
        rdo_light = ctk.CTkRadioButton(master=frm_widgets, text='Light', variable=self._tk_appearance_mode_var,
                                       value='Light')
        rdo_light.grid(row=widget_start_row, column=1, sticky='w')
        widget_start_row += 1

        rdo_dark = ctk.CTkRadioButton(master=frm_widgets, text='Dark', variable=self._tk_appearance_mode_var,
                                      value='Dark')
        rdo_dark.grid(row=widget_start_row, column=1, pady=5, sticky='w')
        widget_start_row += 1

        lbl_enable_tooltips = ctk.CTkLabel(master=frm_widgets, text='Enable tooltips')
        lbl_enable_tooltips.grid(row=widget_start_row, column=0, padx=(40, 0), sticky='e')

        self._tk_enable_tooltips = tk.IntVar(master=frm_widgets)
        self._tk_enable_tooltips.set(self._enable_tooltips)
        self._swt_enable_tooltips = ctk.CTkSwitch(master=frm_widgets,
                                                  text='',
                                                  variable=self._tk_enable_tooltips,
                                                  command=self._get_tooltips_setting)
        self._swt_enable_tooltips.grid(row=widget_start_row, column=1, pady=10, sticky='w')
        widget_start_row += 1

        self._folder_image = load_image(IMAGES / 'folder.png', 20)
        lbl_theme_json_dir = ctk.CTkLabel(master=frm_widgets, text='Theme JSON location')
        lbl_theme_json_dir.grid(row=widget_start_row, column=0, pady=5)

        btn_theme_json_dir = ctk.CTkButton(master=frm_widgets,
                                           text='',
                                           width=30,
                                           height=30,
                                           fg_color='#748696',
                                           image=self._folder_image,
                                           command=self._preferred_json_location)
        btn_theme_json_dir.grid(row=widget_start_row, column=1, pady=5, sticky='w')
        widget_start_row += 1
        # Control buttons
        btn_close = ctk.CTkButton(master=frm_buttons, text='Cancel', command=self._top_prefs.destroy)
        btn_close.grid(row=0, column=0, padx=(5, 35), pady=5)

        btn_save = ctk.CTkButton(master=frm_buttons, text='Save', command=self._save_preferences)
        btn_save.grid(row=0, column=1, padx=(35, 5), pady=5)

    def _save_preferences(self):
        # Save JSON Directory:
        if self._new_theme_json_dir is not None:
            self._theme_json_dir = self._new_theme_json_dir
            self._update_config(section='preferences', option='theme_json_dir', value=self._theme_json_dir)
            self._json_files = self._themes_list()
            self.opm_theme.configure(values=self._json_files)

        self.user_name = self.tk_author_name.get()
        self._update_config(section='preferences', option='theme_author',
                            value=self.user_name)
        self._update_config(section='preferences', option='control_panel_theme',
                            value=self._opm_control_panel_theme.get())
        self._update_config(section='preferences', option='control_panel_mode',
                            value=self._tk_appearance_mode_var.get())
        self._top_prefs.destroy()
        self._status_bar.set_status_text(status_text=f'Preferences saved.')

        self._enable_tooltips = self._tooltips_enabled_setting
        self._update_config(section='preferences', option='enable_tooltips',
                            value=self._enable_tooltips)

    def _preferred_json_location(self):
        self._new_theme_json_dir = Path(tk.filedialog.askdirectory(initialdir=self._theme_json_dir))

    def _set_filtered_widget_display(self, view_name):
        view_file = views_dir / view_name +'.json'
        with open(view_file) as f:
            self._widget_attributes = json.load(f)
        return self._widget_attributes

    def _themes_list(self):
        """This method generates a list of theme names, based on the json files found in the themes folder
        (i.e. self._theme_json_dir). These are basically the theme file names, with the .json extension stripped out."""
        json_files = [file for file in os.listdir(self._theme_json_dir) if file.endswith('.json')]
        theme_names = []
        for file in json_files:
            theme_name = os.path.splitext(file)[0]
            theme_names.append(theme_name)
        theme_names.sort()
        return theme_names

    @staticmethod
    def _view_list():
        """This method generates a list of view names, based on the json files found in the assets/views folder.
        These are basically the theme file names, with the .json extension stripped out."""
        json_files = [file for file in os.listdir(views_dir) if file.endswith('.json')]
        theme_names = []
        for file in json_files:
            theme_name = os.path.splitext(file)[0]
            theme_names.append(theme_name)
        theme_names.sort()
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
        self._source_json_file = self._theme_json_dir / self._theme_file
        if self._source_json_file:
            self._wip_json = self._temp_dir / self._theme_file
            shutil.copyfile(self._source_json_file, self._wip_json)
            with open(self._wip_json) as f:
                self.json_data = json.load(f)
            self._update_config(section='preferences', option='theme_json_dir', value=self._theme_json_dir)
            self.render_widget_properties()
            try:
                self._btn_refresh.configure(state=tk.NORMAL)
            except tk.TclError:
                pass
            # Enable buttons
            self.opm_mode.configure(state=tk.NORMAL)
            self.opm_filter.configure(state=tk.NORMAL)
            self._btn_save.configure(state=tk.NORMAL)
            self._btn_save_as.configure(state=tk.NORMAL)
            self._btn_mirror.configure(state=tk.NORMAL)
            self.opm_filter_view.configure(state=tk.NORMAL)
            self._btn_reset.configure(state=tk.DISABLED)
            self._btn_save.configure(state=tk.DISABLED)

            self.lbl_title.grid(row=0, column=0, columnspan=2, sticky='ew')
            self.app.geometry(f'{ControlPanel.expanded_width_large}x{ControlPanel.expanded_height}')
            self.opm_theme.configure(values=self._json_files)
            self._refresh_preview()
            self._status_bar.set_status_text(status_text_life=10,
                                             status_text=f'Theme file, {self._theme_file}, loaded. ')

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
        source_file = etc_dir / 'default.json'
        dialog = ctk.CTkInputDialog(master=None, text="Enter new theme name:", title="Create New Theme")
        new_theme = dialog.get_input()
        if new_theme:
            # If user has included a ".json" extension, remove it, because we add one below.
            new_theme_basename = os.path.splitext(new_theme)[0]
            new_theme = new_theme_basename + '.json'
            new_theme_path = self._theme_json_dir / new_theme
            shutil.copyfile(source_file, new_theme_path)
            self._json_files = self._themes_list()
            self.opm_theme.configure(values=self._json_files)
            self.opm_theme.set(new_theme_basename)

    def _save_theme_as(self):
        source_file = self._source_json_file
        dialog = ctk.CTkInputDialog(master=None, text="Enter new theme name:", title="Create New Theme")
        new_theme = dialog.get_input()
        if new_theme:
            # If user has included a ".json" extension, remove it, because we add one below.
            new_theme = os.path.splitext(new_theme)[0]
            self.opm_theme.configure(command=None)
            self.opm_theme.set(new_theme)
            self.opm_theme.configure(command=self._load_theme)
            new_theme = new_theme + '.json'
            new_theme_path = self._theme_json_dir / new_theme
            shutil.copyfile(source_file, new_theme_path)
            self._load_theme()
            self._json_files = self._themes_list()
            self.opm_theme.configure(values=self._json_files)

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
            self.app.geometry(f'{ControlPanel.expanded_width_large}x{ControlPanel.expanded_height}')
        else:
            self.app.geometry(f'{ControlPanel.expanded_width_small}x{ControlPanel.expanded_height}')
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
                                         border_width=1,
                                         fg_color=colour,
                                         width=button_width,
                                         height=button_height,
                                         text='',
                                         command=lambda widget_property=key: self.colour_picker(widget_property),
                                         corner_radius=3)
            btn_property.grid(row=row, column=0 + offset, padx=5, pady=pad_y)
            button_dict = {"button": btn_property, "colour": colour, 'label': lbl_property}
            self.widgets[key] = button_dict
            # lbl_colour_code = ctk.CTkLabel(master=palette_frame, text=colour)
            # lbl_colour_code.grid(row=row, column=2 + offset, sticky='w', pady=pad_y)

            row += 1

    def _mirror_appearance_mode(self):
        """This method allows us to copy our Dark configuration (if Sark is our current selection, to our Light and
        vice-versa """
        current_mode = self.opm_mode.get()

        if current_mode == 'Light':
            from_mode = 0
            to_mode = 1
            message = "Appearance mode, 'Light', copied to 'Dark."
        else:
            from_mode = 1
            to_mode = 0
            message = "Appearance mode, 'Dark', copied to 'Light."
        for widget_property, value in self.json_data['color'].items():
            pass
            self.json_data['color'][widget_property][to_mode] = self.json_data['color'][widget_property][from_mode]
        self._status_bar.set_status_text(status_text=message)

        self._btn_save.configure(state=tk.NORMAL)
        self._btn_reset.configure(state=tk.NORMAL)

        self._json_state = 'dirty'

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

    def _close_panels(self):
        if self._json_state == 'dirty':
            confirm = CBtkMessageBox(title='Confirm Action',
                                     message=f'You have unsaved changes. Do you wish to save these before quitting?',
                                     button1_text='Yes',
                                     button2_text='No')
            if confirm.choice == 1:
                self._save_theme()
        try:
            if self.process:
                self.process.terminate()
        except AttributeError:
            pass
        self._save_controller_geometry()
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

    def _restore_controller_geometry(self):
        geometry_ini = self._app_home / 'control_panel.ini'
        try:
            # if the file is there
            # get geometry from file
            ini_file = open(geometry_ini, 'r')
            self.app.geometry(ini_file.read())
            ini_file.close()
            # A bit of a dirty trick here. We are only interested in restoring the
            # window position - not its dimensions, and so we override the dimensions.
            self.app.geometry(f"{ControlPanel.initial_width}x{ControlPanel.initial_height}")

        except FileNotFoundError:
            # if the file is not there, create the file and use default
            # then use default geometry.
            open(geometry_ini, 'w')
            ini_file = open(geometry_ini, 'w')
            ini_file.close()
            self.app.geometry("173x775+347+93")

    def _save_controller_geometry(self):
        # save current geometry to the ini file
        geometry_ini = self._app_home / 'control_panel.ini'
        self.app.update()
        geometry = self.app.geometry()
        if geometry is None:
            print('ERROR: Could not establish screen geometry on exit!')
            return

        with open(geometry_ini, 'w') as ini_file:
            ini_file.write(geometry)
            ini_file.close()

    def _save_theme(self):
        with open(self._wip_json, "w") as f:
            json.dump(self.json_data, f, indent=2)
        shutil.copyfile(self._wip_json, self._source_json_file)
        theme_file = os.path.basename(self._source_json_file)
        self._json_state = 'clean'
        self._btn_reset.configure(state=tk.DISABLED)
        self._btn_save.configure(state=tk.DISABLED)
        self._status_bar.set_status_text(status_text=f'Theme file, {theme_file}, saved successfully!')

    def _get_tooltips_setting(self):
        self._tooltips_enabled_setting = self._tk_enable_tooltips.get()


class PreviewPanel:
    # initial_height = 830
    initial_height = 765
    initial_width = 235
    expanded_width = 636

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
        self._enable_tooltips = int(self._config_property_val('preferences', 'enable_tooltips'))
        self._enable_tooltips = self._config_property_val('preferences', 'theme_author')
        self._expand_palette = int(self._config_property_val('auto_save', 'expand_palette'))
        self._render_disabled = int(self._config_property_val('auto_save', 'render_disabled'))

        self._appearance_mode = appearance_mode
        self._theme = theme

        self.preview = ctk.CTk()
        self.preview.protocol("WM_DELETE_WINDOW", self.block_closing)
        self._restore_preview_geometry()
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

        screen_width = self.preview.winfo_width()
        screen_height = self.preview.winfo_height()

        # self.preview.minsize(screen_width, screen_height)
        # self.preview.maxsize(screen_width, screen_height)

        self.preview.columnconfigure(1, weight=1)
        self.left_frame = ctk.CTkFrame(master=self.preview)
        self.left_frame.grid(row=0, column=0, padx=2, pady=2, sticky='nsew')

        self.right_frame = ctk.CTkFrame(master=self.preview)
        self.right_frame.grid(row=0, column=1, padx=2, pady=2, sticky='nsew')

        self.preview.rowconfigure(1, weight=1)
        self.left_frame.rowconfigure(1, weight=1)
        self.right_frame.rowconfigure(0, weight=1)

        self.palette_frame = ctk.CTkFrame(master=self.right_frame)

        self.control_frame = ctk.CTkFrame(master=self.left_frame)
        self.control_frame.grid(row=0, column=0, padx=10, pady=5, sticky='we')

        self.left_frame.rowconfigure(0, weight=0)
        self.left_frame.rowconfigure(1, weight=1)

        self._widget_frame = ctk.CTkFrame(master=self.left_frame)
        self._widget_frame.grid(row=1, column=0, padx=10, pady=(0, 5))

        lbl_control = ctk.CTkLabel(master=self.control_frame,
                                   text_font=HEADING_FONT,
                                   text='Preview Controls',
                                   justify=tk.CENTER)
        lbl_control.grid(row=0, column=0, pady=(10, 0), padx=(30, 0))

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

        self._status_bar = CBtkStatusBar(master=self.preview,
                                         status_text_life=10)
        self.preview.bind("<Configure>", self._status_bar.auto_size_status_bar)

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

        show_colour_code = False
        js = open(self._theme)
        json_text = json.load(js)

        palette_frame = self.palette_frame
        # palette_frame.grid(row=1)

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
            lbl_property = ctk.CTkLabel(master=palette_frame, text=key + ': ')
            lbl_property.grid(row=row, column=0 + offset, sticky='e', pady=pad_y)
            self._buttons[key] = ctk.CTkButton(master=palette_frame,
                                               fg_color=colour,
                                               width=button_width,
                                               height=button_height,
                                               text='',
                                               corner_radius=3,
                                               border_width=1,
                                               state=self._render_state,
                                               command=lambda colour_code=colour: self.copy_colour_code(colour_code))
            self._buttons[key].grid(row=row, column=1 + offset, sticky='e', padx=5, pady=pad_y)

            reset_tooltip = CBtkToolTip(self._buttons[key],
                                        'Click colour tile, to copy colour code to clipboard.')
            if show_colour_code:
                lbl_colour_code = ctk.CTkLabel(master=palette_frame, text=colour)
                lbl_colour_code.grid(row=row, column=2 + offset, sticky='w', pady=pad_y)

            row += 1
        grid_row = 0
        pad_y = 12
        lbl_heading = ctk.CTkLabel(master=widget_frame,
                                   text='Widget Preview',
                                   text_font=HEADING_FONT,
                                   justify=tk.CENTER)

        lbl_heading.grid(row=grid_row, padx=5, pady=5)
        grid_row += 1

        label_1 = ctk.CTkLabel(master=widget_frame, justify=tk.LEFT)
        label_1.grid(row=grid_row, padx=5, pady=pad_y)
        grid_row += 1

        self.progressbar_1 = ctk.CTkProgressBar(master=widget_frame)
        self.progressbar_1.grid(row=grid_row, padx=5, pady=pad_y)
        grid_row += 1

        self.button_1 = ctk.CTkButton(master=widget_frame, command=button_callback, borderwidth=1)
        self.button_1.grid(row=grid_row, padx=5, pady=pad_y)
        grid_row += 1

        if 1 == 2:
            self.ttk_textbox = ctk.CTkTextbox(master=widget_frame, highlightthickness=0, width=10, height=4)
            self.ttk_textbox.grid(row=grid_row, column=0, padx=5, pady=(5, 0), sticky="nsew")
            self.ttk_textbox.insert(0.0,
                                    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor '
                                    'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, '
                                    'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo '
                                    'consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum '
                                    'dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, '
                                    'sunt in culpa qui officia deserunt mollit anim id est laborum.')

            # create scrollable textbox
            tk_textbox = tk.Text(master=widget_frame, highlightthickness=0, height=10, width=10)
            tk_textbox.grid(row=grid_row, column=0, sticky="nsew")

            # create CTk scrollbar
            ctk_textbox_scrollbar = ctk.CTkScrollbar(master=widget_frame, command=tk_textbox.yview)
            ctk_textbox_scrollbar.grid(row=grid_row, column=1, sticky="ns")
            # connect textbox scroll event to CTk scrollbar
            tk_textbox.configure(yscrollcommand=ctk_textbox_scrollbar.set)
            grid_row += 1

        self.slider_1 = ctk.CTkSlider(master=widget_frame, command=slider_callback, from_=0, to=1)
        self.slider_1.grid(row=grid_row, column=0, padx=5, pady=pad_y)
        grid_row += 1
        self.slider_1.set(0.5)

        self.entry_1 = ctk.CTkEntry(master=widget_frame, placeholder_text="CTkEntry")
        self.entry_1.grid(row=grid_row, padx=5, pady=pad_y)
        grid_row += 1

        self.entry_2 = ctk.CTkEntry(master=widget_frame, placeholder_text="CTkEntry2")
        self.entry_2.grid(row=grid_row, padx=5, pady=pad_y)
        grid_row += 1

        self.optionmenu_1 = ctk.CTkOptionMenu(widget_frame,
                                              values=["Option 1", "Option 2", "CTkOOption 42..."])
        self.optionmenu_1.grid(row=grid_row, padx=5, pady=pad_y)
        grid_row += 1
        self.optionmenu_1.set("CTkOptionMenu")

        self.combobox_1 = ctk.CTkComboBox(widget_frame, values=["Option 1", "Option 2", "Option 42..."])
        self.combobox_1.grid(row=grid_row, padx=5, pady=pad_y)
        grid_row += 1
        self.combobox_1.set("CTkComboBox")

        self.checkbox_1 = ctk.CTkCheckBox(master=widget_frame)
        self.checkbox_1.grid(row=grid_row, padx=5, pady=pad_y)
        grid_row += 1

        self.radiobutton_var = tk.IntVar(value=1)

        self.radiobutton_1 = ctk.CTkRadioButton(master=widget_frame, variable=self.radiobutton_var, value=1)
        self.radiobutton_1.grid(row=grid_row, padx=5, pady=pad_y)
        grid_row += 1

        self.radiobutton_2 = ctk.CTkRadioButton(master=widget_frame, variable=self.radiobutton_var, value=2)
        self.radiobutton_2.grid(row=grid_row, padx=5, pady=pad_y)
        grid_row += 1

        self.switch_1 = ctk.CTkSwitch(master=widget_frame)
        self.switch_1.grid(row=grid_row, padx=5, pady=pad_y)
        grid_row += 1

    def _toggle_palette_display(self):
        show_palette = self._swt_show_palette.get()
        # self.preview.attributes('-zoomed', False)
        if show_palette:
            self.palette_frame.grid(row=1, column=0, padx=2, pady=5, sticky='nsw')
            # self.preview.geometry(f'{950}x{800}-100+100')
            self.preview.geometry(f'{PreviewPanel.expanded_width}x{PreviewPanel.initial_height}')
        else:
            self.palette_frame.grid_remove()
            self.preview.geometry(f'{PreviewPanel.initial_width}x{PreviewPanel.initial_height}')
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

    def copy_colour_code(self, code):
        pyperclip.copy(code)
        self._status_bar.set_status_text(status_text_life=10, status_text=f'Colour, {code}, copied to clipboard.')
        # Whilst we arte here - save the current geometry:
        self._save_preview_geometry()

    def block_closing(self, event=0):
        pass

    def _restore_preview_geometry(self):
        geometry_ini = self._app_home / 'preview_panel.ini'
        try:
            # if the file is there
            # get geometry from file
            ini_file = open(geometry_ini, 'r')
            self.preview.geometry(ini_file.read())
            ini_file.close()

        except FileNotFoundError:
            # if the file is not there, create the file and use default
            # then use default geometry.
            open(geometry_ini, 'w')
            ini_file = open(geometry_ini, 'w')
            ini_file.close()
            self.preview.geometry(f'{PreviewPanel.initial_width}x{PreviewPanel.initial_height}+900+100')

    def _save_preview_geometry(self):
        # save current geometry to the ini file
        geometry_ini = self._app_home / 'preview_panel.ini'
        geometry = self.preview.geometry()
        with open(geometry_ini, 'w') as ini_file:
            ini_file.write(geometry)
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
        launch_preview_panel(appearance_mode=appearance_mode, theme=theme)
    else:
        controller = ControlPanel()

