import os
import tkinter as tk
# from tkinter.tix import *
# import tkinter.messagebox
import customtkinter
from PIL import ImageTk, Image
import openai
import argparse
from argparse import HelpFormatter
import pyperclip
import sys
from operator import attrgetter
from configparser import ConfigParser, ExtendedInterpolation
import textwrap
from os.path import exists
import multiprocessing
import shutil
import re
from pathlib import Path

DEBUG = False
# Initialise primary constants
prog = os.path.basename(__file__)

headings_font_size = -14
status_bar_font_size = -12

platform = sys.platform
if platform == "win32":
    platform = "Windows"
elif platform == "darwin":
    platform = "MacOS"
else:
    platform = "Linux"

if platform == "Windows":
    home_dir = os.getenv("UserProfile")
else:
    home_dir = os.getenv("HOME")
home_dir = Path(home_dir)

def copy_config_section(config_file, source_section, target_section):
    config = ConfigParser()
    config.read(config_file)
    config.add_section(target_section)
    for key, value in config.items(source_section):
        config.set(target_section, key, value)
    with open(config_file, 'w') as f:
        config.write(f)


class MessageBox():
    def __init__(self, message, dimension):
        self.__win_message = customtkinter.CTkToplevel()
        self.__win_message.geometry(dimension)
        self.__win_message.grid_columnconfigure(0, weight=3)
        self.__win_message.grid_columnconfigure(0, weight=1)

    def ok(self):
        self.__win_message.destroy()
        return 0

    @classmethod
    def showwarning(cls, title, message):
        box_width = len(message) + 20
        label_width = int(len(message) + 10)
        #                                        W      x      H
        message_box = MessageBox(message, f'{box_width}' + "x" + "75")

        lbl_message = customtkinter.CTkLabel(master=message_box.__win_message,
                                             text=message)
        #
        lbl_message.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        ok = customtkinter.CTkButton(master=message_box.__win_message,
                                     text="OK",
                                     border_width=2,
                                     fg_color=None,
                                     command=message_box.ok())

        ok.grid(row=2, column=0, pady=10, padx=20, sticky="nsew")
        message_box.__frm_message.wait_visibility()
        message_box.__frm_message.grab_set()


def transfer_config_section(source_file, target_file, section_name):
    """
    Transfer a section from a source config file to a target config file.

    NOTE: This function was partly written using Albert!

    :param source_file: The pathname to the source config file.
    :param target_file: The pathname to the target config file.
    :param section_name: The name of the section to copy.
    """
    source_config = ConfigParser()
    target_config = ConfigParser()
    source_config.read(source_file)
    section = source_config[section_name]
    # config.remove_section(section_name)
    target_config.add_section(section_name)
    for key, value in section.items():
        target_config.set(section_name, key, value)
    with open(target_file, 'w') as f:
        target_config.write(f)


class SortingHelpFormatter(HelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


ap = argparse.ArgumentParser(formatter_class=SortingHelpFormatter
                             , description=f"{prog}: Welcome to Albert, the digital assistant based on GPT-3. "
                                           f"Albert requires an Open AI GPT-3 key. This must be placed into the"
                                           " albert.ini file, under the 'global' section, with a property name."
                                           " of openai_api_key.")
ap.add_argument("-a", '--set-appearance', required=False, action="store", help="Overrides the default appearance "
                                                                               "(dark). Valid options are: 'dark', 'light', "
                                                                               "and 'system'. System only has any effect on"
                                                                               "MacOS.",
                dest='APPEARANCE_MODE', default='dark')

ap.add_argument("-m", '--start-mode', required=False, action="store", help="Override the starting prompt mode. "
                                                                           "You can switch to a different mode option, "
                                                                           "via  'Settings' inside the application. "
                                                                           "This overrides the application's default.",
                default='General Knowledge',
                dest='start_mode')
ap.add_argument("-t", '--set-theme', required=False, action="store", help="Overrides the default appearance "
                                                                          "(green). Valid options are: 'green', "
                                                                          " 'blue',and 'dark-blue'.",
                dest='THEME', default='green')

ap.add_argument("-H", '--albert-home', required=False, default=home_dir / 'albert',
                action="store",
                help=f"The pathname to the initialisation file. The default location is {home_dir}/albert.ini.",
                dest='albert_home')

args_list = vars(ap.parse_args())
start_mode = args_list["start_mode"]
albert_home = Path(args_list["albert_home"])
if not exists(albert_home):
    print(f'Unable to find home directory for the application: {albert_home}')
    exit(1)
app_images = albert_home / 'images'
app_configs = albert_home / 'config'
prompt_files = albert_home / 'prompt_files'
config_ini = app_configs / 'albert.ini'
APPEARANCE_MODE = args_list["APPEARANCE_MODE"]
THEME = args_list["THEME"]

if APPEARANCE_MODE not in ['dark', 'light', 'system']:
    print(f"Error: Invalid appearance setting, '{APPEARANCE_MODE}', valid options are  'dark', 'light' or 'system'.")
    print('Bailing out!')
    exit(1)

if THEME not in ['green', 'blue', 'dark-blue']:
    print(f"Error: Invalid theme setting, '{APPEARANCE_MODE}', valid options are  'green', 'blue', or 'dark-blue'.")
    print('Bailing out!')
    exit(1)

tooltip_bg_colour_dict = {"green": "#72CF9F",
                          "blue": "#3B8ED0",
                          "dark-blue": "#608BD5"}
TOOLTIP_BG_COLOUR = tooltip_bg_colour_dict[THEME]

widget_bg_colour_dict = {"dark": "#3D3D3D",
                         "light": "#FFFFFF",
                         "system": "#FFFFFF"}
WIDGET_BG_COLOUR = widget_bg_colour_dict[APPEARANCE_MODE]

widget_fg_colour_dict = {"dark": "#E1E2DF",
                         "light": "#3B3640",
                         "system": "#3B3640"}

WIDGET_FG_COLOUR = widget_fg_colour_dict[APPEARANCE_MODE]

regions_fg_colour_dict = {"dark": "#E1E2DF",
                          "light": "#3B3640",
                          "system": "#3B3640"}

BG_REGIONS = regions_fg_colour_dict[APPEARANCE_MODE]

frame_colour_dict = {"dark": "#2E2E2E",
                     "light": "#DEDEDE",
                     "system": "#DEDEDE"}

FRAME_COLOUR = frame_colour_dict[APPEARANCE_MODE]

base_colour_dict = {"dark": "#1F1F1F",
                    "light": "#DEDEDE",
                    "system": "#DEDEDE"}
BASE_COLOUR = frame_colour_dict[APPEARANCE_MODE]


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


class AlbertConfig:
    """Class to control our primary Einstein application config."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        self.refresh_config()

    def copy_config_section(self, source_section, target_section):
        self.config.add_section(target_section)
        for key, value in self.config.items(source_section):
            self.config.set(target_section, key, value)
        with open(self.config_path, 'w') as f:
            self.config.write(f)

    def resolve_config_option(self, this_section: str, this_option: str):
        # print(f'This section : {this_section}; This option: {this_option}')
        # If we are being specific about one of the higher level sections we are more stringent.
        if this_section == 'global':
            property_val = self.config[this_section][this_option]

        if this_section == 'default':
            property_val = self.config[this_section][this_option]

        # Here we look for specific mode entries and if they don't exist, we search the
        # higher level sections for a property value
        if self.config.has_option(this_section, this_option):
            property_val = self.config[this_section][this_option]
        elif self.config.has_option("skill_defaults", this_option):
            property_val = self.config["skill_defaults"][this_option]
        else:
            property_val = self.config["global"][this_option]

        if this_option in ['gpt_temperature', 'max_tokens']:
            return float(property_val)
        else:
            return property_val

    def has_section(self, check_section):
        return self.config.has_section(check_section)

    def modes_list(self):
        section_list = []
        for list_section in self.config.sections():
            if list_section in ['global', 'skill_defaults', 'config_data_types']:
                continue
            else:
                section_list.append(list_section)
        return section_list

    def config_sections(self, section: str):
        """The config_sections method, optionally accepts a section for our configparser file and prints the
        properties of the section. If no section is supplied, it lists the sections. This is a debug method."""
        if section:
            print(f'Section dump for: {section}')
            print(dict(self.config.items(section)))
            print('Keys:')
            for key in self.config[section]: print(key)
        else:
            sections = self.config.sections()
            print(f'Init File: {self.config_path}')
            print(f'Sections: {sections}')

    def update_property(self, config_section, config_property, property_value):
        self.config.set(config_section, config_property, property_value)
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

    def refresh_config(self):
        if exists(self.config_path):
            self.config.read(self.config_path)
        else:
            print(f'Cannot open config file: {self.config_path}')
            raise FileNotFoundError

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """

    def __init__(self, widget, text='widget info', bg_colour='#777777'):
        self._bg_colour = bg_colour
        self.waittime = 400  # miliseconds
        self.wraplength = 300  # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 40
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background=self._bg_colour, relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


customtkinter.set_appearance_mode(APPEARANCE_MODE)  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme(THEME)  # Themes: "blue" (standard), "green", "dark-blue"


class SliderWidget:
    def __init__(self, master: customtkinter.CTkToplevel,
                 label_text: str,
                 row: int,
                 column: int,
                 from_: int,
                 to: int,
                 number_of_steps: int,
                 initial_value: float,
                 value_format: str,
                 command,
                 tooltip: str,
                 text_indent: int = 0):
        assert to > from_
        self._format_mask = value_format
        self._command = command

        self._label_text = customtkinter.CTkLabel(master=master, text=" " * text_indent + label_text)
        self._label_text.grid(row=row, column=column, pady=0, padx=0, sticky="e")

        self._render_slider = customtkinter.CTkSlider(master=master,
                                                      from_=from_,
                                                      to=to,
                                                      number_of_steps=number_of_steps,
                                                      command=self.set_value_display)

        self._render_slider.grid(row=row, column=column + 1, columnspan=1, pady=10, padx=0, sticky="w")

        self._render_slider_value = customtkinter.CTkLabel(master=master,
                                                           text=value_format.format(initial_value))

        if tooltip:
            self.widget_tip = CreateToolTip(self._render_slider, tooltip, TOOLTIP_BG_COLOUR)

        self._render_slider_value.grid(row=row, column=column + 2, pady=0, padx=0, sticky="w")
        self._render_slider.set(initial_value)

    def set_value_display(self, value):
        self._render_slider_value.configure(text=self._format_mask.format(value))
        self._command(value)


class App(customtkinter.CTk):

    def __init__(self, default_mode):

        super().__init__()

        self._albert_config = AlbertConfig(config_ini)
        self._slider_widgets = {}

        self._prompt_mode = default_mode
        self._display_fields_width = 120
        # The prompt_mode defines which GTP
        # prompt to work with
        self._prompt_mode = default_mode
        self.locked_skills = self._albert_config.resolve_config_option(default_mode, "locked_skills")
        self._gpt_engine = self._albert_config.resolve_config_option(default_mode, "gpt_engine")
        self._frequency_penalty = self._new_frequency_penalty \
            = float(self._albert_config.resolve_config_option(default_mode, "frequency_penalty"))
        self._gpt_temperature = self._new_gpt_temperature = float(
            self._albert_config.resolve_config_option(default_mode,
                                                      "gpt_temperature"))
        self._max_tokens = self._new_max_tokens = int(
            self._albert_config.resolve_config_option(default_mode, "max_tokens"))
        self._presence_penalty = self._new_presence_penalty = float(
            self._albert_config.resolve_config_option(default_mode,
                                                      "presence_penalty"))
        self._top_p = self._new_top_p = float(self._albert_config.resolve_config_option(default_mode,
                                                                                        "top_p"))
        self._best_of = self._new_best_of = float(self._albert_config.resolve_config_option(default_mode,
                                                                                            "best_of"))
        self._text_to_speech = self._new_text_to_speech = self._albert_config.resolve_config_option(default_mode,
                                                                                                    "text_to_speech")
        self._stop = self._albert_config.resolve_config_option(default_mode, "stop")
        self._text_to_speech_cmd = self._albert_config.resolve_config_option(default_mode, "text_to_speech_cmd")
        self._q_prompt = self._albert_config.resolve_config_option(mode, "q_prompt")
        self._a_prompt = self._albert_config.resolve_config_option(mode, "a_prompt")
        self._result = ''
        self._prompt_file = self._albert_config.resolve_config_option(default_mode, "prompt_file")
        prompt_file = Path(f"{self._prompt_file}")

        with open(prompt_file, 'r') as file:
            if exists(prompt_file):
                self._prompt = file.read()
            else:
                print(f'Cannot locate prompt file: {prompt_file}')
                exit(1)

        self._skill_info_file = self._albert_config.resolve_config_option(default_mode, "skill_info_file")
        skill_info_file = Path(f"{self._skill_info_file}")
        # See if the prompt file is accompanied by an info file.
        if exists(skill_info_file):
            with open(skill_info_file, 'r') as file:
                self._prompt_nfo = file.read()
                self._prompt_nfo = wrap_string(self._prompt_nfo, self._display_fields_width - 10)

        self.openai_api_key = self._albert_config.resolve_config_option("global", "openai_api_key")
        openai.api_key = self.openai_api_key

        self._app_width = 1000
        self._app_height = 600
        self.title("Albert")
        self.geometry(f"{self._app_width}x{self._app_height}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # Configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ============ Left frame ====================
        self.frm_left = customtkinter.CTkFrame(master=self, borderwidth=0)
        self.frm_left.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        self.frm_right = customtkinter.CTkFrame(master=self,
                                                width=180,
                                                corner_radius=0)
        self.frm_right.grid(row=0, column=2, sticky="nswe")

        # configure grid layout (3x7)
        self.frm_left.rowconfigure((0, 1, 2, 3), weight=1)
        self.frm_left.rowconfigure(7, weight=10)
        self.frm_left.columnconfigure((0, 1), weight=1)
        self.frm_left.columnconfigure(2, weight=0)

        self.widget_mode_info = customtkinter.CTkLabel(self.frm_left,
                                                       text=self._prompt_nfo,
                                                       width=self._display_fields_width, height=10)
        self.widget_mode_info.grid(row=0, column=0, padx=15, pady=2, sticky="ew")

        self.question = customtkinter.CTkEntry(master=self.frm_left,
                                               width=self._display_fields_width,
                                               height=30,
                                               corner_radius=3,
                                               placeholder_text="Enter your request")
        self.question.grid(row=2, column=0, columnspan=2, pady=0, padx=10, sticky="ew")

        self.answer = tk.Text(master=self.frm_left,
                              relief='flat',
                              bg=WIDGET_BG_COLOUR,
                              fg=WIDGET_FG_COLOUR,
                              wrap=tk.WORD,
                              borderwidth=0,
                              bd=0,
                              height=25,
                              width=90)

        scroll_bar = tk.Scrollbar(self, command=self.answer.yview)
        scroll_bar.grid(row=0, column=1, sticky='e')

        self.answer.config(state=tk.DISABLED)
        self.answer.grid(row=3, column=0, sticky="nwe", padx=10, pady=10)

        # ============ Right Frame ============
        # configure grid layout (1x11)
        self.frm_right.grid_rowconfigure(0, minsize=10)  # empty row with minsize as spacing
        self.frm_right.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frm_right.grid_rowconfigure(8, minsize=20)  # empty row with minsize as spacing
        self.frm_right.grid_rowconfigure(10, minsize=20)  # empty row with minsize as spacing
        self.frm_right.grid_rowconfigure(14, minsize=10)  # empty row with minsize as spacing

        self.submit = customtkinter.CTkButton(master=self.frm_right,
                                              text="Submit",
                                              border_width=2,
                                              fg_color=None,
                                              command=self.submit)
        self.submit.grid(row=2, column=0, pady=10, padx=20)

        tooltip = 'Copy answer text to clipboard.'
        self.copy = customtkinter.CTkButton(master=self.frm_right,
                                            text="Copy",
                                            border_width=2,
                                            fg_color=None,
                                            command=self.copy)
        self.copy.grid(row=3, column=0, pady=10, padx=20)
        self.copy_tooltip = CreateToolTip(self.copy, tooltip, TOOLTIP_BG_COLOUR)

        self.clear = customtkinter.CTkButton(master=self.frm_right,
                                             text="Clear",
                                             border_width=2,
                                             fg_color=None,
                                             command=self.clear)
        self.clear.grid(row=4, column=0, pady=10, padx=20)

        switch_var = tk.StringVar()
        switch_var.set(self._text_to_speech)

        self.switch_text_to_speech = customtkinter.CTkSwitch(master=self.frm_right,
                                                             onvalue='yes',
                                                             offvalue='no',
                                                             command=self.set_text_to_speech,
                                                             text="Text to Speech")

        self.switch_text_to_speech.grid(row=8, column=0, columnspan=2, pady=25, padx=0, sticky="n")

        if self._text_to_speech == 'yes':
            self.switch_text_to_speech.select()
        else:
            self.switch_text_to_speech.deselect()

        self.text_to_speech_tip = CreateToolTip(self.switch_text_to_speech,
                                                "Controls text to speech. When switched to on, in addition to the  "
                                                "response being displayed, Albert also relays the test, to be "
                                                "processed via text-to-speech. This option requires that you have"
                                                " Festival text-to-speech installed.",
                                                TOOLTIP_BG_COLOUR)

        self.label_mode = customtkinter.CTkLabel(master=self.frm_right,
                                                 text="Skill (GPT prompt)",
                                                 justify="left",
                                                 text_font=("Roboto Medium", headings_font_size))

        self.label_mode.grid(row=9, column=0, pady=0, padx=0, sticky="n")

        modes_list = self._albert_config.modes_list()

        self.combo_mode = customtkinter.CTkOptionMenu(master=self.frm_right,
                                                      values=modes_list,
                                                      command=self.set_prompt_mode)
        self.combo_mode.grid(row=10, column=0, pady=0, padx=0, sticky="n")
        self.combo_mode.set(self._prompt_mode)

        self.label_filler = customtkinter.CTkLabel(master=self.frm_right,
                                                   text="",
                                                   justify="left")

        self.label_filler.grid(row=11, column=0, pady=0, padx=0, sticky="n")

        self.settings = customtkinter.CTkButton(master=self.frm_right,
                                                text="Settings",
                                                border_width=2,
                                                fg_color=None,
                                                command=self.launch_settings)

        self.settings.grid(row=14, column=0, pady=15, padx=20, sticky="s")

        self.quit = customtkinter.CTkButton(master=self.frm_right,
                                            text="Quit",
                                            border_width=2,
                                            fg_color=None,
                                            command=self.on_closing)
        self.quit.grid(row=15, column=0, pady=15, padx=5, sticky="s")

        self.avatar_image = app_images / 'albert_einstein_lol.gif'

        self.avatar = Image.open(self.avatar_image)
        self.avatar = self.avatar.resize((130, 130))
        self.einstein = tk.PhotoImage(file=self.avatar_image)
        self.avatar = ImageTk.PhotoImage(self.avatar)

        self.label_avatar = customtkinter.CTkLabel(self.frm_right, image=self.avatar, width=50, height=50)
        self.label_avatar.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        if not self.openai_api_key:
            dialog = customtkinter.CTkInputDialog(master=None, text="Enter OpenAI API Key:", title="Test")
            self.openai_api_key = dialog.get_input()

    def get_openai_api_key(self):
        dialog = customtkinter.CTkInputDialog(master=None, text="Enter OpenAI API Key:", title="OpenAI Key")
        new_key = dialog.get_input()
        if new_key:
            self.openai_api_key = new_key
            self._albert_config.update_property('global', 'openai_api_key', self.openai_api_key)

    def ask_gpt(self, my_question):
        prompt = self._prompt
        prompt = prompt + self._stop + self._q_prompt + ' ' + my_question + self._stop + self._a_prompt + ' '
        if DEBUG:
            print('=' * 100)
            print(f'PROMPT: {self._prompt}')
        # print('Prompt: ', prompt)
        gpt_response = openai.Completion.create(
            # engine="davinci-instruct-beta-v3",
            engine=self._gpt_engine,
            prompt=prompt,
            temperature=float(self._gpt_temperature),
            max_tokens=int(self._max_tokens),
            top_p=float(self._top_p),
            frequency_penalty=float(self._frequency_penalty),
            presence_penalty=float(self._presence_penalty),
            stop=self._stop
        )
        if DEBUG:
            print(f'      prompt_mode: {self._prompt_mode}')
            print(f'           engine: {self._gpt_engine}')
            print(f'  gpt_temperature: {self._gpt_temperature}')
            print(f'       max_tokens: {self._max_tokens}')
            print(f'            top_p: {self._top_p}')
            print(f'frequency_penalty: {self._frequency_penalty}')
            print(f' presence_penalty: {self._presence_penalty}')
            print(f'             stop: {self._stop}')
            print(f'           prompt: <<<{prompt}>>>')

        # print ('Response: ', gpt_response)
        return gpt_response

    def launch_copy_skill(self):
        self.win_settings.withdraw()
        self.win_skill_copy = customtkinter.CTkToplevel()
        height = 130
        width = 400
        self.win_skill_copy.geometry(f"{width}x{height}")
        self.win_skill_copy.minsize(width, height)
        self.win_skill_copy.maxsize(width, height)

        self.win_skill_copy.grid_columnconfigure(0, weight=3)
        self.win_skill_copy.grid_columnconfigure(0, weight=1)

        self.frm_skill_fields = customtkinter.CTkFrame(master=self.win_skill_copy, borderwidth=0)
        self.frm_skill_fields.grid(row=0, column=0, columnspan=1, padx=5, pady=1, sticky="nsw")

        self.frm_skill_buttons = customtkinter.CTkFrame(master=self.win_skill_copy, borderwidth=0, corner_radius=0)
        self.frm_skill_buttons.grid(row=0, column=1, columnspan=1, padx=5, pady=1, sticky="nsw")

        self.frm_status_bar = customtkinter.CTkFrame(master=self.win_skill_copy, borderwidth=0, corner_radius=0)
        self.frm_status_bar.grid(row=1, column=0, columnspan=2, padx=0, pady=0, sticky="w")

        val_copy_to_skill = self.win_skill_copy.register(self.validate_copy_to_skill)
        val_copy_to_prompt = self.win_skill_copy.register(self.validate_copy_to_prompt)

        self.ent_skill_copy_to_skill = customtkinter.CTkEntry(master=self.frm_skill_fields,
                                                              width=200,
                                                              height=30,
                                                              corner_radius=3,
                                                              placeholder_text="New skill name")
        self.ent_skill_copy_to_skill.grid(row=0, column=0, columnspan=1, pady=10, padx=10, sticky="nsw")
        self.ent_skill_copy_to_skill.config(validate="focusout", validatecommand=(val_copy_to_skill, '%P'))

        self.ent_skill_copy_to_prompt = customtkinter.CTkEntry(master=self.frm_skill_fields,
                                                               width=150,
                                                               height=30,
                                                               corner_radius=3,
                                                               placeholder_text="Prompt file prefix")
        self.ent_skill_copy_to_prompt.grid(row=1, column=0, columnspan=1, pady=10, padx=10, sticky="nsw")
        self.ent_skill_copy_to_prompt.config(validate="key", validatecommand=(val_copy_to_prompt, '%P'))

        self.btn_skill_cancel_settings = customtkinter.CTkButton(master=self.frm_skill_buttons,
                                                                 text="Cancel",
                                                                 border_width=2,
                                                                 fg_color=None,
                                                                 command=self.quit_skill_copy)
        self.btn_skill_cancel_settings.grid(row=1, column=0, pady=15, padx=10, sticky="nsew")

        self.btn_skill_save_settings = customtkinter.CTkButton(master=self.frm_skill_buttons,
                                                               text="Save",
                                                               border_width=2,
                                                               fg_color=None,
                                                               command=self.submit_config_copy)
        self.btn_skill_save_settings.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        self.lbl_status_bar = customtkinter.CTkLabel(master=self.frm_status_bar,
                                                     text=f"Enter a new skill name followed by the associated prompt "
                                                          f"file prefix.",
                                                     anchor="w",
                                                     justify="left",
                                                     height=5,
                                                     width=160,
                                                     text_font=("Roboto Medium", status_bar_font_size))

        # self.lbl_status_bar.pack()
        self.lbl_status_bar.grid(row=3, column=0, pady=1, padx=0, columnspan=1, sticky="w")
        # self.lbl_status_bar.place(relx=0.22, rely=0.05, anchor="e")
        self.lbl_status_pad = customtkinter.CTkLabel(master=self.frm_status_bar,
                                                     text="",
                                                     anchor="e",
                                                     justify="right",
                                                     height=5,
                                                     text_font=("Roboto Medium", status_bar_font_size))
        self.lbl_status_pad.grid(row=3, column=1, pady=1, padx=0, columnspan=1, sticky="e")
        self.ent_skill_copy_to_skill.focus_set()
        self.win_skill_copy.wait_visibility()
        self.win_skill_copy.grab_set()

    def quit_skill_copy(self):
        self.win_skill_copy.destroy()
        self.win_settings.deiconify()

    def launch_settings(self):

        self.win_settings = customtkinter.CTkToplevel()
        #                        W      x      H
        self.win_settings.geometry("670" + "x" + "340")
        self.win_settings.minsize(670, 340)
        self.win_settings.maxsize(670, 340)

        self.win_settings.grid_columnconfigure(0, weight=3)
        self.win_settings.grid_columnconfigure(0, weight=1)

        self.frm_settings_top = customtkinter.CTkFrame(master=self.win_settings, borderwidth=0)
        self.frm_settings_top.grid(row=0, column=0, columnspan=1, sticky="nsew", padx=5, pady=5)

        self.frm_settings_left = customtkinter.CTkFrame(master=self.win_settings, borderwidth=0)
        self.frm_settings_left.grid(row=1, column=0, columnspan=1, sticky="nsew", padx=5, pady=5)

        self.frm_settings_right = customtkinter.CTkFrame(master=self.win_settings, borderwidth=0, corner_radius=0)
        self.frm_settings_right.grid(row=0, column=1, rowspan=3, sticky="nsew")

        self.frm_settings_bottom = customtkinter.CTkFrame(master=self.win_settings, borderwidth=0, corner_radius=0)
        self.frm_settings_bottom.grid(row=2, column=0, columnspan=1, sticky="nsew", padx=5, pady=5)

        self.win_settings.wait_visibility()
        self.win_settings.grab_set()
        self.win_settings.title("Albert's Settings")

        self.win_settings.iconbitmap(bitmap="@" + str(icon_file))

        self.label_gpt_settings = customtkinter.CTkLabel(master=self.frm_settings_top,
                                                         text=f"GPT Settings for  {self._prompt_mode}",
                                                         fg_="green",
                                                         justify="center",
                                                         text_font=("Roboto Medium", headings_font_size))

        self.label_gpt_settings.grid(row=0, column=0, pady=10, padx=150, sticky="ew")

        tooltip = "Controls randomness: Lowering results in less random completions. As " \
                  "the temperature approached zero, the model will become more " \
                  "deterministic and repetitive."
        self._temperature_slider = SliderWidget(master=self.frm_settings_left,
                                                label_text='Temperature',
                                                row=3,
                                                column=0,
                                                from_=0,
                                                to=1,
                                                number_of_steps=100,
                                                initial_value=self._gpt_temperature,
                                                value_format="{:.3f}",
                                                command=self.set_temperature,
                                                tooltip=tooltip,
                                                text_indent=20)

        tooltip = "The maximum number of tokens to generate. Requests can use up to 2,048 or " \
                  "4,000 tokens, shared between prompt and completion. The exact limit varies by " \
                  "model. (One token is roughly 4 characters of English text)"

        self._max_tokens_slider = SliderWidget(master=self.frm_settings_left,
                                               label_text='Max Length (Tokens)',
                                               row=4,
                                               column=0,
                                               from_=1,
                                               to=4000,
                                               number_of_steps=100,
                                               initial_value=self._max_tokens,
                                               value_format="{:.0f}",
                                               command=self.set_max_tokens,
                                               tooltip=tooltip,
                                               text_indent=10)

        tooltip = "Controls diversity via nucleus sampling: " \
                  "0.5 means half of all likelihood - weighted options are considered."
        self._top_p_slider = SliderWidget(master=self.frm_settings_left,
                                          label_text='Top P',
                                          row=5,
                                          column=0,
                                          from_=0,
                                          to=1,
                                          number_of_steps=100,
                                          initial_value=self._top_p,
                                          value_format="{:.3f}",
                                          command=self.set_top_p,
                                          tooltip=tooltip,
                                          text_indent=30)

        tooltip = "How much to penalise new tokens based on their existing frequency " \
                  "in the text so far. Decreases the model's likelihood to repeat the " \
                  "same line verbatim."

        self._frequency_slider = SliderWidget(master=self.frm_settings_left,
                                              label_text='Frequency penalty',
                                              row=9,
                                              column=0,
                                              from_=0,
                                              to=2,
                                              number_of_steps=100,
                                              initial_value=self._frequency_penalty,
                                              value_format="{:.3f}",
                                              command=self.set_frequency_penalty,
                                              tooltip=tooltip,
                                              text_indent=10)

        tooltip = "How much to penalise new tokens depending on whether they appear " \
                  "in the text so far. Increase the model's likelihood to talk about " \
                  "new topics."

        self._presence_slider = SliderWidget(master=self.frm_settings_left,
                                             label_text='Presence penalty',
                                             row=11,
                                             column=0,
                                             from_=0,
                                             to=2,
                                             number_of_steps=100,
                                             initial_value=self._presence_penalty,
                                             value_format="{:.3f}",
                                             command=self.set_presence_penalty,
                                             tooltip=tooltip,
                                             text_indent=10)

        tooltip = "USE WITH CAUTION!\nGenerates multiple completions server-side, and displays only the " \
                  "best. Streaming only works when set to 1. Since it acts as a  " \
                  "multiplier on the number of completions, this parameter can eat " \
                  "into your token quota very quickly."

        self._presence_slider = SliderWidget(master=self.frm_settings_left,
                                             label_text='Best of',
                                             row=12,
                                             column=0,
                                             from_=1,
                                             to=20,
                                             number_of_steps=20,
                                             initial_value=self._best_of,
                                             value_format="{:.0f}",
                                             command=self.set_best_of,
                                             tooltip=tooltip,
                                             text_indent=30)
        self.btn_edit_skill = customtkinter.CTkButton(master=self.frm_settings_right,
                                                      text="Edit Skill",
                                                      border_width=2,
                                                      fg_color=None,
                                                      command=self.save_settings)
        self.btn_edit_skill.grid(row=0, column=0, pady=10, padx=10)

        if self._prompt_mode in self.locked_skills:
            self.btn_edit_skill.configure(state=tk.DISABLED)

        self.btn_copy_skill = customtkinter.CTkButton(master=self.frm_settings_right,
                                                      text="Copy Skill",
                                                      border_width=2,
                                                      fg_color=None,
                                                      command=self.launch_copy_skill)
        self.btn_copy_skill.grid(row=1, column=0, pady=10, padx=10)

        if self.openai_api_key:
            self.btn_api_key = customtkinter.CTkButton(self.frm_settings_right, text="Update OpenAI key",
                                                       border_width=2,
                                                       fg_color=None,
                                                       command=self.get_openai_api_key)
        else:
            self.btn_api_key = customtkinter.CTkButton(self.frm_settings_right, text="Set OpenAI key",
                                                       border_width=2,
                                                       command=self.get_openai_api_key)
        self.btn_api_key.grid(row=3, column=0, pady=10, padx=10)
        # self.btn_api_key.place(relx=0.5, rely=.908, anchor=tkinter.CENTER)

        self.btn_cancel_settings = customtkinter.CTkButton(master=self.frm_settings_bottom,
                                                           text="Cancel",
                                                           border_width=2,
                                                           fg_color=None,
                                                           command=self.win_settings.destroy)
        self.btn_cancel_settings.grid(row=28, column=0, pady=10, padx=50)

        self.btn_save_settings = customtkinter.CTkButton(master=self.frm_settings_bottom,
                                                         text="Save",
                                                         border_width=2,
                                                         fg_color=None,
                                                         command=self.save_settings)
        self.btn_save_settings.grid(row=28, column=2, pady=10, padx=50)

    def get_defaults(self, new_prompt_mode):
        """ Retrieves and sets the settings for the supplied prompt mode.

        :param new_prompt_mode:
        """
        self._gpt_engine = self._albert_config.resolve_config_option(new_prompt_mode, "gpt_engine")
        self._gpt_temperature = self._albert_config.resolve_config_option(new_prompt_mode, "gpt_temperature")
        self._max_tokens = self._albert_config.resolve_config_option(new_prompt_mode, "max_tokens")
        self._prompt_file = self._albert_config.resolve_config_option(new_prompt_mode, "prompt_file")
        self._skill_info_file = self._albert_config.resolve_config_option(new_prompt_mode, "skill_info_file")
        self._stop = self._albert_config.resolve_config_option(new_prompt_mode, "stop")
        self._text_to_speech_cmd = self._albert_config.resolve_config_option(new_prompt_mode, "text_to_speech_cmd")
        with open(self._prompt_file, 'r') as file:
            self._prompt = file.read()

        # See if the prompt file is accompanied by an info file.
        if exists(self._skill_info_file):
            with open(self._skill_info_file, 'r') as file:
                self._prompt_nfo = file.read()
                self._prompt_nfo = wrap_string(self._prompt_nfo, self._display_fields_width - 10)
        else:
            self._prompt_nfo = ''

    def clear(self):
        """ Clears out the contents of the question and answer entry widgets,
        """
        self.question.delete(0, tk.END)
        self.answer.config(state=tk.NORMAL)
        self.answer.delete(0.0, tk.END)
        self.answer.config(state=tk.DISABLED)
        self._result = ''

    def on_closing(self, event=0):
        self.destroy()

    def copy(self):
        pyperclip.copy(self._result)

    @staticmethod
    def change_appearance_mode(new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    @staticmethod
    def change_color_mode(new_colour_mode):
        customtkinter.set_default_color_theme("blue")

    def set_temperature(self, new_temperature):
        """Updates the self._new_temperature. This property is only promoted when the save_settings mode is
        called. """
        self._new_gpt_temperature = new_temperature
        # print (f"Temperature set to: {self.temperature}")

    def set_max_tokens(self, new_max_tokens):
        """Updates the self._new_max_tokens. This property is only promoted when the save_settings mode is
        called. """
        self._new_max_tokens = new_max_tokens

    def set_frequency_penalty(self, new_frequency_penalty):
        """Updates the self._new_frequency_penalty. This property is only promoted when the save_settings mode is
        called. """
        self._new_frequency_penalty = new_frequency_penalty

    def set_presence_penalty(self, new_presence_penalty):
        """Updates the self._new_presence_penalty. This property is only promoted when the save_settings mode is
        called. """
        self._new_presence_penalty = new_presence_penalty

    def set_top_p(self, new_top_p):
        """Updates the self._new_top_p. This property is only promoted when the save_settings mode is
        called. """
        self._new_top_p = new_top_p
        # print('New top = ' + str(self._new_top_p))

    def set_best_of(self, new_best_of):
        """Updates the self._new_best_of property. This property is only promoted when the save_settings mode is
        called. """
        self._new_best_of = new_best_of

    def set_prompt_mode(self, choice: str):
        """Sets all related settings associated with a newly selected prompt mode (personality).
        :param choice:
        """
        choice = choice
        self._prompt_mode = choice
        self._gpt_engine = self._albert_config.resolve_config_option(choice, "gpt_engine")
        self._frequency_penalty = float(self._albert_config.resolve_config_option(choice, "frequency_penalty"))
        self._gpt_temperature = float(self._albert_config.resolve_config_option(choice, "gpt_temperature"))
        self._max_tokens = int(self._albert_config.resolve_config_option(choice, "max_tokens"))
        self._presence_penalty = float(self._albert_config.resolve_config_option(choice, "presence_penalty"))
        self._top_p = float(self._albert_config.resolve_config_option(choice, "top_p"))
        self._best_of = float(self._albert_config.resolve_config_option(choice, "best_of"))
        self._text_to_speech = self._albert_config.resolve_config_option(choice, "text_to_speech")
        self._stop = self._albert_config.resolve_config_option(choice, "stop")
        self._text_to_speech_cmd = self._albert_config.resolve_config_option(choice, "text_to_speech_cmd")
        self._q_prompt = self._albert_config.resolve_config_option(choice, "q_prompt")
        self._a_prompt = self._albert_config.resolve_config_option(choice, "a_prompt")
        self._app_prompt_files = self._albert_config.resolve_config_option('global', 'app_prompt_files')
        self._prompt_file = self._albert_config.resolve_config_option(choice, "prompt_file")
        with open(Path(self._prompt_file), 'r') as file:
            self._prompt = file.read()
        if DEBUG:
            print(f'Mode updated: {self._prompt_mode}')
        # See if the prompt file is accompanied by an info file.
        if exists(self._prompt_file + '.nfo'):
            with open(self._prompt_file + '.nfo', 'r') as file:
                self._prompt_nfo = file.read()
                self._prompt_nfo = wrap_string(self._prompt_nfo, self._display_fields_width - 10)
        else:
            self._prompt_nfo = ''

        self.widget_mode_info.configure(text=self._prompt_nfo)

    def set_text_to_speech(self):
        self._text_to_speech = self.switch_text_to_speech.get()
        if DEBUG:
            print(f'Text to speech: {self._text_to_speech}')

    def save_settings(self):
        """Saves the settings selected in the settings display."""
        self._frequency_penalty = self._new_frequency_penalty
        self._gpt_temperature = self._new_gpt_temperature
        self._max_tokens = self._new_max_tokens
        self._presence_penalty = self._new_presence_penalty
        self._top_p = self._new_top_p
        self._best_of = self._new_best_of
        self._text_to_speech = self._new_text_to_speech
        self.win_settings.destroy()

    def speak_result(self, result_text, speech_cmd):
        print('SPEAKING!')
        os.system('echo "' + result_text + '" | ' + speech_cmd)

    def spawn_speak_task(self):
        process = multiprocessing.Process(target=self.speak_result, args=(self._result, self._text_to_speech_cmd))
        process.start()

    def submit(self):
        """Submits the entered question / request to the GPT service."""
        entered_text = self.question.get()  # this will collect the text from the text entry box
        self.answer.config(state=tk.NORMAL)
        self.answer.delete(0.0, tk.END)

        response = self.ask_gpt(entered_text)
        if DEBUG:
            print('=' * 100)
        self._result = response['choices'][0]['text']
        if DEBUG:
            print('Raw response:')
            print(response)
            print('=' * 100)
            print('Extracted result:')
            print(self._result)
            print('=' * 100)
        self._result = self._result.strip()
        if not self._result:
            self._result = "I can't answer that, sorry!"
        self.answer.insert(tk.END, self._result)
        self.answer.config(state=tk.DISABLED)
        if self._text_to_speech == 'yes':
            self.spawn_speak_task()

    def show_copy_to_message(self, error='', color='white'):
        self.lbl_status_bar.configure(text=error,
                                      justify="left"
                                      # , fg="red"
                                      )

    def validate_copy_to_skill(self, value):
        if self._albert_config.has_section(value):
            self.show_copy_to_message(error='The entered skill name, is already in use.')
            return False
        else:
            self.show_copy_to_message(error='')
            return True

    def validate_copy_to_prompt(self, value):
        pattern = '^[\w\d_()]*$'
        copy_to_prompt = value
        if not re.fullmatch(pattern, copy_to_prompt) and copy_to_prompt != '':
            self.show_copy_to_message(error='"Prompt prefix", should only include alphanumerics & '
                                            'underscores.')
            return False
        else:
            self.show_copy_to_message(error='')
            return True

    def submit_config_copy(self):
        copy_from_skill = self._prompt_mode
        copy_to_skill = self.ent_skill_copy_to_skill.get()
        copy_to_prompt = self.ent_skill_copy_to_prompt.get()

        if copy_to_prompt == '':
            self.show_copy_to_message(error='You must enter a prompt file prefix!')
            return
        elif exists(f'{self._app_prompt_files}/{copy_to_prompt}.nfo'):
            self.show_copy_to_message(error='The entered prompt prefix is already in use. Please choose another!')
            return
        if not self._albert_config.has_section(copy_to_skill):
            self._albert_config.copy_config_section(copy_from_skill, copy_to_skill)
        else:
            self.show_copy_to_message(error=f'Skill, "{copy_to_skill}", already exists!')
            # MessageBox.showwarning(title='Skill Exists', message=f'Skill, {copy_to_skill}, already exists!')
            # tk.messagebox.showwarning(title='Skill Exists', message=f'Skill, {copy_to_skill}, already exists!',
            #                                parent=self.win_skill_copy)
            return

        shutil.copyfile(f'{self._prompt_file}.prompt', f'{self._app_prompt_files}/{copy_to_prompt}.prompt')
        if exists(self._prompt_file + '.nfo'):
            shutil.copyfile(f'{self._prompt_file}.nfo', f'{self._app_prompt_files}/{copy_to_prompt}.nfo')
        else:
            open(f'{self._prompt_file}.nfo', 'a').close()
        self.quit_skill_copy()


if __name__ == "__main__":
    base_config = AlbertConfig(config_ini)
    # The start_mode is optionally set by the user via the argparse -m option.
    if start_mode:
        mode = start_mode
    else:
        mode = base_config.resolve_config_option("defaults", "mode")
    app = App(mode)
    icon_file = app_images / 'einstein_small.xbm'
    app.iconbitmap(bitmap="@" + str(icon_file))
    app.mainloop()