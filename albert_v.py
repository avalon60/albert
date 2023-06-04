import albert_m as am
import os
import tkinter as tk
import cbtk_kit as ck
import re
from pathlib import Path
from PIL import ImageTk, Image
import customtkinter as ctk
from customtkinter import ThemeManager

DEBUG = False

# Initialise primary constants
prog = os.path.basename(__file__)


class AlbertGUIView(ck.CBTk):
    ALBERT_FONT = "Roboto Medium"
    DISPLAY_FIELDS_WIDTH = 120
    HEADINGS_FONT_SIZE = -14
    LABEL_FONT_SIZE = -12
    STATUS_BAR_FONT_SIZE = -11

    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.top_skill_setting = None
        self._controller = controller
        self._app_width = self._controller.APP_WIDTH
        self._app_height = self._controller.APP_HEIGHT
        self._text_to_speech = 'no'
        self.title('Albert')
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self._complete_root_entry_frame()
        self._complete_main_buttons_frame()
        self._render_avatar()
        self.create_menu()

    def _clear_contents(self):
        pass
        """ Clears out the contents of the question and answer entry widgets,
        """
        self.lbl_root_question.delete(0, tk.END)
        self.answer.textbox.config(state=tk.NORMAL)
        self.answer.textbox.delete(0.0, tk.END)
        self.answer.textbox.config(state=tk.DISABLED)
        self.lbl_root_question.focus_set()
        self._result = ''

    def _complete_root_entry_frame(self):
        """Complete the widget content, for the left hand-side of the root window.

        The root windows centre frame, actually appears as a left frame. However, this is because of the way the CBTk
        class operates, allowing a left and/or centre and/or right frame to be requested. We only request the centre
        and right frame in our app. """
        # configure grid layout (3x7)
        self.entry_frame.rowconfigure((0, 1, 2, 3), weight=1)
        self.entry_frame.rowconfigure(7, weight=10)
        self.entry_frame.columnconfigure((0, 1), weight=1)
        self.entry_frame.columnconfigure(2, weight=0)

        skill_info_text = self._controller.skill_info_text()

        self.lbl_root_skill_info = ctk.CTkLabel(self.entry_frame,
                                                text=skill_info_text,
                                                width=self.DISPLAY_FIELDS_WIDTH, height=10)

        self.lbl_root_skill_info.grid(row=0, column=0, padx=15, pady=(15, 0), sticky="ew")

        self.lbl_root_question = ctk.CTkEntry(master=self.entry_frame,
                                              width=self.DISPLAY_FIELDS_WIDTH,
                                              height=30,
                                              placeholder_text="Enter your request")
        self.lbl_root_question.grid(row=2, column=0, columnspan=2, pady=0, padx=10, sticky="ew")

        self.answer = ctk.CTkTextbox(master=self.entry_frame,
                                     relief='flat',
                                     wrap=tk.WORD,
                                     borderwidth=0,
                                     bd=0,
                                     height=450,
                                     width=1000)

        fg_color = "default_theme",
        text_color = "default_theme"
        self.answer.grid(row=3, column=0, sticky="nwe", padx=10, pady=10)
        self.fg_color = ThemeManager.theme["color"]["entry"] if fg_color == "default_theme" else fg_color
        self.text_color = ThemeManager.theme["color"]["text"] if text_color == "default_theme" else text_color
        self.answer.configure(state="disabled")

    def copy_to_skill_parameters(self):
        from_skill_name = self.combo_from_skill.get()
        to_skill_name = self.ent_copy_to_skill.get()
        to_file_name = self.ent_copy_to_file_name.get()
        copy_to_dict = {'from_skill_name': from_skill_name, 'to_skill_name': to_skill_name,
                        'to_prompt_file_name': to_file_name, 'to_info_file_name': to_file_name}
        return copy_to_dict

    def display_response(self, response_text):
        self.answer.configure(state=tk.NORMAL)
        self.answer.textbox.delete(0.0, tk.END)
        self.answer.insert(tk.END, response_text)
        self.answer.configure(state=tk.DISABLED)

    def launch_ai_key_entry(self):
        dialog = ctk.CTkInputDialog(master=self, text="Enter OpenAI API Key:", title="OpenAI Key")
        new_key = dialog.get_input()
        if new_key:
            self._controller.test_openai_key(new_key)
            #

    def launch_copy_skill(self):
        # self.win_settings.withdraw()

        skills_list = self._controller.skills_list()
        self.top_skill_copy = ck.CBTkToplevel(master=self,
                                              window_name='Copy Skill',
                                              window_width=750,
                                              window_height=200,
                                              add_status_bar=True,
                                              initial_frames=3,
                                              btn_cancel=True,
                                              btn_submit=True,
                                              modal=True)

        filter_frame = self.top_skill_copy.filter_frame
        entry_frame = self.top_skill_copy.entry_frame
        button_frame = self.top_skill_copy.button_frame

        self.top_skill_copy.grid_columnconfigure(0, weight=1)

        # Adjust the auto-buttons:
        btn_copy = self.top_skill_copy.btn_submit
        btn_cancel = self.top_skill_copy.btn_cancel
        btn_copy.grid(row=1, pady=(50, 0))
        btn_copy.configure(text='Copy', command=self._controller.copy_skill_config)
        btn_cancel.grid(row=2, pady=(10, 0))

        # self.top_skill_copy.btn_cancel.destroy()
        self.lbl_filler1 = ctk.CTkLabel(master=button_frame,
                                        text="")

        self.lbl_filler1.grid(row=0, column=0, pady=3, padx=0, sticky="w")

        val_copy_to_skill = self.top_skill_copy.register(self._controller.validate_copy_to_skill)
        val_copy_to_prompt = self.top_skill_copy.register(self._controller.validate_copy_to_prompt)

        self.lbl_skill = ctk.CTkLabel(master=filter_frame,
                                      text="Copy from:",
                                      justify="left",
                                      anchor='w',
                                      text_font=(AlbertGUIView.ALBERT_FONT, AlbertGUIView.HEADINGS_FONT_SIZE))

        self.lbl_skill.grid(row=0, column=0, pady=5, padx=0, sticky="n")

        self.combo_from_skill = ctk.CTkOptionMenu(master=filter_frame,
                                                  values=skills_list,
                                                  command=self._controller.set_copy_skill)
        self.combo_from_skill.grid(row=1, column=0, pady=0, padx=5, sticky="n")

        self.lbl_copy_to = ctk.CTkLabel(master=entry_frame,
                                        text="Copy to:",
                                        justify="left",
                                        anchor='w',
                                        text_font=(AlbertGUIView.ALBERT_FONT, AlbertGUIView.HEADINGS_FONT_SIZE))

        self.lbl_copy_to.grid(row=0, column=0, pady=(5, 0), padx=0, sticky="w")

        self.ent_copy_to_skill = ctk.CTkEntry(master=entry_frame,
                                              width=250,
                                              corner_radius=3,
                                              placeholder_text="New skill name")
        self.ent_copy_to_skill.grid(row=1, column=0, columnspan=1, pady=(5, 10), padx=10, sticky="nsw")
        tip_copy_to_skill = ck.CBtkToolTip(self.ent_copy_to_skill, 'Enter the new skill name.')

        # self.ent_skill_copy_to_skill.config(validate="focusout", validatecommand=(val_copy_to_skill, '%P'))

        self.ent_copy_to_file_name = ctk.CTkEntry(master=entry_frame,
                                                  width=250,
                                                  # height=30,
                                                  corner_radius=3,
                                                  placeholder_text="Prompt/Info files name prefix")
        self.ent_copy_to_file_name.grid(row=2, column=0, columnspan=1, pady=10, padx=10, sticky="nsw")
        tip_copy_to_prompt_file = ck.CBtkToolTip(self.ent_copy_to_file_name, 'Enter the info file name prefix.')

        # self.ent_skill_copy_to_prompt.config(validate="key", validatecommand=(val_copy_to_prompt, '%P'))

        # self.btn_skill_save_settings.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        self.ent_copy_to_skill.focus_set()
        # self.top_skill_copy.wait_visibility()

    def launch_skill_modify(self, status_text_life):
        """Launch the GPT skill settings / adjustment dialog."""

        skills_list = self._controller.editable_skills()
        self.top_skill_mod = ck.CBTkToplevel(master=self,
                                             window_name='Modify Skills',
                                             window_width=900,
                                             window_height=250,
                                             initial_frames=3,
                                             frame_orientation='v',
                                             adjustable_window=True,
                                             modal=False,
                                             add_submit=False,
                                             add_edit=True,
                                             add_delete=True,
                                             add_cancel=True,
                                             pady=(5, 0),
                                             padx=(5,),
                                             cursor='arrow',
                                             status_text_life=status_text_life)

        #                        W      x      H
        mod_entry_frame = self.top_skill_mod.entry_frame
        mod_filter_frame = self.top_skill_mod.filter_frame

        self.lbl_mod_skill = ctk.CTkLabel(master=mod_filter_frame,
                                          text="Select AI Skill:",
                                          justify="left",
                                          anchor='w',
                                          text_font=(AlbertGUIView.ALBERT_FONT, AlbertGUIView.HEADINGS_FONT_SIZE))
        self.lbl_mod_skill.grid(row=0, column=0, pady=0, padx=(50, 5))

        self.opm_mod_skill = ctk.CTkOptionMenu(master=mod_filter_frame,
                                               values=skills_list,
                                               command=self._controller.set_mod_skill)

        self.opm_mod_skill.grid(row=1, column=0, pady=0, padx=(5, 0))

        frm_mod_info_pane = ck.CBtkCollapsiblePane(mod_entry_frame, option_text='Skill Synopsis',
                                                  initial_state='expanded')
        frm_mod_info_pane.grid(row=0, column=0)

        skill_info_text = self._controller.skill_info_text(skill_text_width=80)
        self.txt_mod_skill_info = ctk.CTkTextbox(frm_mod_info_pane.frame,
                                                 width=500, height=100)
        ck.set_entry(self.txt_mod_skill_info, text=skill_info_text)

        self.txt_mod_skill_info.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        btn_cancel = self.top_skill_mod.btn_cancel
        btn_edit = self.top_skill_mod.btn_edit
        btn_delete = self.top_skill_mod.btn_delete

        btn_edit.grid(pady=(10, 10))
        # btn_delete.grid(padx=(60, 20))
        btn_cancel.grid(row=4, pady=(95, 10))

        btn_delete.configure(command=self._controller.delete_skill)
        btn_edit.configure(command=lambda: self._controller.launch_skill_editor(mode='edit',
                                                                                skill=self.opm_mod_skill.get()))

        # btn_cancel.grid(row=0, column=0, padx=(10, 0), pady=10)
        # btn_delete.grid(row=0, column=5, padx=(100, 100), pady=10)
        # btn_edit.grid(row=0, column=6, pady=10)

    def launch_skill_editor(self, status_text_life, skill='', mode='edit'):
        """Launch the skill editor adjustment dialog.

        :param status_text_life:
        :param skill: The skill to be edited. If empty string, we assume the currently
        selected.
        :param mode: String describing how the toplevel frame should function.

        Values for "mode", are as follows: "edit" - edit an existing; "create" - create a new skill from scratch;
        "settings" - only present the GTP ( slider) settings.
        """

        if mode == 'create':
            window_name = 'Create Skill'
        elif mode == 'edit':
            window_name = 'Modify Skill'
        else:
            window_name = 'GPT Skill Settings'
        print(f'v.launch_skill_editor: skill={skill}; mode={mode}')
        self.top_skill_editor = ck.CBTkToplevel(master=self,
                                                window_name=window_name,
                                                window_width=1200,
                                                window_height=400,
                                                initial_frames=3,
                                                frame_orientation='v',
                                                adjustable_window=True,
                                                add_submit=True,
                                                add_cancel=True,
                                                pady=(5, 0),
                                                padx=(5,),
                                                cursor='arrow',
                                                status_text_life=status_text_life)

        #                        W      x      H
        # self.top_skill_editor.geometry("670" + "x" + "340")

        self.top_skill_editor.grid_columnconfigure(0, weight=3)
        self.top_skill_editor.grid_columnconfigure(0, weight=1)

        self.frm_kill_settings_top = self.top_skill_editor.entry_frame

        self.btn_reset_settings = ctk.CTkButton(master=self.top_skill_editor.button_frame,
                                                text="Reset",
                                                border_width=2,
                                                fg_color=None,
                                                command=self._controller.reset_skill_settings)

        self.btn_apply_settings = ctk.CTkButton(master=self.top_skill_editor.button_frame,
                                                text="Apply",
                                                border_width=2,
                                                fg_color=None,
                                                command=self._controller.apply_slider_settings)

        screen_width = self.top_skill_editor.winfo_width()
        screen_height = self.top_skill_editor.winfo_height()

        self.top_skill_editor.btn_submit.configure(text='Save', command=self._controller.save_gtp_settings)
        self.top_skill_editor.btn_cancel.configure(command=self._controller.rollback_skill_settings)

        # Button tooltips.
        cancel_tooltip = ck.CBtkToolTip(self.top_skill_editor.btn_submit, 'Save (and persist) GPT slider settings.')
        reset_tooltip = ck.CBtkToolTip(self.btn_reset_settings, 'Reset the slider settings, to their original state.')

        # self.top_skill_editor.btn_cancel.grid(row=9, column=4, pady=10, padx=10, sticky="w")
        # self.btn_reset_settings.grid(row=9, column=6, padx=(10, 10), pady=10)
        # self.btn_apply_settings.grid(row=9, column=8, padx=(10, 10), pady=10)
        # self.top_skill_editor.btn_submit.grid(row=9, column=10, pady=10, padx=10, sticky="e")

        # self.top_skill_editor.wait_visibility()
        self.top_skill_editor.grab_set()

        # breadcrumb red
        self.label_gpt_settings = ctk.CTkLabel(master=self.frm_kill_settings_top,
                                               text=f"GPT Settings for:  {self._controller.active_skill()}",
                                               fg_="green",
                                               # fg_color='red',
                                               justify="center",
                                               text_font=(AlbertGUIView.ALBERT_FONT, AlbertGUIView.LABEL_FONT_SIZE))

        self.label_gpt_settings.grid(row=0, column=0, pady=10, padx=10, sticky="e")

        tooltip = "Controls randomness: Lowering results in less random completions. As " \
                  "the temperature approached zero, the model will become more " \
                  "deterministic and repetitive."
        self._temperature_slider = ck.CBtkSlider(master=self.frm_kill_settings_top,
                                                 label_text='Temperature',
                                                 row=3,
                                                 column=0,
                                                 from_=0,
                                                 to=1,
                                                 number_of_steps=100,
                                                 initial_value=self._controller.gpt_temperature(),
                                                 value_format="{:.3f}",
                                                 command=self._controller.set_temperature,
                                                 tooltip=tooltip,
                                                 text_indent=20)
        tooltip = "The maximum number of tokens to generate. Requests can use up to 2,048 or " \
                  "4,000 tokens, shared between prompt and completion. The exact limit varies by " \
                  "model. (One token is roughly 4 characters of English text)"

        self._max_tokens_slider = ck.CBtkSlider(master=self.frm_kill_settings_top,
                                                label_text='Max Length (Tokens)',
                                                row=4,
                                                column=0,
                                                from_=1,
                                                to=4000,
                                                number_of_steps=100,
                                                initial_value=self._controller.max_tokens(),
                                                value_format="{:.0f}",
                                                command=self._controller.set_max_tokens,
                                                tooltip=tooltip,
                                                text_indent=10)

        tooltip = "Controls diversity via nucleus sampling: " \
                  "0.5 means half of all likelihood - weighted options are considered."
        self._top_p_slider = ck.CBtkSlider(master=self.frm_kill_settings_top,
                                           label_text='Top P',
                                           row=5,
                                           column=0,
                                           from_=0,
                                           to=1,
                                           number_of_steps=100,
                                           initial_value=self._controller.top_p(),
                                           value_format="{:.3f}",
                                           command=self._controller.set_top_p,
                                           tooltip=tooltip,
                                           text_indent=30)

        tooltip = "How much to penalise new tokens based on their existing frequency " \
                  "in the text so far. Decreases the model's likelihood to repeat the " \
                  "same line verbatim."

        self._frequency_slider = ck.CBtkSlider(master=self.frm_kill_settings_top,
                                               label_text='Frequency penalty',
                                               row=9,
                                               column=0,
                                               from_=0,
                                               to=2,
                                               number_of_steps=100,
                                               initial_value=self._controller.frequency_penalty(),
                                               value_format="{:.3f}",
                                               command=self._controller.set_frequency_penalty,
                                               tooltip=tooltip,
                                               text_indent=10)

        tooltip = "How much to penalise new tokens depending on whether they appear " \
                  "in the text so far. Increase the model's likelihood to talk about " \
                  "new topics."

        self._presence_slider = ck.CBtkSlider(master=self.frm_kill_settings_top,
                                              label_text='Presence penalty',
                                              row=11,
                                              column=0,
                                              from_=0,
                                              to=2,
                                              number_of_steps=100,
                                              initial_value=self._controller.presence_penalty(),
                                              value_format="{:.3f}",
                                              command=self._controller.set_presence_penalty,
                                              tooltip=tooltip,
                                              text_indent=10)

        tooltip = "USE WITH CAUTION!\nGenerates multiple completions server-side, and displays only the " \
                  "best. Streaming only works when set to 1. Since it acts as a  " \
                  "multiplier on the number of completions, this parameter can eat " \
                  "into your token quota very quickly."

        self._best_of_slider = ck.CBtkSlider(master=self.frm_kill_settings_top,
                                             label_text='Best of',
                                             row=12,
                                             column=0,
                                             from_=1,
                                             to=20,
                                             number_of_steps=20,
                                             initial_value=self._controller.best_of(),
                                             value_format="{:.0f}",
                                             command=self._controller.set_best_of,
                                             tooltip=tooltip,
                                             text_indent=30)

    def launch_skill_settings(self, status_text_life):
        """Launch the GPT skill settings / adjustment dialog."""
        self.top_skill_setting = ck.CBTkToplevel(master=self,
                                                 window_name='Skill GPT Settings',
                                                 window_width=660,
                                                 window_height=380,
                                                 initial_frames=2,
                                                 frame_orientation='h',
                                                 adjustable_window=False,
                                                 add_submit=True,
                                                 add_cancel=True,
                                                 pady=(5, 0),
                                                 padx=(5,),
                                                 cursor='arrow',

                                                 status_text_life=status_text_life)

        #                        W      x      H
        # self.top_skill_setting.geometry("670" + "x" + "340")

        self.top_skill_setting.grid_columnconfigure(0, weight=3)
        self.top_skill_setting.grid_columnconfigure(0, weight=1)

        self.frm_kill_settings_top = self.top_skill_setting.entry_frame

        self.btn_reset_settings = ctk.CTkButton(master=self.top_skill_setting.button_frame,
                                                text="Reset",
                                                border_width=2,
                                                fg_color=None,
                                                command=self._controller.reset_skill_settings)

        self.btn_apply_settings = ctk.CTkButton(master=self.top_skill_setting.button_frame,
                                                text="Apply",
                                                border_width=2,
                                                fg_color=None,
                                                command=self._controller.apply_slider_settings)

        screen_width = self.top_skill_setting.winfo_width()
        screen_height = self.top_skill_setting.winfo_height()

        self.top_skill_setting.btn_submit.configure(text='Save', command=self._controller.save_gtp_settings)
        self.top_skill_setting.btn_cancel.configure(command=self._controller.rollback_skill_settings)

        # Button tooltips.
        cancel_tooltip = ck.CBtkToolTip(self.top_skill_setting.btn_submit, 'Save (and persist) GPT slider settings.')
        reset_tooltip = ck.CBtkToolTip(self.btn_reset_settings, 'Reset the slider settings, to their original state.')

        self.top_skill_setting.btn_cancel.grid(row=9, column=4, pady=10, padx=10, sticky="w")
        self.btn_reset_settings.grid(row=9, column=6, padx=(10, 10), pady=10)
        self.btn_apply_settings.grid(row=9, column=8, padx=(10, 10), pady=10)
        self.top_skill_setting.btn_submit.grid(row=9, column=10, pady=10, padx=10, sticky="e")

        # self.top_skill_setting.wait_visibility()
        self.top_skill_setting.grab_set()
        self.top_skill_setting.title("GPT Skill Settings")

        self._icon_file = self._controller.global_property_value(config_key='icon_file')
        self.top_skill_setting.iconbitmap(bitmap="@" + str(self._icon_file))
        # breadcrumb red
        self.label_gpt_settings = ctk.CTkLabel(master=self.frm_kill_settings_top,
                                               text=f"GPT Settings for:  {self._controller.active_skill()}",
                                               fg_="green",
                                               # fg_color='red',
                                               justify="center",
                                               text_font=(AlbertGUIView.ALBERT_FONT, AlbertGUIView.LABEL_FONT_SIZE))

        self.label_gpt_settings.grid(row=0, column=0, pady=10, padx=10, sticky="e")

        tooltip = "Controls randomness: Lowering results in less random completions. As " \
                  "the temperature approached zero, the model will become more " \
                  "deterministic and repetitive."
        self._temperature_slider = ck.CBtkSlider(master=self.frm_kill_settings_top,
                                                 label_text='Temperature',
                                                 row=3,
                                                 column=0,
                                                 from_=0,
                                                 to=1,
                                                 number_of_steps=100,
                                                 initial_value=self._controller.gpt_temperature(),
                                                 value_format="{:.3f}",
                                                 command=self._controller.set_temperature,
                                                 tooltip=tooltip,
                                                 text_indent=20)
        tooltip = "The maximum number of tokens to generate. Requests can use up to 2,048 or " \
                  "4,000 tokens, shared between prompt and completion. The exact limit varies by " \
                  "model. (One token is roughly 4 characters of English text)"

        self._max_tokens_slider = ck.CBtkSlider(master=self.frm_kill_settings_top,
                                                label_text='Max Length (Tokens)',
                                                row=4,
                                                column=0,
                                                from_=1,
                                                to=4000,
                                                number_of_steps=100,
                                                initial_value=self._controller.max_tokens(),
                                                value_format="{:.0f}",
                                                command=self._controller.set_max_tokens,
                                                tooltip=tooltip,
                                                text_indent=10)

        tooltip = "Controls diversity via nucleus sampling: " \
                  "0.5 means half of all likelihood - weighted options are considered."
        self._top_p_slider = ck.CBtkSlider(master=self.frm_kill_settings_top,
                                           label_text='Top P',
                                           row=5,
                                           column=0,
                                           from_=0,
                                           to=1,
                                           number_of_steps=100,
                                           initial_value=self._controller.top_p(),
                                           value_format="{:.3f}",
                                           command=self._controller.set_top_p,
                                           tooltip=tooltip,
                                           text_indent=30)

        tooltip = "How much to penalise new tokens based on their existing frequency " \
                  "in the text so far. Decreases the model's likelihood to repeat the " \
                  "same line verbatim."

        self._frequency_slider = ck.CBtkSlider(master=self.frm_kill_settings_top,
                                               label_text='Frequency penalty',
                                               row=9,
                                               column=0,
                                               from_=0,
                                               to=2,
                                               number_of_steps=100,
                                               initial_value=self._controller.frequency_penalty(),
                                               value_format="{:.3f}",
                                               command=self._controller.set_frequency_penalty,
                                               tooltip=tooltip,
                                               text_indent=10)

        tooltip = "How much to penalise new tokens depending on whether they appear " \
                  "in the text so far. Increase the model's likelihood to talk about " \
                  "new topics."

        self._presence_slider = ck.CBtkSlider(master=self.frm_kill_settings_top,
                                              label_text='Presence penalty',
                                              row=11,
                                              column=0,
                                              from_=0,
                                              to=2,
                                              number_of_steps=100,
                                              initial_value=self._controller.presence_penalty(),
                                              value_format="{:.3f}",
                                              command=self._controller.set_presence_penalty,
                                              tooltip=tooltip,
                                              text_indent=10)

        tooltip = "USE WITH CAUTION!\nGenerates multiple completions server-side, and displays only the " \
                  "best. Streaming only works when set to 1. Since it acts as a  " \
                  "multiplier on the number of completions, this parameter can eat " \
                  "into your token quota very quickly."

        self._best_of_slider = ck.CBtkSlider(master=self.frm_kill_settings_top,
                                             label_text='Best of',
                                             row=12,
                                             column=0,
                                             from_=1,
                                             to=20,
                                             number_of_steps=20,
                                             initial_value=self._controller.best_of(),
                                             value_format="{:.0f}",
                                             command=self._controller.set_best_of,
                                             tooltip=tooltip,
                                             text_indent=30)

    def disable_settings_save(self):
        """For any skills distributed with Albert, we want to disable the saving of the config file."""
        self.top_skill_setting.btn_submit.configure(state=tk.DISABLED)
        cancel_tooltip = ck.CBtkToolTip(self.top_skill_setting.btn_submit, 'Save disabled for standard skills.')

    def enable_settings_save(self):
        """Saving (persistent save) of GPT settings, may have been disabled, if the currently selected skill is one
        distributed with Albert. If a non protected skill is selected (created by the user) we want to re-enable the
        Save button."""
        self.top_skill_setting.btn_submit.configure(state=tk.NORMAL)
        cancel_tooltip = ck.CBtkToolTip(self.top_skill_setting.btn_submit, 'Save (and persist) GPT slider settings.')

    def kill_and_reset_skill_settings(self):
        self.destroy()

    def create_menu(self):
        # Set up the core of our menu
        albert_menu = tk.Menu(self)
        foreground = ck.get_color_from_name('text')
        background = ck.get_color_from_name('frame_low')
        albert_menu.config(background=background, foreground=foreground)
        self.config(menu=albert_menu)

        # Now add a File sub-menu option
        file_menu = tk.Menu(albert_menu)
        file_menu.config(background=background, foreground=foreground)
        albert_menu.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='Quit', command=self.quit)

        # Now add a Tools sub-menu option
        skills_menu = tk.Menu(albert_menu)
        skills_menu.config(background=background, foreground=foreground)
        albert_menu.add_cascade(label='Tools', menu=skills_menu)
        skills_menu.add_command(label='Copy Skill', command=self._controller.launch_copy_skill)
        skills_menu.add_command(label='Modify Skills', command=self._controller.launch_skill_modify)
        skills_menu.add_command(label='Update AI Key', command=self._controller.launch_ai_key_entry)

    def main(self):
        self.mainloop()

    def _render_avatar(self):
        self._avatar_image = self._controller.global_property_value(config_key='avatar_file')
        self.avatar = Image.open(self._avatar_image)
        self.avatar = self.avatar.resize((130, 130))
        # self.einstein = tk.PhotoImage(file=self._avatar_image)
        self.avatar = ImageTk.PhotoImage(self.avatar)
        self.label_avatar = ctk.CTkLabel(self.button_frame, image=self.avatar, width=50, height=50)
        self.label_avatar.grid(row=0, column=0, padx=15, pady=15, sticky="w")

    def _complete_main_buttons_frame(self):
        # Adjust our Submit button. Normally this is
        # placed on row 0 when added automatically by
        # CBTkApp, but Albert is sitting there.

        # Adjust the submit button, which was auto-created for root window, upon request.
        self.btn_submit.configure(command=self._controller.submit_gpt_question)
        self.btn_submit.grid(row=1, pady=10, padx=20)

        skills_list = self._controller.skills_list()
        widget_parent = self.button_frame
        tooltip = 'Copy answer text to clipboard.'
        self.btn_copy = ctk.CTkButton(master=widget_parent,
                                      text="Copy",
                                      border_width=2,
                                      fg_color=None,
                                      command=self._controller.copy_answer_to_clipboard)
        self.btn_copy.grid(row=3, column=0, pady=10, padx=20)
        self.copy_tooltip = ck.CBtkToolTip(self.btn_copy, tooltip)

        self.btn_clear = ctk.CTkButton(master=widget_parent,
                                       text="Clear",
                                       border_width=2,
                                       fg_color=None,
                                       command=self._clear_contents)

        self.btn_clear.grid(row=4, column=0, pady=10, padx=20)

        self.switch_text_to_speech = ctk.CTkSwitch(master=widget_parent,
                                                   onvalue='yes',
                                                   offvalue='no',
                                                   command=self._controller.update_text_to_speech_status,
                                                   text="Text to Speech")
        switch_var = tk.StringVar()
        self.switch_text_to_speech.grid(row=8, column=0, columnspan=2, pady=25, padx=0, sticky="n")
        # Get the text-to-speech setting (enabled or disabled) for our currently selected skill.
        self._switch_text_to_speech = self._controller.skill_property_value(skill_key='text_to_speech')

        self.text_to_speech_tip = ck.CBtkToolTip(self.switch_text_to_speech,
                                                 "Controls text to speech. When switched to on, in addition to the  "
                                                 "response being displayed, Albert also relays the test, to be "
                                                 "processed via text-to-speech. This option requires that you have"
                                                 " Festival text-to-speech installed.")

        self.lbl_mode = ctk.CTkLabel(master=widget_parent,
                                     text="AI Skill:",
                                     justify="left",
                                     anchor='w',
                                     text_font=(AlbertGUIView.ALBERT_FONT, AlbertGUIView.HEADINGS_FONT_SIZE))
        self.lbl_mode.grid(row=9, column=0, pady=0, padx=0, sticky="n")


        self.opm_skill_combo = ctk.CTkOptionMenu(master=widget_parent,
                                                 values=skills_list,
                                                 command=self._set_skill)


        self.opm_skill_combo.grid(row=10, column=0, pady=0, padx=0, sticky="n")
        # self.combo_mode.set(self._prompt_mode)

        self.label_filler = ctk.CTkLabel(master=widget_parent,
                                         text="",
                                         justify="left")

        self.label_filler.grid(row=11, column=0, pady=0, padx=0, sticky="n")

        self.settings = ctk.CTkButton(master=widget_parent,
                                      text="Skill Settings",
                                      border_width=2,
                                      fg_color=None,
                                      command=self._controller.launch_skill_settings)

        self.settings.grid(row=14, column=0, pady=15, padx=20, sticky="s")

        self.btn_cancel.configure(text='Quit')
        self.btn_cancel.grid(row=15, column=0, pady=15, padx=5, sticky="s")

    def set_text_to_speech_widget(self, enabled):
        if enabled == 'yes':
            self.switch_text_to_speech.select()
        else:
            self.switch_text_to_speech.deselect()

    def set_skill_display(self, skill):
        self.opm_skill_combo.set(skill)

    def get_text_to_speech_widget(self):
        return self.switch_text_to_speech.get()

    def set_mod_skill_info(self, skill_info_text):
        self.lbl_mod_skill_info.configure(text=skill_info_text)
        self.update_idletasks()

    def set_lbl_root_skill_info(self, skill_info_text):
        self.lbl_root_skill_info.configure(text=skill_info_text)
        self.update_idletasks()

    def save_skill_settings(self):
        pass

    def apply_skill_settings(self):
        pass

    @staticmethod
    def messagebox(
            title='CBtkMessageBox',
            msg='',
            btn1_text='OK',
            btn2_text='',
            btn3_text='',
            btn4_text=''):
        response = ck.CBtkMessageBox(title=title,
                                     message=msg,
                                     button1_text=btn1_text,
                                     button2_text=btn2_text,
                                     button3_text=btn3_text,
                                     button4_text=btn4_text)
        return response.choice

    def set_temperature_slider(self, value):
        self._temperature_slider.set(value)

    def set_max_tokens_slider(self, value):
        self._max_tokens_slider.set(value=value)

    def set_top_p_slider(self, value):
        self._top_p_slider.set(value)

    def set_frequency_slider(self, value):
        self._frequency_slider.set(value)

    def set_presence_slider(self, value):
        self._presence_slider.set(value)

    def set_best_of_slider(self, value):
        self._best_of_slider.set(value)

    def _set_skill(self, skill):
        self._controller.set_root_skill(skill)

    def update_text_to_speech(self):
        self._text_to_speech = self.switch_text_to_speech.get()
        return self._text_to_speech


if __name__ == "__main__":
    from pathlib import Path
    import os
    import albert_c as ac

    home_dir = Path(os.getenv("HOME"))
    albert_home = home_dir / "albert"
    app_images = albert_home / 'images'
    app_configs = albert_home / 'config'
    prompt_files = albert_home / 'prompt_files'
    config_ini = app_configs / 'albert.ini'
    skill_selection = 'O/S Commands'
    albert_controller = ac.AlbertController(app_home=albert_home, initial_skill=skill_selection)
