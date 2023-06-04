import tkinter as tk
import tkinter
import customtkinter as ctk
from customtkinter import ThemeManager
from customtkinter import CTkBaseClass
from tkinter import ttk
import textwrap


# Define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class InvalidParameterValue(Error):
    """Raised when the input value is too small"""
    pass


# Defaults/constants
SIDE_FRAMES_WIDTH = 160
STATUS_BAR_FONT_SIZE = -12
HEADINGS_FONT_SIZE = -14
DEFAULT_FONT_SIZE = -14
DEFAULT_FONT = "Roboto Medium"

tooltip_bg_colour_dict = {"green": "#72CF9F",
                          "blue": "#3B8ED0",
                          "dark-blue": "#608BD5"}

widget_bg_colour_dict = {"dark": "#3D3D3D",
                         "light": "#FFFFFF",
                         "system": "#FFFFFF"}

widget_fg_colour_dict = {"dark": "#E1E2DF",
                         "light": "#3button3_text640",
                         "system": "#3button3_text640"}

regions_fg_colour_dict = {"dark": "#E1E2DF",
                          "light": "#3button3_text640",
                          "system": "#3button3_text640"}

frame_colour_dict = {"dark": "#2E2E2E",
                     "light": "#DEDEDE",
                     "system": "#DEDEDE"}

base_colour_dict = {"dark": "#1F1F1F",
                    "light": "#DEDEDE",
                    "system": "#DEDEDE"}


def str_mode_to_int():
    appearance_mode = ctk.get_appearance_mode()
    if appearance_mode == "Light":
        return 0
    return 1


def get_color_from_name(name: str):
    int_mode = str_mode_to_int()
    return ThemeManager.theme["color"][name][int_mode]

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


def set_entry(widget_object: tk.Entry, text):
    # widget_object.delete(0, "END")
    # widget_object.delete(0, tk.END)
    widget_object.insert(tk.END, text)
    return


class CBTk(ctk.CTk):
    """Root window kick-start class. Provides optionally up to 3 columnar frames. The middle frame owns the weight and
     expands/contracts on lateral resizing of the window. It also provides options for a couple of starter buttons:
     Submit and Cancel. """

    def __init__(self,
                 *args,
                 window_height: int = 0,
                 window_width: int = 0,
                 padx: int = 5,
                 pady: int = 5,
                 appearance_mode: str = 'Light',
                 theme: str = 'green',
                 initial_frames: int = 2,
                 frame_orientation: str = 'v',
                 add_submit: bool = False,
                 add_edit: bool = False,
                 add_delete: bool = False,
                 add_cancel: bool = False,
                 add_status_bar: bool = True,
                 adjustable_window: bool = False,
                 status_bar_font=DEFAULT_FONT,
                 status_bar_font_size=STATUS_BAR_FONT_SIZE,
                 status_text_life=0,
                 title='CBTk',
                 **kwargs):
        """
        Root window class; instantiates with the following parameters. All of which are optional except for master and
        window name).
        :param args:
        :param window_height:
        :param window_width:
        :param padx:
        :param pady:
        :param appearance_mode:
        :param theme:
        :param left_frame:
        :param centre_frame:
        :param right_frame:
        :param add_submit:
        :param add_cancel:
        :param add_status_bar:
        :param status_bar_font:
        :param status_bar_font_size:
        :param status_text_life:
        :param title:
        :param kwargs:
        """

        if 'window_height' in kwargs:
            self._app_height = kwargs.pop('window_height')
        else:
            self._app_height = window_height

        if 'title' in kwargs:
            self._title = kwargs.pop('title')
        else:
            self._title = title

        if 'window_width' in kwargs:
            self._app_width = kwargs.pop('window_width')
        else:
            self._app_width = window_width

        if 'appearance_mode' in kwargs:
            appearance_mode = kwargs.pop('appearance_mode')
        if 'theme' in kwargs:
            window_width = kwargs.pop('theme')

        if 'initial_frames' in kwargs:
            self.initial_frames = kwargs.pop('initial_frames')
        else:
            self.initial_frames = initial_frames

        if 'add_status_bar' in kwargs:
            status_bar = kwargs.pop('add_status_bar')
        if 'adjustable_window' in kwargs:
            adjustable_window = kwargs.pop('adjustable_window')
        if 'add_submit' in kwargs:
            add_submit = kwargs.pop('add_submit')

        if 'btn_edit' in kwargs:
            add_edit = kwargs.pop('btn_edit')

        if 'btn_delete' in kwargs:
            add_delete = kwargs.pop('btn_delete')

        if 'add_cancel' in kwargs:
            add_cancel = kwargs.pop('add_cancel')

        super().__init__(*args, **kwargs)
        ctk.set_appearance_mode(appearance_mode)  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme(theme)  # Themes: "blue" (standard), "green", "dark-blue"

        self._pad_x = padx
        self._pad_y = pady

        self._status_text_life = status_text_life

        assert isinstance(self._status_text_life, int)
        assert isinstance(self._app_height, int)
        assert isinstance(self._app_width, int)
        assert frame_orientation in ('v', 'h'), 'Parameter frame_orientation, must be either "v" or "h"'

        self.title(title)
        if self._app_width and self._app_height:
            geometry = f"{self._app_width}x{self._app_height}"
            self.geometry(geometry)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        if initial_frames == 2:
            if frame_orientation == 'v':
                self.grid_columnconfigure(0, weight=1)
            else:
                self.grid_rowconfigure(0, weight=1)
        elif initial_frames == 3:
            if frame_orientation == 'v':
                self.grid_columnconfigure(1, weight=1)
            else:
                self.grid_rowconfigure(1, weight=1)

        if add_status_bar and frame_orientation == 'v':
            self.grid_rowconfigure(0, weight=1)

        # If initial panels are requested then let's provide them.
        if initial_frames >= 1:
            self.first_frame = ctk.CTkFrame(master=self, borderwidth=0, corner_radius=0, width=SIDE_FRAMES_WIDTH)
            self.first_frame.grid(row=0, column=0, sticky="nsew", padx=padx, pady=pady)

        if initial_frames == 1:
            self.first_frame = ctk.CTkFrame(master=self, borderwidth=0, corner_radius=0, width=SIDE_FRAMES_WIDTH)
            self.first_frame.grid(row=0, column=0, sticky="nsew", padx=padx, pady=pady)
            self.button_frame = self.first_frame = self.first_frame

        if initial_frames >= 2:
            self.second_frame = ctk.CTkFrame(master=self, borderwidth=0)
            if frame_orientation == 'v':
                self.second_frame.grid(row=0, column=1, sticky="nsew", padx=padx, pady=pady)
            else:
                self.second_frame.grid(row=1, column=0, sticky="nsew", padx=padx, pady=pady)

        if initial_frames == 2:
            self.entry_frame = self.first_frame
            self.button_frame = self.second_frame

        if initial_frames == 3:
            self.third_frame = ctk.CTkFrame(master=self, borderwidth=0)
            if frame_orientation == 'v':
                self.third_frame.grid(row=0, column=2, sticky="nsew", padx=padx, pady=pady)
            else:
                self.third_frame.grid(row=2, column=0, sticky="nsew", padx=padx, pady=pady)

            self.filter_frame = self.first_frame
            self.entry_frame = self.second_frame
            self.button_frame = self.third_frame

        # Now we check to see if default buttons are requested.
        # CANCEL button
        if add_cancel:
            self.btn_cancel = ctk.CTkButton(master=self.button_frame,
                                            text="Cancel",
                                            border_width=2,
                                            fg_color=None,
                                            command=self.on_closing)
            self.btn_cancel.grid(row=0, column=0, padx=padx, pady=pady, sticky="ew")

        # EDIT button
        if add_edit:
            self.btn_edit = ctk.CTkButton(master=self.button_frame,
                                          text="Edit",
                                          border_width=2,
                                          fg_color=None,
                                          command=self.on_closing)
            if frame_orientation == 'v':
                self.btn_edit.grid(row=1, column=0, padx=padx, pady=pady, sticky="ew")
            else:
                self.btn_edit.grid(row=0, column=1, padx=padx, pady=pady, sticky="ew")

        if add_delete:
            self.btn_delete = ctk.CTkButton(master=self.button_frame,
                                            text="Delete",
                                            border_width=2,
                                            fg_color=None,
                                            command=self.on_closing)
            if frame_orientation == 'v':
                self.btn_delete.grid(row=3, column=0, padx=padx, pady=pady, sticky="ew")
            else:
                self.btn_delete.grid(row=0, column=3, padx=padx, pady=pady, sticky="ew")

        # SUBMIT button
        if add_submit:
            self.btn_submit = ctk.CTkButton(master=self.button_frame,
                                            text="Submit",
                                            border_width=2,
                                            fg_color=None,
                                            command=self.on_closing)
            if frame_orientation == 'v':
                self.btn_submit.grid(row=9, column=0, padx=padx, pady=pady, sticky="ew")
            else:
                self.btn_submit.grid(row=0, column=9, padx=padx, pady=pady, sticky="ew")

        self._add_status_bar = add_status_bar
        if add_status_bar:
            self._status_bar = CBtkStatusBar(master=self,
                                             font=status_bar_font,
                                             font_size=status_bar_font_size,
                                             status_text_life=self._status_text_life)
            self.bind("<Configure>", self._status_bar.auto_size_status_bar)

        self.update_idletasks()
        screen_width = self.winfo_width()
        screen_height = self.winfo_height()

        if not adjustable_window:
            self.minsize(screen_width, screen_height)
            self.maxsize(screen_width, screen_height)

    def close_window(self):
        self.on_closing()

    def on_closing(self, event=0):
        if self._status_bar:
            self._status_bar.cancel_message_timer()
        self.destroy()

    def set_status_text(self, status_text, status_text_life=None):
        if self._status_bar:
            self._status_bar.set_status_text(status_text=status_text)
        else:
            print('ERROR: No status bar configured for this object.')

    def set_status_fg_colour(self, fg_color):
        self._status_bar.set_fg_color(fg_color=fg_color)

    def set_status_text_colour(self, text_color):
        self._status_bar.set_text_color(text_color=text_color)

    def set_status_text_life(self, status_text_life):
        self._status_text_life = status_text_life
        self._status_bar.set_status_text_life(self._status_text_life)

    def _str_mode_to_int(self):
        self._appearance_mode = ctk.get_appearance_mode()
        if self._appearance_mode == "Light":
            return 0
        return 1

    def _get_color_from_name(self, name: str):
        self._int_mode = self._str_mode_to_int()
        return ThemeManager.theme["color"][name][self._int_mode]


class CBTkToplevel(ctk.CTkToplevel):
    """TopLevel kick-start class. Provides optionally up to 3 columnar frames. The middle frame owns the weight and
    expands/contracts on lateral resizing of the window. It also provides options for a couple of starter buttons:
    Submit and Cancel. """

    def __init__(self, *args,
                 master: object,
                 window_name: str,
                 window_height: int = 0,
                 window_width: int = 0,
                 padx: tuple = 5,
                 pady: tuple = 5,
                 modal: bool = True,
                 hide_master: bool = False,
                 initial_frames: int = 2,
                 frame_orientation: str = 'v',
                 add_submit: bool = False,
                 add_edit: bool = False,
                 add_delete: bool = False,
                 add_cancel: bool = False,
                 add_status_bar: bool = True,
                 adjustable_window: bool = False,
                 status_bar_font=DEFAULT_FONT,
                 status_bar_font_size=STATUS_BAR_FONT_SIZE,
                 status_text_life=0,
                 **kwargs):
        """
        Class instantiates with the following parameters. All of which are optional except for master and window name).
        :param args:
        :param master: The parent CTk widget.
        :param window_name: Name of the CTk window.
        :param window_height: Optional height of the window, in pixels.
        :param window_width: Optional width of the window in pixels.
        :param padx:
        :param pady:
        :param modal: If set to true, causes grab_set to prevent interaction with other windows within the app.
        :param hide_master: If set to true, requests that the master be hidden. This is currently broken with
               customtkinter
        :param initial_frames: Number of frames to auto-create. These are side-by-side frames. Default 2
        :param status_bar: If set to true, a status bar is included, of the CBtkStatusBar class.
        :param add_submit: If set to true a non-functional (no command is implemented) Submit button is included.
        :param add_cancel: If set to true a functional Cancel button is included.
        :param status_bar:
        :param adjustable_window: If set to True, the window geometry is locked (i.e. cannot be resized).
        :param status_bar_font:
        :param status_bar_font_size:
        :param status_text_life:
        :param kwargs:
        """

        if 'window_height' in kwargs:
            self._app_height = kwargs.pop('window_height')
        else:
            self._app_height = window_height

        if 'window_width' in kwargs:
            self._app_width = kwargs.pop('window_width')
        else:
            self._app_width = window_width

        if 'initial_frames' in kwargs:
            self.initial_frames = kwargs.pop('initial_frames')
        else:
            self.initial_frames = initial_frames

        if 'add_status_bar' in kwargs:
            add_status_bar = kwargs.pop('add_status_bar')

        if 'btn_submit' in kwargs:
            add_submit = kwargs.pop('btn_submit')

        if 'btn_edit' in kwargs:
            add_edit = kwargs.pop('btn_edit')

        if 'btn_delete' in kwargs:
            add_delete = kwargs.pop('btn_delete')

        if 'btn_cancel' in kwargs:
            add_cancel = kwargs.pop('btn_cancel')

        if 'adjustable_window' in kwargs:
            adjustable_window = kwargs.pop('adjustable_window')

        super().__init__(master, *args, **kwargs)

        assert isinstance(window_height, int)
        assert isinstance(window_width, int)

        self._status_text_life = status_text_life
        assert isinstance(self._status_text_life, int)
        assert frame_orientation in ('v', 'h'), 'Parameter frame_orientation, must be either "v" or "h"'

        self._master = master
        self._status_bar = add_status_bar
        self.name = window_name
        self.title(window_name)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        if modal:
            self.wait_visibility()
            self.grab_set()

        if hide_master:
            self.wait_visibility()
            self._master.withdraw()

        if window_height and window_width:
            auto_size = True
            geometry = f"{self._app_width}x{self._app_height}"
            self.geometry(geometry)

        if initial_frames == 2:
            if frame_orientation == 'v':
                self.grid_columnconfigure(0, weight=1)
            else:
                self.grid_rowconfigure(0, weight=1)
        elif initial_frames == 3:
            if frame_orientation == 'v':
                self.grid_columnconfigure(1, weight=1)
            else:
                self.grid_rowconfigure(1, weight=1)

        if add_status_bar and frame_orientation == 'v':
            self.grid_rowconfigure(0, weight=1)

        # If initial panels are requested then let's provide them.
        if initial_frames >= 1:
            self.first_frame = ctk.CTkFrame(master=self, borderwidth=0, corner_radius=0, width=SIDE_FRAMES_WIDTH)
            self.first_frame.grid(row=0, column=0, sticky="nsew", padx=padx, pady=pady)

        if initial_frames == 1:
            self.first_frame = ctk.CTkFrame(master=self, borderwidth=0, corner_radius=0, width=SIDE_FRAMES_WIDTH)
            self.first_frame.grid(row=0, column=0, sticky="nsew", padx=padx, pady=pady)
            self.button_frame = self.first_frame = self.first_frame
            self.entry_frame = self.button_frame

        if initial_frames >= 2:
            self.second_frame = ctk.CTkFrame(master=self, borderwidth=0)
            if frame_orientation == 'v':
                self.second_frame.grid(row=0, column=1, sticky="nsew", padx=padx, pady=pady)
            else:
                self.second_frame.grid(row=1, column=0, sticky="nsew", padx=padx, pady=pady)

        if initial_frames == 2:
            self.entry_frame = self.first_frame
            self.button_frame = self.second_frame

        if initial_frames == 3:
            self.third_frame = ctk.CTkFrame(master=self, borderwidth=0)
            if frame_orientation == 'v':
                self.third_frame.grid(row=0, column=2, sticky="nsew", padx=padx, pady=pady)
            else:
                self.third_frame.grid(row=2, column=0, sticky="nsew", padx=padx, pady=pady)

            self.filter_frame = self.first_frame
            self.entry_frame = self.second_frame
            self.button_frame = self.third_frame

        # Now we check to see if default buttons are requested.
        # SUBMIT button
        self.update_idletasks()
        screen_width = self.winfo_width()

        # CANCEL button

        if add_cancel:
            self.btn_cancel = ctk.CTkButton(master=self.button_frame,
                                            text="Cancel",
                                            border_width=2,
                                            fg_color=None,
                                            command=self.on_closing)

            self.btn_cancel.grid(row=0, column=0, padx=padx, pady=pady, sticky="ew")

        # EDIT button
        if add_edit:
            self.btn_edit = ctk.CTkButton(master=self.button_frame,
                                          text="Edit",
                                          border_width=2,
                                          fg_color=None,
                                          command=self.on_closing)
            if frame_orientation == 'v':
                self.btn_edit.grid(row=1, column=0, padx=padx, pady=pady, sticky="ew")
            else:
                self.btn_edit.grid(row=0, column=1, padx=padx, pady=pady, sticky="ew")

        if add_delete:
            self.btn_delete = ctk.CTkButton(master=self.button_frame,
                                            text="Delete",
                                            border_width=2,
                                            fg_color=None,
                                            command=self.on_closing)

            if frame_orientation == 'v':
                self.btn_delete.grid(row=3, column=0, padx=padx, pady=pady, sticky="ew")
            else:
                self.btn_delete.grid(row=0, column=3, padx=padx, pady=pady, sticky="ew")

        # SUBMIT button
        if add_submit:
            self.btn_submit = ctk.CTkButton(master=self.button_frame,
                                            text="Submit",
                                            border_width=2,
                                            fg_color=None,
                                            command=self.on_closing)
            if frame_orientation == 'v':
                self.btn_submit.grid(row=9, column=0, padx=padx, pady=pady, sticky="ew")
            else:
                self.btn_submit.grid(row=0, column=9, padx=padx, pady=pady, sticky="ew")

        self._add_status_bar = add_status_bar
        if add_status_bar:
            self._status_bar = CBtkStatusBar(master=self,
                                             font=status_bar_font,
                                             font_size=status_bar_font_size,
                                             status_text_life=self._status_text_life)
            self.bind("<Configure>", self._status_bar.auto_size_status_bar)

        self.update_idletasks()
        screen_width = self.winfo_width()
        screen_height = self.winfo_height()

        if not adjustable_window:
            self.minsize(screen_width, screen_height)
            self.maxsize(screen_width, screen_height)

    def close_window(self):
        """Using close_window is synonymous with a call to on_closing. If using the status message timeout feature,
        it is important to use the close_window function to facilitate the close. This prevents the later reference
        and exception, associated with an "after" method resource reference to an object which is destroyed."""
        self.on_closing()

    def on_closing(self, event=0):
        """Using on_closing is synonymous with a call to close_window. If using the status message timeout feature,
        it is important to use the close_window function to facilitate the close. This prevents the later reference
        and exception, associated with an "after" method resource reference to an object which is destroyed."""
        self._status_bar.cancel_message_timer()
        self.destroy()

    def set_status_text(self, status_text, status_text_life=None):
        if self._status_bar:
            self._status_bar.set_status_text(status_text=status_text, status_text_life=status_text_life)
        else:
            print('ERROR: No status bar configured for this object.')

    def set_status_text_life(self, status_text_life):
        self._status_text_life = status_text_life
        self._status_bar.set_status_text_life(self._status_text_life)


class CBtkCollapsiblePane(ctk.CTkFrame):

    def __init__(self,
                 parent,
                 option_text='',
                 initial_state='collapsed',
                 expand_text="+",
                 collapse_text="-",
                 frame_padx=5,
                 frame_pady=5,
                 button_width=35):

        ctk.CTkFrame.__init__(self, parent)
        s = ttk.Style()
        self._initial_state = initial_state

        self._frame_padx = frame_padx
        self._frame_pady = frame_pady

        # These are the class variable
        # see an underscore in expanded_text and _collapsed_text
        # this means these are private to class
        self.parent = parent
        self._expand_text = expand_text
        self._collapse_text = collapse_text

        # Here weight implies that it can grow its
        # size if extra space is available
        # default weight is 0
        self.columnconfigure(1, weight=1)

        self.frame = ctk.CTkFrame(self)
        self.frame.configure(width=0, height=60)

        # Tkinter variable storing integer value
        if initial_state == 'expanded':
            self._label = self._collapse_text
            self._state_ind = 1
        elif initial_state == 'collapsed':
            self._label = self._expand_text
            self._state_ind = 0
        else:
            print(f'Invalid parameter value, {self._initial_state} passed for initial_state, whilst instantiating '
                  f'CBtCollapsiblePane.')
            raise InvalidParameterValue

        self._button = ctk.CTkButton(self,
                                     command=self._toggle,
                                     text=self._label,
                                     width=button_width)
        self._button.grid(row=0, column=0, sticky='w', padx=(2, 5))

        option_text = option_text.ljust(200, ' ')
        self._label = ctk.CTkLabel(master=self, text=option_text, anchor='w')
        self._label.grid(row=0, column=1, sticky='w')

        self._set_state()

        # This will call activate function of class

    def _set_state(self):
        if not self._state_ind:
            self._appearance_mode = ctk.get_appearance_mode()
            # As soon as button is pressed it removes this widget
            # but is not destroyed means can be displayed again
            self.frame.grid_forget()
            # This will change the text of the checkbutton
            self._button.configure(text=self._expand_text)
        elif self._state_ind:
            # increasing the frame area so new widgets
            # could reside in this container
            self.frame.grid(row=1,
                            column=0,
                            columnspan=2,
                            padx=self._frame_padx,
                            pady=self._frame_pady,
                            sticky='w')
            self._button.configure(text=self._collapse_text)

    def _toggle(self):
        if self._state_ind == 0:
            self._state_ind = 1
        else:
            self._state_ind = 0
        self._set_state()


class CBtkStatusBar(tk.Entry):
    """Create a status bar on the parent window. The status bar auto-fits the window width. Messages can be written
    to the status bar using the set_status_text method. The status_text_life can be used to auto-erase the status
    text after the specified number of seconds. The default value, 0, disables this feature. """

    def __init__(self,
                 master,
                 font=DEFAULT_FONT,
                 font_size=DEFAULT_FONT_SIZE,
                 status_text_life=0):
        super().__init__()

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
                                        text_font=(DEFAULT_FONT, HEADINGS_FONT_SIZE),
                                        fg_color=self._default_fg_color)
        # breadcrumb
        self._status_bar.grid(row=grid_rows + 1, column=0, padx=0, pady=0, columnspan=grid_columns, sticky='ew')
        self._master.update_idletasks()
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


class CBtkSlider:
    """CBtk slider class. Draws a customkinter slider, but includes a label."""

    def __init__(self, master,
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
        self._label_text = ctk.CTkLabel(master=master, text=" " * text_indent + label_text)
        self._label_text.grid(row=row, column=column, pady=0, padx=0, sticky="e")

        self._render_slider = ctk.CTkSlider(master=master,
                                            from_=from_,
                                            to=to,
                                            number_of_steps=number_of_steps,
                                            command=self.set_value_display)

        self._render_slider.grid(row=row, column=column + 1, columnspan=1, pady=10, padx=0, sticky="w")

        self._render_slider_value = ctk.CTkLabel(master=master,
                                                 text=value_format.format(initial_value))

        if tooltip:
            self.widget_tip = CBtkToolTip(self._render_slider, tooltip)

        self._render_slider_value.grid(row=row, column=column + 2, pady=0, padx=0, sticky="w")
        self._render_slider.set(initial_value)

    def set_value_display(self, value):
        self._render_slider_value.configure(text=self._format_mask.format(value))
        self._command(value)

    def set(self, value):
        self._render_slider.set(value)
        self.set_value_display(value=value)


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
        # self.root.columnconfigure(0, weight=1)
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


if __name__ == "__main__":
    my_app = CBTk(appearance_mode='Dark',
                  initial_frames=3,
                  frame_orientation='h',
                  # theme='green',
                  theme='blue',
                  adjustable_window=True,
                  add_submit=True,
                  add_cancel=True)
    my_app.title('Root (CBTk) Window')

    lbl_filter = ctk.CTkLabel(master=my_app.filter_frame, text='Filter Frame')
    lbl_filter.grid(row=0, column=0)

    lbl_entry = ctk.CTkLabel(master=my_app.entry_frame, text='Entry Frame')
    lbl_entry.grid(row=0, column=0)

    btn_cancel = my_app.btn_cancel
    btn_submit = my_app.btn_submit

    btn_cancel.grid(column=1)
    btn_submit.grid(column=5)

    btn_button = ctk.CTkLabel(master=my_app.button_frame, text='Button Frame')
    btn_button.grid(row=0, column=3)
    # btn_button.place(x=0)

    # Creating Object of Collapsible Pane Container
    # If we do not pass these strings i
    # parameter the default strings will appear
    # on button that were, expand >>, collapse <<
    pane1 = CBtkCollapsiblePane(my_app.entry_frame, option_text='Option Text', expand_text='+', collapse_text='-')
    pane1.grid(row=1, column=0)

    # Button and checkbutton, these will
    # appear in collapsible pane container
    # Button and checkbutton, these will
    # appear in collapsible pane container
    buttonA_text = ctk.CTkButton(pane1.frame, text="CTkButton").grid(
        row=1, column=1, pady=5, padx=5, sticky='w')

    buttonB_text = ctk.CTkCheckBox(pane1.frame, text="CTkCheckBox").grid(
        row=2, column=1, pady=5, sticky='w')

    entryA_text = ctk.CTkEntry(pane1.frame, text="CTkEntry", placeholder_text="CTkEntry Placeholder").grid(
        row=3, column=1, pady=5, sticky='w')

    pane2 = CBtkCollapsiblePane(my_app.entry_frame, option_text='Text Entry', expand_text='+', collapse_text='-')
    pane2.grid(row=2, column=0)

    textA = ctk.CTkTextbox(pane2.frame, width=300, height=90)
    textA.grid(row=1, column=1, pady=5, padx=5)

    answer = CBtkMessageBox(title='Confirm Delete',
                            message=f'Are you sure you wish to delete this extremely valuable skill?',
                            button1_text='Yes',
                            button2_text='No',
                            button3_text='Wob',
                            button4_text='Wib')
    print(f'Message box return: {answer.choice}')

    my_app.mainloop()
