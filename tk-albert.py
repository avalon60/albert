import os
import tkinter as tk
from tkinter.tix import *
import tkinter.messagebox
import customtkinter
from PIL import ImageTk, Image
import openai
import pyperclip
import argparse
from argparse import HelpFormatter
import sys
from operator import attrgetter
from configparser import ConfigParser, ExtendedInterpolation
import textwrap
from os.path import exists
import multiprocessing

DEBUG = True
# Initialise primary constants
prog = os.path.basename(__file__)
home_dir = os.getenv("HOME")

headings_point_size = -14

platform = sys.platform
if platform == "win32":
    platform = "Windows"
elif platform == "darwin":
    platform = "MacOS"
else:
    platform = "Linux"


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
                default='general',
                dest='start_mode')
ap.add_argument("-t", '--set-theme', required=False, action="store", help="Overrides the default appearance "
                                                                          "(green). Valid options are: 'green', "
                                                                          " 'blue',and 'dark-blue'.",
                dest='THEME', default='green')

ap.add_argument("-H", '--albert-home', required=False, default=home_dir + '/albert',
                action="store",
                help="The pathname to the initialisation file. The default location is $HOME/albert/config/albert.ini.",
                dest='albert_home')

args_list = vars(ap.parse_args())
start_mode = args_list["start_mode"]
albert_home = args_list["albert_home"]
app_images = albert_home + '/images'
app_config = albert_home + '/config'
prompt_files = albert_home + '/prompt_files'
config_ini = app_config + '/albert.ini'
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
    :rtype: str
    :param text_string:
    :param wrap_width:
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
        self.config.read(self.config_path)

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
        elif self.config.has_option("defaults", this_option):
            property_val = self.config["defaults"][this_option]
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
            if list_section in ['global', 'defaults']:
                continue
            else:
                section_list.append(list_section.capitalize())
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


class App(customtkinter.CTk):

    def __init__(self, default_mode):

        super().__init__()

        self._prompt_mode = default_mode
        self._app_width = 1000
        self._app_height = 650
        self._display_fields_width = 120
        # The prompt_mode defines which GTP
        # prompt to work with
        self._prompt_mode = default_mode
        self._gpt_engine = app_config.resolve_config_option(default_mode, "gpt_engine")
        self._frequency_penalty = self._new_frequency_penalty \
            = float(app_config.resolve_config_option(default_mode, "frequency_penalty"))
        self._gpt_temperature = self._new_gpt_temperature = float(app_config.resolve_config_option(default_mode,
                                                                                                   "gpt_temperature"))
        self._max_tokens = self._new_max_tokens = int(app_config.resolve_config_option(default_mode, "max_tokens"))
        self._presence_penalty = self._new_presence_penalty = float(app_config.resolve_config_option(default_mode,
                                                                                                     "presence_penalty"))
        self._top_p = self._new_top_p = float(app_config.resolve_config_option(default_mode,
                                                                               "top_p"))
        self._best_of = self._new_best_of = float(app_config.resolve_config_option(default_mode,
                                                                                   "best_of"))
        self._text_to_speech = self._new_text_to_speech = app_config.resolve_config_option(default_mode,
                                                                                           "text_to_speech")
        self._stop = app_config.resolve_config_option(default_mode, "stop")
        self._text_to_speech_cmd = app_config.resolve_config_option(default_mode, "text_to_speech_cmd")
        self._q_prompt = app_config.resolve_config_option(mode, "q_prompt")
        self._a_prompt = app_config.resolve_config_option(mode, "a_prompt")
        self._result = ''
        self._prompt_file = app_config.resolve_config_option(default_mode, "prompt_file")
        with open(self._prompt_file + '.prompt', 'r') as file:
            self._prompt = file.read()

        # See if the prompt file is accompanied by an info file.
        if exists(self._prompt_file + '.nfo'):
            with open(self._prompt_file + '.nfo', 'r') as file:
                self._prompt_nfo = file.read()
                self._prompt_nfo = wrap_string(self._prompt_nfo, self._display_fields_width - 10)

        self.title("Albert")
        self.geometry(f"{self._app_width}x{self._app_height}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed
        self.openai_api_key = app_config.resolve_config_option("global", "openai_api_key")
        openai.api_key = self.openai_api_key

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ============ Left frame ====================
        self.frame_left = customtkinter.CTkFrame(master=self, borderwidth=0)
        self.frame_left.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        self.frame_right = customtkinter.CTkFrame(master=self,
                                                  width=180,
                                                  corner_radius=0)
        self.frame_right.grid(row=0, column=2, sticky="nswe")

        # configure grid layout (3x7)
        self.frame_left.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_left.rowconfigure(7, weight=10)
        self.frame_left.columnconfigure((0, 1), weight=1)
        self.frame_left.columnconfigure(2, weight=0)

        self.widget_mode_info = customtkinter.CTkLabel(self.frame_left,
                                                       text=self._prompt_nfo,
                                                       width=self._display_fields_width, height=10)
        self.widget_mode_info.grid(row=0, column=0, padx=15, pady=15, sticky="ew")

        self.question = customtkinter.CTkEntry(master=self.frame_left,
                                               width=self._display_fields_width,
                                               placeholder_text="Enter your request")
        self.question.grid(row=2, column=0, columnspan=2, pady=5, padx=10, sticky="we")

        self.answer = tkinter.Text(master=self.frame_left,
                                   relief='flat',
                                   bg=WIDGET_BG_COLOUR,
                                   fg=WIDGET_FG_COLOUR,
                                   wrap=tkinter.WORD,
                                   borderwidth=0,
                                   bd=0,
                                   height=25,
                                   width=100)

        scroll_bar = tkinter.Scrollbar(self, command=self.answer.yview)
        scroll_bar.grid(row=0, column=1, sticky='e')

        self.answer.config(state=tkinter.DISABLED)

        self.answer.grid(row=3, column=0, sticky="nwe", padx=5, pady=10)

        # ============ Right Frame ============
        # configure grid layout (1x11)
        self.frame_right.grid_rowconfigure(0, minsize=10)  # empty row with minsize as spacing
        self.frame_right.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frame_right.grid_rowconfigure(8, minsize=20)  # empty row with minsize as spacing
        self.frame_right.grid_rowconfigure(10, minsize=20)  # empty row with minsize as spacing
        self.frame_right.grid_rowconfigure(14, minsize=10)  # empty row with minsize as spacing

        self.submit = customtkinter.CTkButton(master=self.frame_right,
                                              text="Submit",
                                              border_width=2,
                                              fg_color=None,
                                              command=self.submit)
        self.submit.grid(row=2, column=0, pady=10, padx=20)

        self.copy = customtkinter.CTkButton(master=self.frame_right,
                                            text="Copy",
                                            border_width=2,
                                            fg_color=None,
                                            command=self.copy)
        self.copy.grid(row=3, column=0, pady=10, padx=20)

        self.clear = customtkinter.CTkButton(master=self.frame_right,
                                             text="Clear",
                                             border_width=2,
                                             fg_color=None,
                                             command=self.clear)
        self.clear.grid(row=4, column=0, pady=10, padx=20)

        switch_var = tkinter.StringVar()
        switch_var.set(self._text_to_speech)

        self.switch_text_to_speech = customtkinter.CTkSwitch(master=self.frame_right,
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
                                                "response being displayed, it is also processed via text-to-speech."
                                                "This option requires that you have Festival text-to-speech installed.",
                                                TOOLTIP_BG_COLOUR)

        self.label_mode = customtkinter.CTkLabel(master=self.frame_right,
                                                 text="Skill (GPT prompt)",
                                                 justify="left",
                                                 text_font=("Roboto Medium", headings_point_size))

        self.label_mode.grid(row=9, column=0, pady=0, padx=0, sticky="n")

        modes_list = app_config.modes_list()

        self.combo_mode = customtkinter.CTkOptionMenu(master=self.frame_right,
                                                      values=modes_list,
                                                      command=self.set_prompt_mode)
        self.combo_mode.grid(row=10, column=0, pady=0, padx=0, sticky="n")
        self.combo_mode.set(self._prompt_mode.capitalize())

        self.label_filler = customtkinter.CTkLabel(master=self.frame_right,
                                                   text="",
                                                   justify="left")

        self.label_filler.grid(row=11, column=0, pady=0, padx=0, sticky="n")

        self.settings = customtkinter.CTkButton(master=self.frame_right,
                                                text="Settings",
                                                border_width=2,
                                                fg_color=None,
                                                command=self.launch_settings)

        self.settings.grid(row=14, column=0, pady=15, padx=20, sticky="s")

        self.quit = customtkinter.CTkButton(master=self.frame_right,
                                            text="Quit",
                                            border_width=2,
                                            fg_color=None,
                                            command=self.on_closing)
        self.quit.grid(row=15, column=0, pady=15, padx=2, sticky="s")

        self.avatar_image = app_images + '/albert_einstein_lol.gif'

        self.avatar = Image.open(self.avatar_image)
        self.avatar = self.avatar.resize((130, 130))
        self.einstein = tkinter.PhotoImage(file=self.avatar_image)
        self.avatar = ImageTk.PhotoImage(self.avatar)

        label_avatar = customtkinter.CTkLabel(self.frame_right, image=self.avatar, width=50, height=50)
        label_avatar.grid(row=0, column=0, padx=15, pady=15, sticky="w")

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

    def launch_settings(self):
        self.settings = customtkinter.CTkToplevel()
        self.settings.wait_visibility()
        self.settings.grab_set()
        self.settings.title("Albert's Settings")
        #                        W x H
        self.settings.geometry(f"575x350")

        # self.settings.iconbitmap('/home/clive/albert/images/einstein_small.xbm')

        self.label_gpt_settings = customtkinter.CTkLabel(master=self.settings,
                                                         text=f"GPT Settings for  {self._prompt_mode.capitalize()}",
                                                         fg_="green",
                                                         justify="center",
                                                         text_font=("Roboto Medium", headings_point_size))

        self.label_gpt_settings.grid(row=1, column=0, pady=10, padx=0)

        self.label_temperature = customtkinter.CTkLabel(master=self.settings, text=" " * 30 + "Temperature")

        self.label_temperature.grid(row=3, column=0, pady=0, padx=0, sticky="e")

        self.temperature_bar = customtkinter.CTkSlider(master=self.settings,
                                                       from_=0,
                                                       to=1,
                                                       number_of_steps=100,
                                                       command=self.set_temperature)
        self.temperature_bar.grid(row=3, column=1, columnspan=1, pady=10, padx=0, sticky="w")

        self.temperature_tip = CreateToolTip(self.temperature_bar,
                                             "Controls randomness: Lowering results in less random completions. As "
                                             "the temperature approached zero, the model will become more "
                                             "deterministic and repetitive.", TOOLTIP_BG_COLOUR)

        self._new_label_temperature_val = customtkinter.CTkLabel(master=self.settings,
                                                                 text="{:.3f}".format(self._gpt_temperature))

        self._new_label_temperature_val.grid(row=3, column=2, pady=0, padx=0, sticky="w")

        self.max_tokens = customtkinter.CTkLabel(master=self.settings, text="Max Length (Tokens)")
        self.max_tokens.grid(row=5, column=0, pady=0, padx=0, sticky="e")
        self.tokens_bar = customtkinter.CTkSlider(master=self.settings,
                                                  from_=1,
                                                  to=4000,
                                                  number_of_steps=100,
                                                  command=self.set_max_tokens)
        self.tokens_bar.grid(row=5, column=1, columnspan=1, pady=10, padx=0, sticky="w")
        self.tokens_tip = CreateToolTip(self.tokens_bar,
                                        "The maximum number of tokens to generate. Requests can use up to 2,048 or "
                                        "4,000 tokens, shared between prompt and completion. The exact limit varies by "
                                        "model. (One token is roughly 4 characters of English text)", TOOLTIP_BG_COLOUR)
        self._new_label_max_tokens_val = customtkinter.CTkLabel(master=self.settings,
                                                                text="{:.0f}".format(self._max_tokens))

        self._new_label_max_tokens_val.grid(row=5, column=2, pady=0, padx=0, sticky="w")

        self.label_top_p = customtkinter.CTkLabel(master=self.settings, text=" " * 30 + "Top P")
        self.label_top_p.grid(row=7, column=0, pady=0, padx=0, sticky="e")
        self.top_p_bar = customtkinter.CTkSlider(master=self.settings,
                                                 from_=0,
                                                 to=1,
                                                 number_of_steps=100,
                                                 command=self.set_top_p)

        self.top_p_bar.grid(row=7, column=1, columnspan=1, pady=10, padx=0, sticky="w")
        self.top_p_tip = CreateToolTip(self.top_p_bar,
                                       "Controls diversity via nucleus sampling: "
                                       "0.5 means half of all likelihood - weighted options are considered.",
                                       TOOLTIP_BG_COLOUR)

        self._new_label_top_p_val = customtkinter.CTkLabel(master=self.settings,
                                                           text="{:.3f}".format(self._top_p))
        self._new_label_top_p_val.grid(row=7, column=2, pady=0, padx=0, sticky="w")

        self._new_label_max_tokens_val.grid(row=5, column=2, pady=0, padx=0, sticky="w")
        self.label_frequency = customtkinter.CTkLabel(master=self.settings, text=" " * 15 + "Frequency penalty")
        self.label_frequency.grid(row=9, column=0, pady=0, padx=0, sticky="e")

        self.frequency_penalty_bar = customtkinter.CTkSlider(master=self.settings,
                                                             from_=0,
                                                             to=2,
                                                             number_of_steps=100,
                                                             command=self.set_frequency_penalty)

        self.frequency_penalty_bar.grid(row=9, column=1, columnspan=1, pady=10, padx=0, sticky="w")
        self.frequency_penalty_tip = CreateToolTip(self.frequency_penalty_bar,
                                                   "How much to penalise new tokens based on their existing frequency "
                                                   "in the text so far. Decreases the model's likelihood to repeat the "
                                                   "same line verbatim.", TOOLTIP_BG_COLOUR)

        self._new_label_frequency_penalty_val = customtkinter.CTkLabel(master=self.settings,
                                                                       text="{:.3f}".format(self._frequency_penalty))
        self._new_label_frequency_penalty_val.grid(row=9, column=2, pady=0, padx=0, sticky="w")

        self.label_presence = customtkinter.CTkLabel(master=self.settings, text=" " * 10 + "Presence penalty")
        self.label_presence.grid(row=11, column=0, pady=0, padx=0, sticky="e")

        self.presence_penalty_bar = customtkinter.CTkSlider(master=self.settings,
                                                            from_=0,
                                                            to=2,
                                                            number_of_steps=100,
                                                            command=self.set_presence_penalty)

        self.presence_penalty_bar.grid(row=11, column=1, columnspan=2, pady=10, padx=0, sticky="w")
        self.presence_penalty_tip = CreateToolTip(self.presence_penalty_bar,
                                                  "How much to penalise new tokens depending on whether they appear "
                                                  "in the text so far. Increase the model's likelihood to talk about "
                                                  "new topics.", TOOLTIP_BG_COLOUR)
        self._new_label_presence_penalty_val = customtkinter.CTkLabel(master=self.settings,
                                                                      text="{:.3f}".format(self._presence_penalty))
        self._new_label_presence_penalty_val.grid(row=11, column=2, pady=0, padx=0, sticky="w")

        self.label_best_of = customtkinter.CTkLabel(master=self.settings, text=" " * 20 + "Best of")
        self.label_best_of.grid(row=13, column=0, pady=0, padx=0, sticky="e")
        self.best_of_bar = customtkinter.CTkSlider(master=self.settings,
                                                   from_=1,
                                                   to=20,
                                                   number_of_steps=100,
                                                   command=self.set_best_of)

        self.best_of_bar.grid(row=13, column=1, columnspan=2, pady=10, padx=0, sticky="w")
        self.best_of_tip = CreateToolTip(self.best_of_bar,
                                         "Generates multiple completions server-side, and displays only the "
                                         "best. Streaming only works when set to 1. Since it acts as a  "
                                         "multiplier on the number of completions, this parameter can eat "
                                         "into your token quota very quickly - use caution!", TOOLTIP_BG_COLOUR)
        self._new_label_best_of_val = customtkinter.CTkLabel(master=self.settings,
                                                             text="{:.0f}".format(self._best_of))

        self._new_label_best_of_val.grid(row=13, column=2, pady=0, padx=0, sticky="w")

        self.btn_cancel_settings = customtkinter.CTkButton(master=self.settings,
                                                           text="Cancel",
                                                           border_width=2,
                                                           fg_color=None,
                                                           command=self.settings.destroy)
        self.btn_cancel_settings.grid(row=28, column=0, pady=40, padx=0)
        # self.btn_cancel_settings.place(relx=0, rely=0, anchor=tkinter.CENTER)

        self.btn_save_settings = customtkinter.CTkButton(master=self.settings,
                                                         text="Save",
                                                         border_width=2,
                                                         fg_color=None,
                                                         command=self.save_settings)
        self.btn_save_settings.grid(row=28, column=2, pady=40, padx=1)

        self.best_of_bar.set(self._best_of)
        self.frequency_penalty_bar.set(self._frequency_penalty)
        self.presence_penalty_bar.set(self._presence_penalty)
        self.temperature_bar.set(self._gpt_temperature)
        self.tokens_bar.set(self._max_tokens)
        self.top_p_bar.set(self._top_p)

    def get_defaults(self, new_prompt_mode):
        """ Retrieves and sets the settings for the supplied prompt mode.

        :param new_prompt_mode:
        """
        self._gpt_engine = app_config.resolve_config_option(new_prompt_mode, "gpt_engine")
        self._gpt_temperature = app_config.resolve_config_option(new_prompt_mode, "gpt_temperature")
        self._max_tokens = app_config.resolve_config_option(new_prompt_mode, "max_tokens")
        self._prompt_file = app_config.resolve_config_option(new_prompt_mode, "prompt_file")
        self._stop = app_config.resolve_config_option(new_prompt_mode, "stop")
        self._text_to_speech_cmd = app_config.resolve_config_option(new_prompt_mode, "text_to_speech_cmd")
        with open(self._prompt_file + '.prompt', 'r') as file:
            self._prompt = file.read()

        # See if the prompt file is accompanied by an info file.
        if exists(self._prompt_file + '.nfo'):
            with open(self._prompt_file + '.nfo', 'r') as file:
                self._prompt_nfo = file.read()
                self._prompt_nfo = wrap_string(self._prompt_nfo, self._display_fields_width - 10)
        else:
            self._prompt_nfo = ''

    def clear(self):
        """ Clears out the contents of the question and answer entry widgets,
        """
        self.question.delete(0, tkinter.END)
        self.answer.config(state=tkinter.NORMAL)
        self.answer.delete(0.0, tkinter.END)
        self.answer.config(state=tkinter.DISABLED)
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
        self._new_label_temperature_val.configure(text="{:.3f}".format(self._new_gpt_temperature))
        # print (f"Temperature set to: {self.temperature}")

    def set_max_tokens(self, new_max_tokens):
        """Updates the self._new_max_tokens. This property is only promoted when the save_settings mode is
        called. """
        self._new_max_tokens = new_max_tokens
        self._new_label_max_tokens_val.configure(text="{:.0f}".format(self._new_max_tokens))

    def set_frequency_penalty(self, new_frequency_penalty):
        """Updates the self._new_frequency_penalty. This property is only promoted when the save_settings mode is
        called. """
        self._new_frequency_penalty = new_frequency_penalty
        self._new_label_frequency_penalty_val.configure(text="{:.3f}".format(self._new_frequency_penalty))

    def set_presence_penalty(self, new_presence_penalty):
        """Updates the self._new_presence_penalty. This property is only promoted when the save_settings mode is
        called. """
        self._new_presence_penalty = new_presence_penalty
        self._new_label_presence_penalty_val.configure(text="{:.3f}".format(self._new_presence_penalty))

    def set_top_p(self, new_top_p):
        """Updates the self._new_top_p. This property is only promoted when the save_settings mode is
        called. """
        self._new_top_p = new_top_p
        self._new_label_top_p_val.configure(text="{:.3f}".format(self._new_top_p))
        # print('New top = ' + str(self._new_top_p))

    def set_best_of(self, new_best_of):
        """Updates the self._new_best_of property. This property is only promoted when the save_settings mode is
        called. """
        self._new_best_of = new_best_of
        self._new_label_best_of_val.configure(text="{:.0f}".format(self._new_best_of))

    def set_prompt_mode(self, choice: str):
        """Sets all related settings associated with a newly selected prompt mode (personality).
        :param choice:
        """
        choice = choice.lower()
        self._prompt_mode = choice
        self._gpt_engine = app_config.resolve_config_option(choice, "gpt_engine")
        self._frequency_penalty = float(app_config.resolve_config_option(choice, "frequency_penalty"))
        self._gpt_temperature = float(app_config.resolve_config_option(choice, "gpt_temperature"))
        self._max_tokens = int(app_config.resolve_config_option(choice, "max_tokens"))
        self._presence_penalty = float(app_config.resolve_config_option(choice, "presence_penalty"))
        self._top_p = float(app_config.resolve_config_option(choice, "top_p"))
        self._best_of = float(app_config.resolve_config_option(choice, "best_of"))
        self._text_to_speech = app_config.resolve_config_option(choice, "text_to_speech")
        self._stop = app_config.resolve_config_option(choice, "stop")
        self._text_to_speech_cmd = app_config.resolve_config_option(choice, "text_to_speech_cmd")
        self._q_prompt = app_config.resolve_config_option(choice, "q_prompt")
        self._a_prompt = app_config.resolve_config_option(choice, "a_prompt")
        self._prompt_file = app_config.resolve_config_option(choice, "prompt_file")
        with open(self._prompt_file + '.prompt', 'r') as file:
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
        self.settings.destroy()

    def speak_result(self, result_text, speech_cmd):
        print('SPEAKING!')
        os.system('echo "' + result_text + '" | ' + speech_cmd)

    def spawn_speak_task(self):
        process = multiprocessing.Process(target=self.speak_result, args=(self._result, self._text_to_speech_cmd))
        process.start()

    def submit(self):
        """Submits the entered question / request to the GPT service."""
        entered_text = self.question.get()  # this will collect the text from the text entry box
        self.answer.config(state=tkinter.NORMAL)
        self.answer.delete(0.0, tkinter.END)

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
        self.answer.insert(tkinter.END, self._result)
        self.answer.config(state=tkinter.DISABLED)
        if self._text_to_speech == 'yes':
            self.spawn_speak_task()


if __name__ == "__main__":
    app_config = AlbertConfig(config_ini)
    # The start_mode is optionally set by the user via the argparse -m option.
    if not start_mode:
        mode = start_mode
    else:
        mode = app_config.resolve_config_option("defaults", "mode")

    app = App(mode)
    icon_file = app_images + '/einstein_small.xbm'
    app.iconbitmap(bitmap="@" + icon_file)
    app.mainloop()
