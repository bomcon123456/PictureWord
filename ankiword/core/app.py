import sys
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
        self.current_pronunciation_index = 1
        self.image_url = None

    @classmethod
    def get_int_input(cls, lower, higher):
        n = -1
        while True:
            try:
                n = int(input())
                if n < lower or n > higher:
                    raise
                n -= 1
                return n
            except ValueError:
                print('[Error] Invalid selection, please try again.')
            except (EOFError, KeyboardInterrupt):
                cls.stop()

    def clear(self):
        # check and make call for specific operating system
        _ = system('clear') if name == 'posix' else system('cls')

    def run(self):
        word = self.args_parser.get_word()
        self.set_current_word(word)
        self.print_UI()

    @staticmethod
    def stop():
        print('')
        print('Thank you for using!')
        sys.exit(0)

    def pick_definition(self):
        n = self.print_property("def")
        self.pick_property("def", n)
        n = self.print_property("exm")
        self.pick_property("exm", n)
        self.print_UI()

    def get_current_definition(self):
        return self.get_definitions()[self.current_def_index]

    def get_current_example(self):
        return self.get_examples_of_definitions()[self.current_example_index]

    def get_current_pronunciation(self):
        return self.get_pronunciations()[self.current_pronunciation_index]

    def get_examples_of_definitions(self):
        entry = self.word_info["definitions"][self.current_def_index]
        definition_dict = entry["definitions"][0]
        word_example = definition_dict["examples"]
        return word_example

    def get_definitions(self):
        if not self.definitions:
            entry = self.word_info["definitions"]
            self.definitions = list(map(
                lambda x: x["definitions"][0]["description"],
                entry))
        return self.definitions

    def print_property(self, prop, pick=False):
        print_dict_option = {
            "prn": {
                "txt": "Pronunciations",
                "func": self.get_pronunciations,
                "idx": self.current_pronunciation_index,
                "cb": self.print_UI},
            "def": {
                "txt": "Definitions",
                "func": self.get_definitions,
                "idx": self.current_def_index,
                "cb": self.print_UI},

            "exm": {
                "txt": "Examples",
                "func": self.get_examples_of_definitions,
                "idx": self.current_example_index}
        }

        current_opt = print_dict_option[prop]
        self.clear()
        print('Your word: "{}"'.format(self.word.capitalize()))
        print('{}:'.format(current_opt["txt"]))
        print()
        array = current_opt["func"]().copy()
        array.append("Back")

        for i in range(len(array)):
            if i == current_opt["idx"]:
                print('*', end=' ')
            print('{0}. {1}'.format(i+1, array[i]))
        print('Options[1-{}]: '.format(i+1), end=' ')

        return i+1

    def pick_property(self, prop, back_index):
        """
            Return False when user want to go back to previous UI
        """
        callbacks = {
            "exm": self.pick_definition,
            "def": self.print_UI,
            "prn": self.print_UI
        }
        n = self.get_int_input(1, back_index)
        # n is zero-based
        if n == back_index-1:
            callbacks[prop]()
        elif prop == "def":
            self.current_def_index = n
            # Set to the first one just in case
            self.current_example_index = 0
        elif prop == "prn":
            self.current_pronunciation_index = n
        elif prop == "exm":
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
                  'NAmE.' if self.current_pronunciation_index else 'BrE.')
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
            ), end='\n\n')

        options = [("sav", "Save to Anki"), ("ext", "Exit")]
        if pro_length > 1:
            options.insert(0, ("prn", "Change pronunciation speaker"))
        if def_length > 1:
            options.insert(0, ("def", "See other definitions"))

        for i in range(len(options)):
            print("{0}. {1}".format(i+1, options[i][1]))
        print('Option [1-4]: ', end='')

        n = self.get_int_input(1, 4)
        action = options[n][0]
        if action == "def":
            n = self.print_property("def")
            self.pick_property("def", n)
            n = self.print_property("exm")
            self.pick_property("exm", n)
            self.print_UI()
        elif action == "prn":
            self.print_property("prn")
            self.pick_pronun()
        elif action == "ext":
            self.stop()


if __name__ == "__main__":
    app = App()
    app.run()
