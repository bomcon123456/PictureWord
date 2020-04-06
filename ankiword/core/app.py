from os import system, name
import json

from ankiword.utils.parser import ArgsParser
import ankiword.dict.oxford as oxford
from ankiword.utils.bing_image_fetcher import BingImageFetcher
from ankiword.ui.image_picker import ImagePicker


def pretty_print_dict(d):
    print(json.dumps(d, indent=4, sort_keys=True))


class App:
    def __init__(self):
        self.args_parser = ArgsParser()
        self.fetcher = BingImageFetcher()

        # Cached info so that user can change option if they want.
        # Since Word doesn't cache itself but parse the soup_data everytime
        self.word = None
        self.word_info = None
        self.definitions = None

        # Pick the first defintion and its first example
        self.current_def_index = 0
        self.current_example_index = 0
        # Pick american pronounciation first.
        self.current_pronounciation_index = 1
        self.image_url = None

        # self.word_dict = {
        #     "name": None,
        #     "definitions": [],
        #     "pronunciations": [],
        #     "examples": [],
        #     "image_src": None
        # }

    @staticmethod
    def get_int_input(lower, higher):
        try:
            n = int(input())
            if n <= lower or n >= higher:
                raise
            n -= 1
        except:
            print('[Error] Invalid selection, please try again.')
            n = -1
        finally:
            return n

    def clear(self):
        # check and make call for specific operating system
        _ = system('clear') if name == 'posix' else system('cls')

    def run(self):
        word = self.args_parser.get_word()
        self.set_current_word(word)
        self.print_UI()

    def get_current_definition(self):
        return self.get_definitions()[self.current_def_index]

    def get_current_example(self):
        return self.get_example_of_definitions()[self.current_example_index]

    def get_current_pronunciation(self):
        return self.get_pronunciations()[self.current_pronounciation_index]

    def get_example_of_definitions(self):
        entry = self.word_info["definitions"][self.current_def_index]
        definition_dict = entry["definitions"][0]
        # import json
        # print(json.dumps(definition_dict, indent=2, sort_keys=True))
        word_example = definition_dict["examples"]
        return word_example

    def get_definitions(self):
        if not self.definitions:
            entry = self.word_info["definitions"]
            self.definitions = list(map(
                lambda x: x["definitions"][0]["description"],
                entry))
        return self.definitions

    def print_definitions(self):
        self.clear()
        print('Your word: "{}"'.format(self.word.capitalize()))
        print('Definitions:')
        defs = self.get_definitions()

        for i in range(len(defs)):
            if i == self.current_def_index:
                print('*', end=' ')
            print('{0}. {1}'.format(i+1, defs[i]))
        print('Options[1-{}]: '.format(i+1), end=' ')

    def pick_definitions(self):
        n = self.get_int_input(0, len(self.get_definitions()))
        if n == -1:
            return

        self.current_def_index = n

    def print_example(self):
        self.clear()
        print('Your word: "{}"'.format(self.word.capitalize()))
        print('Examples:')
        exs = self.get_example_of_definitions()

        for i in range(len(exs)):
            if i == self.current_example_index:
                print('*', end=' ')
            print('{0}. {1}'.format(i+1, exs[i]))
        print('Options[1-{}]: '.format(i+1), end=' ')

    def pick_example(self):
        n = self.get_int_input(0, len(self.get_example_of_definitions()))
        if n == -1:
            return
        self.current_example_index = n

    def get_pronunciations(self):
        return self.word_info["pronunciations"]

    def set_current_word(self, word):
        oxford.Word.get(word)

        self.word_info = oxford.Word.info()
        self.word = oxford.Word.name()

    def print_UI(self):
        self.clear()
        print('Welcome to AnkiWord!')
        print()
        print('Your word: "{}"'.format(self.word.capitalize()))
        print('Definition:', self.get_current_definition())
        print('Example:', self.get_current_example())
        pronunciation = self.get_current_pronunciation()
        if pronunciation['ipa']:
            print('IPA:', pronunciation['ipa'], end=' --- ')
            print('Current audio file is',
                  'NAmE.' if self.current_pronounciation_index else 'BrE.')
        if self.image_url:
            print("Picture word: Loaded.")
        else:
            print("Picture word: Not found.")
        print()

        def_length = len(self.get_definitions())
        pro_length = len(self.get_pronunciations())

        print(
            'There are {0} other definitions and {1} other pronunciation speaker.'.format(
                str(def_length-1), str(pro_length-1)
            ))
        print('1. See other definitions')
        print('2. Change pronunciation speaker')
        print('3. Choose picture word')
        print('3. Save to Anki')
        print('4. Exit')
        print('Option [1-4]: ', end='')
        n = int(input())
        if n == 1:
            self.print_definitions()
            self.pick_definitions()
            self.print_example()
            self.pick_example()
            self.print_UI()


if __name__ == "__main__":
    app = App()
    app.run()
