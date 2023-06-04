from argparse import HelpFormatter
import tkinter as tk
from customtkinter import theme_manager
from operator import attrgetter
from pathlib import Path
import albert_m as am
import albert_v as av
import argparse
import os
import sys

DEBUG = False
STATUS_MESSAGE_TIMEOUT = 10

# Initialise primary constants
prog = os.path.basename(__file__)
home_dir = os.getenv("HOME")

headings_font_size = -14
status_bar_font_size = -12

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
ap.add_argument("-a", '--set-appearance', required=False, action="store",
                help="Overrides the default appearance "
                     "(dark). Valid options are: 'dark', 'light', "
                     "and 'system'. System only has any effect on"
                     "MacOS.",
                dest='appearance_mode', default='dark')

ap.add_argument("-s", '--skill-mode', required=False, action="store",
                help="Override the starting skill. "
                     "You can switch to a different skill "
                     "inside the application UI. "
                     "This overrides the application's default.",
                default='General Knowledge',
                dest='skill_selection')
ap.add_argument("-t", '--set-theme', required=False, action="store",
                help="Overrides the default appearance "
                     "(green). Valid options are: 'green', "
                     " 'blue',and 'dark-blue'.",
                dest='theme', default='oceanix')

ap.add_argument("-H", '--albert-home', required=False, default=home_dir + '/albert',
                action="store",
                help="The pathname to the initialisation file. The default "
                     "location is $HOME/albert/config/albert.ini.",
                dest='albert_home')

args_list = vars(ap.parse_args())
skill_selection = args_list["skill_selection"]
albert_home = Path(args_list["albert_home"])
app_images = albert_home / 'images'
app_configs = albert_home / 'config'
prompt_files = albert_home / 'prompt_files'
config_ini = app_configs / 'albert.ini'
appearance_mode = args_list["appearance_mode"]
theme = args_list["theme"]

if appearance_mode not in ['dark', 'light', 'system']:
    print(f"Error: Invalid appearance setting, '{appearance_mode}', valid options are  'dark', 'light' or 'system'.")
    print('Bailing out!')
    exit(1)

valid_themes_list = theme_manager.ThemeManager().built_in_themes
valid_themes_list.append('oceanix')
valid_themes = ', '.join(e for e in valid_themes_list)
valid_themes = valid_themes

if theme not in valid_themes_list:
    print(f"Error: Invalid theme setting, valid themes are:  {valid_themes}")
    print('Bailing out!')
    exit(1)


class AlbertController:
    APP_WIDTH = 1120
    APP_HEIGHT = 660

    def __init__(self, app_home, initial_skill):
        self._home_dir = os.getenv("HOME")
        self._selected_skill = initial_skill
        self._albert_model = am.AlbertModel(app_home, initial_skill='O/S Commands')
        self._albert_view = av.AlbertGUIView(controller=self,
                                             window_height=AlbertController.APP_HEIGHT,
                                             window_width=AlbertController.APP_WIDTH,
                                             appearance_mode=appearance_mode,
                                             theme=theme,
                                             add_status_bar=True,
                                             initial_frames=2,
                                             add_submit=True,
                                             add_cancel=True,
                                             adjustable_window=False,
                                             status_text_life=STATUS_MESSAGE_TIMEOUT)

        self._icon_file = self.global_property_value(config_key='icon_file')
        self._albert_view.iconbitmap(bitmap="@" + str(self._icon_file))
        self._skill_info_text = None

        self._albert_view.set_skill_display(skill=initial_skill)

        # The mainloop included in main() - no code past this point, in this method.
        self._albert_view.main()

    def copy_answer_to_clipboard(self):
        self._albert_model.copy_answer_to_clipboard()

    def launch_skill_editor(self, skill='', mode='edit'):
        print(f'c.launch_skill_editor: skill={skill}; mode={mode}')
        self._albert_view.launch_skill_editor(status_text_life=STATUS_MESSAGE_TIMEOUT, skill=skill, mode=mode)

    def copy_skill_config(self):

        copy_to_dict = self._albert_view.copy_to_skill_parameters()
        from_skill_name = copy_to_dict['from_skill_name']
        to_skill_name = copy_to_dict['to_skill_name']
        to_prompt_file_name = copy_to_dict['to_prompt_file_name']
        to_info_file_name = copy_to_dict['to_info_file_name']
        result = self._albert_model.copy_skill_config(from_skill_name=from_skill_name,
                                                      to_skill_name=to_skill_name,
                                                      to_prompt_file_name=to_prompt_file_name,
                                                      to_info_file_name=to_info_file_name)
        self._albert_view.top_skill_copy.set_status_text(result)

        skills_list = self._albert_model.skills_list()
        self._albert_view.opm_skill_combo.configure(values=skills_list)

    def skill_property_value(self, skill_key: str):
        """Leverage the model view to obtain a skill property value"""
        property_val = self._albert_model.skill_property_value(skill_key=skill_key)
        return property_val

    def global_property_value(self, config_key: str):
        # Use our model class to obtain a configuration property value.
        property_val = self._albert_model.config_property_value(config_section='global', config_key=config_key)
        return property_val

    def apply_slider_settings(self):
        """Allow the selected slider settings to be used for the session."""
        # The slider settings dynamically adjust our session GTP settings related to the sliders, so to apply the
        # settings (session only) we need only close (destroy) the settings window.
        # self._albert_view.top_skill_setting.close_window()
        self._albert_view.set_status_text(f'Settings for skill, "{self._albert_model.active_skill()}", have been '
                                          f'adjusted for this session, or until a new skill is selected.')

    def launch_copy_skill(self):
        self._albert_view.launch_copy_skill()

    def launch_skill_modify(self):
        self._albert_view.launch_skill_modify(status_text_life=STATUS_MESSAGE_TIMEOUT)
        skills_list = self.editable_skills()
        if self._albert_model.is_locked_skill(skills_list[0]):
            self._albert_view.top_skill_mod.btn_edit.configure(state=tk.DISABLED)
            self._albert_view.top_skill_mod.btn_delete.configure(state=tk.DISABLED)
            self._albert_view.top_skill_mod.set_status_text(f'The current skill selection, "{skills_list[0]}", is '
                                                            f'protected, and so cannot be modified or deleted.')

    def editable_skills(self):
        return self._albert_model.editable_skills()

    def launch_skill_settings(self):
        """Launch the GPT skill settings / adjustment dialog."""
        self._albert_model.take_config_savepoint()
        self._albert_view.launch_skill_settings(status_text_life=STATUS_MESSAGE_TIMEOUT)
        if self._albert_model.is_locked_skill():
            self._albert_view.disable_settings_save()
            self._albert_view.top_skill_setting.set_status_text(
                f'Modifications to this skill, cannot be made permanent. "Save" is '
                f'disabled.')

    def launch_ai_key_entry(self):
        self._albert_view.launch_ai_key_entry()

    def skill_info_text(self, skill='', skill_text_width=120):
        """Provide the skill info text to be displayed at the top of the root window."""
        return self._albert_model.skill_info_text(skill=skill, skill_text_width=skill_text_width)

    def active_skill(self):
        return self._albert_model.active_skill()

    def set_mod_skill(self, skill):
        """The set_mod_skill method, updates the Skills Modification window, when an AI Skill is selected from the
        combo box at the top of the screen."""
        filter_frame = self._albert_view.top_skill_mod.filter_frame

        # Determine whether ths skill selection is protected (locked). If so disable the buttons which would do harm.
        # On the other hand, if the skill selection is not locked, then ensure that the widgets are enabled.
        skill = self._albert_view.opm_mod_skill.get()
        if self._albert_model.is_locked_skill(skill):
            self._albert_view.top_skill_mod.btn_edit.configure(state=tk.DISABLED)
            self._albert_view.top_skill_mod.btn_delete.configure(state=tk.DISABLED)
            self._albert_view.top_skill_mod.set_status_text(f'The current skill selection, "{skill}", is '
                                                            f'protected, and so cannot be modified or deleted.')
        else:
            self._albert_view.top_skill_mod.btn_edit.configure(state=tk.NORMAL)
            self._albert_view.top_skill_mod.btn_delete.configure(state=tk.NORMAL)

        skills_list = self._albert_model.skills_list()
        self._skill_info_text = self._albert_model.skill_info_text(skill=skill, skill_text_width=80)
        self._albert_view.set_mod_skill_info(self._skill_info_text)

    def set_copy_skill(self, skill):
        self.copy_from_skill = skill

    def set_root_skill(self, skill):
        """The set_mod_skill method, updates the main window, when an AI Skill is selected from the
        combo box on the right hand side panel. """
        self._albert_model.switch_skill(new_skill=skill)
        self._skill_info_text = self._albert_model.skill_info_text()
        self._albert_view.set_lbl_root_skill_info(self._skill_info_text)

    def delete_skill(self):
        #  TODO: Add a confirmation message box!
        skill = self._albert_view.opm_mod_skill.get()
        choice = self._albert_view.messagebox(title='Confirm Delete',
                                              msg=f'Are you sure you wish to delete the, "{skill}", skill?',
                                              btn1_text='Yes',
                                              btn2_text='No')

        if int(choice) == 2:
            return

        self._albert_model.delete_skill(skill)
        skills_list = self._albert_model.skills_list()
        next_skill_in_list = skills_list[0]
        skill = tk.StringVar(self._albert_view.opm_mod_skill, next_skill_in_list)
        self._albert_view.opm_mod_skill.configure(values=skills_list, variable=skill)
        self._albert_view.opm_skill_combo.configure(values=skills_list, variable=skill)
        if self._albert_model.is_locked_skill(next_skill_in_list):
            self._albert_view.top_skill_mod.btn_edit.configure(state=tk.DISABLED)
            self._albert_view.top_skill_mod.btn_delete.configure(state=tk.DISABLED)
            self._albert_view.top_skill_mod.set_status_text(f'The current skill selection, "{skill}", is '
                                                            f'protected, and so cannot be modified or deleted.')
        else:
            self._albert_view.top_skill_mod.btn_edit.configure(state=tk.NORMAL)
            self._albert_view.top_skill_mod.btn_delete.configure(state=tk.NORMAL)

        self._albert_view.opm_mod_skill.update_idletasks()

    def skills_list(self):
        return self._albert_model.skills_list()

    def frequency_penalty(self):
        return self._albert_model.skill_property_value('frequency_penalty')

    def gpt_engine(self):
        return self._albert_model.skill_property_value('gpt_engine')

    def gpt_temperature(self):
        return self._albert_model.skill_property_value('gpt_temperature')

    def max_tokens(self):
        return self._albert_model.skill_property_value('max_tokens')

    def presence_penalty(self):
        return self._albert_model.skill_property_value('presence_penalty')

    def text_to_speech(self):
        return self._albert_model.skill_property_value('text_to_speech')

    def best_of(self):
        return self._albert_model.skill_property_value('best_of')

    def submit_gpt_question(self):
        self._albert_view.set_status_text(status_text=f'Working on it...', status_text_life=0)
        self._albert_view.update_idletasks()
        question = self._albert_view.lbl_root_question.get()
        if question:
            response = self._albert_model.ask_gpt(question)
            self._albert_view.display_response(response_text=response)
        else:
            self._albert_view.set_status_text('You must ask a question, before pressing Submit!')
        self._albert_view.set_status_text(status_text=f'Done.')

    def top_p(self):
        return self._albert_model.skill_property_value('top_p')

    def reset_skill_settings(self):
        self._albert_model.load_skill_dictionary()
        self._albert_view.set_temperature_slider(self.gpt_temperature())
        self._albert_view.set_max_tokens_slider(self.max_tokens())
        self._albert_view.set_top_p_slider(self.top_p())
        self._albert_view.set_frequency_slider(self.frequency_penalty())
        self._albert_view.set_presence_slider(self.presence_penalty())
        self._albert_view.set_best_of_slider(self.best_of())

    def rollback_skill_settings(self, skill):
        self._albert_model.restore_config_savepoint()
        self._albert_view.top_skill_editor.close_window()

    def rollback_skill_settings(self):
        self._albert_model.restore_config_savepoint()
        self._albert_view.top_skill_setting.close_window()

    def set_temperature(self, new_gpt_temperature):
        """Updates the self._new_temperature. This property is only promoted when the save_settings mode is
        called. """
        self._albert_model.set_skill_property('gpt_temperature', new_gpt_temperature)

    def set_max_tokens(self, new_max_tokens):
        """Updates the self._new_max_tokens. This property is only promoted when the save_settings mode is
        called. """
        self._albert_model.set_skill_property('max_tokens', new_max_tokens)

    def set_frequency_penalty(self, new_frequency_penalty):
        """Updates the self._new_frequency_penalty. This property is only promoted when the save_settings mode is
        called. """
        self._albert_model.set_skill_property('frequency_penalty', new_frequency_penalty)

    def set_presence_penalty(self, new_presence_penalty):
        """Updates the self._new_presence_penalty. This property is only promoted when the save_settings mode is
        called. """
        self._albert_model.set_skill_property('presence_penalty', new_presence_penalty)

    def set_top_p(self, new_top_p):
        """Updates the self._new_top_p. This property is only promoted when the save_settings mode is
        called. """
        self._albert_model.set_skill_property('top_p', new_top_p)
        # print('New top = ' + str(self._new_top_p))

    def set_best_of(self, new_best_of):
        """Updates the self._new_best_of property. This property is only promoted when the save_settings mode is
        called. """
        self._albert_model.set_skill_property('best_of', new_best_of)

    def save_gtp_settings(self):
        self._albert_model.save_gtp_settings()
        self._albert_view.top_skill_setting.destroy()
        self._albert_view.set_status_text(f'Settings for skill, "{self._albert_model.active_skill()}", have been '
                                          f'updated.')

    def test_openai_key(self, openai_key):
        result = self._albert_model.test_openai_key(openai_key)
        if result:
            self._albert_view.set_status_text(result)
        else:
            self.update_global_config_value('openai_api_key', openai_key)
            self._albert_view.set_status_text('Open AI key updated.')

    def update_text_to_speech_status(self):
        """Function which enables/disables the text-to-speech capability."""
        text_to_speech = self._albert_view.get_text_to_speech_widget()
        print(f'Text to Speech: {text_to_speech}')
        if text_to_speech == 'yes':
            self._albert_view.set_status_text(f'Text to speech enabled.')
        else:
            self._albert_view.set_status_text(f'Text to speech disabled.')
        self._albert_model.update_text_to_speech_status(status=text_to_speech)

    def update_global_config_value(self, config_property, property_value):
        """Broker function, which allows an update to occur to an entry in the global section of the config file."""
        self._albert_model.update_property_value('global', config_property, property_value)

    def validate_copy_to_prompt(self, prompt_file_name: str):
        result = self._albert_model.validate_copy_to_prompt(prompt_file_name)
        if result:
            self._albert_view.top_skill_copy.set_status_text(result)
            return False

    def validate_copy_to_skill(self, copy_to_skill):
        result = self._albert_model.validate_copy_to_prompt(copy_to_skill)
        if result:
            self._albert_view.top_skill_copy.set_status_text(result)
            return False


if __name__ == "__main__":
    albert_controller = AlbertController(app_home=albert_home, initial_skill=skill_selection)
    pass
