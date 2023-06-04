import cbtk_kit as ck
import os
import openai
import re
import sys
import textwrap
from os.path import exists
import shutil
import copy
import pyperclip
import multiprocessing
# import re
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path

DEBUG = False


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


class AlbertModel:
    """Class to control our primary Einstein application data."""

    def __init__(self, app_home: Path, initial_skill: str):

        self._config = ConfigParser(interpolation=ExtendedInterpolation())
        self._display_fields_width = 120
        self._app_home = app_home
        self._app_images = self._app_home / 'images'
        self._app_configs = self._app_home / 'config'
        self._etc = self._app_home / 'etc'
        self._config_ini = self._app_configs / 'albert.ini'
        self._skill_info_file = Path('')
        self._skill_nfo_text = ''
        self._prompt_file = Path('')
        self._prompt_text = ''
        self._response = ''
        self._skill = ''
        # We populate the skill settings dict later, these are properties for the selected skill.
        # They are initialised from the config/ini file.
        self._skill_settings_dict = {}
        # We establish a shadow copy of self._skill_settings_dict, in the form of self._session_settings_dict. This can
        # be used to rollback changes to settings, when the cancel button is used in the settings dialog.
        self._savepoint_settings_dict = {}
        # We populate the components settings dict later, these are components  related to the
        # selected skill (e.g. prompt file and skill infor text). This also includes the associated skill.
        self._skill_components_dict = {}
        self.switch_skill(new_skill=initial_skill)
        # Initialise properties
        self._control_params_dict = {'home_dir': str(Path(os.getenv("HOME")))}

        self._control_params_dict['app_home'] = self._control_params_dict['home_dir'] + '/albert'
        self._control_params_dict['albert_config'] = self._control_params_dict['app_home'] + '/config'
        self._albert_config = self._control_params_dict['albert_config'] + '/albert.ini'

        self._openai_api_key = self.config_property_value("global", "openai_api_key")
        openai.api_key = self._openai_api_key

        self._text_to_speech_cmd = self.config_property_value("global", "text_to_speech_cmd")
        self._text_to_speech = 'no'

    def copy_skill_config(self, from_skill_name: str, to_skill_name: str, to_prompt_file_name: str, to_info_file_name: str):
        etc_dir = self._app_home / 'etc'
        if to_skill_name == '':
            return 'You must enter a prompt file name!'
        elif self._config.has_section(to_skill_name):
            return 'The entered "new" skill name, already exists!'
        elif exists(f'{self._etc}/{to_prompt_file_name}.prompt'):
            return 'The entered prompt file name, is already in use. Please choose another!'
        elif exists(f'{self._etc}/{to_info_file_name}.nfo'):
            return 'The entered info file name, is already in use. Please choose another!'

        self.copy_config_section(source_section=from_skill_name,
                                 target_section=to_skill_name)

        self.update_property_value(config_section=to_skill_name,
                                   config_property='prompt_file',
                                   property_value=str(self._etc / to_prompt_file_name) + '.prompt')

        self.update_property_value(config_section=to_skill_name,
                                   config_property='skill_info_file',
                                   property_value=str(self._etc / to_info_file_name) + '.nfo')

        file_check = self.validate_file_name(file_name=to_prompt_file_name, purpose='prompt')
        if file_check:
            return file_check
        file_check = self.validate_file_name(file_name=to_info_file_name, purpose='info')
        if file_check:
            return file_check

        from_prompt_file = self.config_property_value(config_section=from_skill_name, config_key='prompt_file')
        from_info_file = self.config_property_value(config_section=from_skill_name, config_key='skill_info_file')

        shutil.copyfile(from_prompt_file, f'{self._etc}/{to_prompt_file_name}.prompt')
        shutil.copyfile(from_info_file, f'{self._etc}/{to_info_file_name}.nfo')
        return f'New skill, "{to_skill_name}", created.'


    def test_openai_key(self, openai_key):
        question = 'How far is the Sun from the Earth?'
        openai.api_key = openai_key
        try:
            self.ask_gpt(my_question=question)
        except openai.error.AuthenticationError:
            # Restore previous key
            self._openai_api_key = self.config_property_value("global", "openai_api_key")
            openai.api_key = self._openai_api_key
            return 'You entered an invalid OpenAI key!'

    def ask_gpt(self, my_question):
        prompt = self._prompt_text
        prompt = prompt + self.skill_property_value('stop') \
                 + self.skill_property_value('q_prompt') + ' ' + my_question \
                 + self.skill_property_value('stop') \
                 + self.skill_property_value('a_prompt') + ' '

        prompt_text = str(prompt)

        engine = self.skill_property_value('gpt_engine')
        temperature = self.skill_property_value('gpt_temperature')
        max_tokens = self.skill_property_value('max_tokens')
        top_p = self.skill_property_value('top_p')
        frequency_penalty = self.skill_property_value('frequency_penalty')
        presence_penalty = self.skill_property_value('presence_penalty')
        stop = self.skill_property_value('stop')

        if DEBUG:
            print('=' * 100)
            print(f'PROMPT: {self._prompt_text}')
        # print('Prompt: ', prompt)
        gpt_response = openai.Completion.create(
            # engine="davinci-instruct-beta-v3",
            engine=engine,
            prompt=prompt_text,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop
        )
        if DEBUG:
            print(f'     active_skill: {self.active_skill()}')
            print(f'           engine: {engine}')
            print(f'  gpt_temperature: {temperature}')
            print(f'       max_tokens: {max_tokens}')
            print(f'            top_p: {top_p}')
            print(f'frequency_penalty: {frequency_penalty}')
            print(f' presence_penalty: {presence_penalty}')
            print(f'             stop: {stop}')
            print(f'           prompt: <<<{prompt_text}>>>')

        # print ('Response: ', gpt_response)
        response = gpt_response['choices'][0]['text']
        if DEBUG:
            print('Raw response:')
            print(gpt_response)
            print('=' * 100)
            print('Extracted result:')
            print(response)
            print('=' * 100)
        response = response.strip()
        if not response:
            response = "I can't answer that, sorry!"
        self._response = response
        if self._text_to_speech == 'yes':
            self.spawn_speak_task()
        return response

    def copy_answer_to_clipboard(self):
        pyperclip.copy(self._response)

    def copy_config_section(self, source_section, target_section):
        self._config.add_section(target_section)
        for key, value in self._config.items(source_section):
            self._config.set(target_section, key, value)
        with open(self._config_ini, 'w') as f:
            self._config.write(f)

    def delete_skill(self, skill):
        prompt_file = self.config_property_value(config_section=skill, config_key='prompt_file')
        info_file = self.config_property_value(config_section=skill, config_key='skill_info_file')
        try:
            os.remove(prompt_file)
        except FileNotFoundError:
            print(f'WARNING: Prompt file, {prompt_file}, was not found - could not delete!')

        try:
            os.remove(info_file)
        except FileNotFoundError:
            print(f'WARNING: Skill info file, {info_file}, was not found - could not delete!')

        self._config.remove_section(skill)
        with open(self._config_ini, "w") as f:
            self._config.write(f)

    def editable_skills(self):
        """Returns a list of non-locked skills.
        :return: list
        """
        # self.config_sections(section='global')
        locked_skills = self.config_property_value(config_section='global', config_key='locked_skills')
        system_sections = self.config_property_value(config_section='global', config_key='system_sections')
        skip_entries = locked_skills + ',' + system_sections
        skip_entries = skip_entries.split(',')

        editable_skills = [section for section in self._config.sections() if section not in skip_entries]
        return editable_skills

    def is_locked_skill(self, skill=''):
        """Determines whether the specified skill is a locked skill (cannot be edited and changes persisted). If a
        skill is not passed as a parameter, the currently active skill is assumed and checked for.
        :param skill:
        :return: bool
        """
        locked_skills = self.config_property_value(config_section='global', config_key='locked_skills')
        if skill:
            if skill in locked_skills:
                return True
        elif self._skill in locked_skills:
            return True

    def save_gtp_settings(self):
        for key, _ in self._config.items(self._skill):
            property_value = self._skill_settings_dict[key]
            data_type = self.skill_property_data_type(skill_key=key)

            if data_type == 'int':
                property_value = int(property_value)
            property_value = str(property_value)
            self._config.set(self._skill, key, property_value)
        with open(self._config_ini, 'w') as f:
            self._config.write(f)

    def take_config_savepoint(self):
        """Take a savepoint of our selected skill settings dictionary"""
        self._savepoint_settings_dict = copy.deepcopy(self._skill_settings_dict)

    def restore_config_savepoint(self):
        """Restore from savepoint our selected skill settings dictionary"""
        self._skill_settings_dict = copy.deepcopy(self._savepoint_settings_dict)

    def config_property_value(self, config_section: str, config_key: str):
        # print(f'This section : {this_section}; This option: {this_option}')
        # If we are being specific about one of the higher level sections we are more stringent.
        property_val = ''
        property_val = self._config[config_section][config_key]
        return property_val

    def skill_property_data_type(self, skill_key):
        try:
            data_type = self.config_property_value(config_section='config_data_types', config_key=skill_key)
            return data_type
        except KeyError:
            print(f'Cannot locate skill property datatype for: {skill_key}')
            raise

    def skill_property_value(self, skill_key: str):
        """Obtain a skill related property value from the configuration for the specified skill (i.e.config section):
        :param skill_key:
        :return: str/float/int/Path
        """

        # Here we look for specific mode entries and if they don't exist, we search the
        # higher default for a property value
        property_val = self._skill_settings_dict[skill_key]
        data_type = self.skill_property_data_type(skill_key)

        if data_type == 'str':
            return property_val
        elif data_type == 'float':
            return float(property_val)
        elif data_type == 'int':
            return int(property_val)
        elif data_type == 'Path':
            return Path(property_val)
        else:
            return property_val

    def set_skill_property(self, skill_property_key, skill_property_value):
        self._skill_settings_dict[skill_property_key] = skill_property_value

    def has_section(self, check_section):
        return self._config.has_section(check_section)

    def config_sections(self, section: str):
        """The config_sections method, optionally accepts a section for our configparser file and prints the
        properties of the section. If no section is supplied, it lists the sections. This is a debug method."""
        if section:
            print(f'Section dump for: {section}')
            print(dict(self._config.items(section)))
            print('Keys:')
            for key in self._config[section]: print(key)
        else:
            sections = self._config.sections()
            print(f'Init File: {self._config_ini}')
            print(f'Sections: {sections}')

    def update_property_value(self, config_section, config_property, property_value):
        self._config.set(config_section, config_property, property_value)
        with open(self._config_ini, 'w') as configfile:
            self._config.write(configfile)

    def set_skill(self, skill):
        self._skill = skill

    def load_skill_dictionary(self):
        """The load_skill_dictionary function loads the skills into a dictionary. If the user changes the settings, 
        (e.g. using the sliders), it's the dictionary settings that we maintain. We persist these to the config file, 
        only if the user is allowed to saVe them. These are also the settings used to run the GPT engine."""

        # First get the defaults
        for key, value in self._config.items('skill_defaults'):
            self._skill_settings_dict[key] = value
        # Now get the explicit skill settings, overwriting defaults in the dictionary, as required.
        for key, value in self._config.items(self._skill):
            self._skill_settings_dict[key] = value

    def switch_skill(self, new_skill):
        """The switch skill function, accepts a new skill and establishes the corresponding prompt file. It then goes
        on the call self._load_skill_settings_dict, which loads the properties of the selected skill, into a dictionary.
        :param new_skill: """
        if not exists(self._config_ini):
            print(f'ERROR: Cannot locate configuration file: {self._config_ini}')
            raise FileNotFoundError
        self._config = ConfigParser(interpolation=ExtendedInterpolation())
        self._config.read(self._config_ini)
        self._skill = new_skill
        self.load_skill_dictionary()

        # Obtain and store the skill prompt text.
        self._prompt_file = self.skill_property_value(skill_key='prompt_file')
        if not exists(self._prompt_file):
            print(f'Cannot open prompt file: {self._prompt_file}')
            raise FileNotFoundError
        else:
            with open(self._prompt_file, 'r') as file:
                self._prompt_text = file.read()

        # Obtain and store the skill info text.
        self._skill_info_file = self.skill_property_value(skill_key='skill_info_file')
        if not exists(self._skill_info_file):
            print(f'Cannot open prompt file: {self._skill_info_file}')
            raise FileNotFoundError
        else:
            with open(self._skill_info_file, 'r') as file:
                skill_info_text = file.read()
                self._skill_components_dict['skill_info_text'] = skill_info_text

        # Store the associated skill
        self._skill_components_dict['active_skill'] = new_skill

        self._text_to_speech = self.skill_property_value(skill_key='text_to_speech')

    def component_value(self, component_key):
        """The component_value function, Serves up the prompt value associated with the passed component_key.
        :return: self._skill_components_dict[component_key]"""
        return self._skill_components_dict[component_key]

    def active_skill(self):
        """The active_skill function, Serves up the currently active (selected) skill.
        :return: self._skill_components_dict['active_skill']"""
        return self.component_value('active_skill')

    def prompt_file_text(self):
        """The prompt_file_text function, Serves up the prompt file text on demand. This is the text used to "describe"
        the mode of operation to GPT-3.
        :return: self._skill_components_dict['prompt_file_text']"""
        return self.component_value('prompt_file_text')

    def skill_info_text(self, skill='', skill_text_width=120):
        """The skill_info_text function, Serves up the prompt info text on demand. This is the text used to describe
        the skill at the top of the main (root) window. If no skill is passed, then we retrieve the skill infor text
        for the currently active skill.
        :return: self._skill_components_dict['skill_info_text'] """
        if skill:
            self._skill_info_file = self.config_property_value(config_section=skill, config_key='skill_info_file')
            with open(self._skill_info_file, 'r') as file:
                skill_info_text = file.read()
        else:
            skill_info_text = self.component_value('skill_info_text')
        # SKill settings frame width:
        skill_settings_width = skill_text_width
        skill_info_text = wrap_string(skill_info_text, skill_settings_width)
        return skill_info_text

    def spawn_speak_task(self):
        process = multiprocessing.Process(target=self.speak_result, args=(self._response,))
        process.start()

    def speak_result(self, result_text):
        speech_cmd = self.config_property_value("global", "text_to_speech_cmd")
        command = f'echo "{result_text}" | {speech_cmd}'
        if DEBUG:
            print(command)
        os.system(command)

    def submit_config_copy(self, source_section: str, target_section: str, target_prompt_prefix: str):
        copy_from_skill = source_section
        copy_to_skill = target_section
        copy_to_prompt = target_prompt_prefix

        shutil.copyfile(f'{self._prompt_file}.prompt', f'{self._app_etc}/{copy_to_prompt}.prompt')
        if exists(self._prompt_file + '.nfo'):
            shutil.copyfile(f'{self._prompt_file}.nfo', f'{self._app_etc}/{copy_to_prompt}.nfo')
        else:
            open(f'{self._prompt_file}.nfo', 'a').close()

    def skills_list(self):
        section_list = [entry for entry in self._config.sections() if entry not in ('global',
                                                                                    'skill_defaults',
                                                                                    'config_data_types')]
        return section_list

    def update_text_to_speech_status(self, status):
        self._text_to_speech = status

    def validate_copy_to_skill(self, copy_to_skill):
        if self._albert_config.has_section(copy_to_skill):
            return 'The entered skill name, is already in use.'
        else:
            return ''

    @staticmethod
    def validate_file_name(file_name, purpose):
        pattern = '^[\w\d_()]*$'
        if not re.fullmatch(pattern, file_name) and file_name != '':
            return f'Entered {purpose} file name is invalid. It should only include alphanumerics & underscores.'
        else:
            return ''


if __name__ == "__main__":
    home_dir = Path(os.getenv("HOME"))
    home = home_dir / 'albert'
    # config_ini = home_dir + 'albert/config'
    albert = AlbertModel(app_home=home, initial_skill='O/S Commands')
