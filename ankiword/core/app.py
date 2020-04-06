from ankiword.utils.parser import ArgsParser
import ankiword.dict.oxford as oxford
from ankiword.utils.bing_image_fetcher import BingImageFetcher
from ankiword.ui.image_picker import ImagePicker


class App:
    def __init__(self):
        self.args_parser = ArgsParser()
        self.fetcher = BingImageFetcher()

        # Cached info so that user can change option if they want.
        # Since Word doesn't cache itself but parse the soup_data everytime
        self.word_info = None
        self.definitions = None

        # Pick the first defintion and its first example
        self.current_def_index = 0
        self.current_example_index = 0
        # Pick american pronounciation first.
        self.current_pronounciation_index = 1

        self.word_dict = {
            "name": None,
            "definitions": [],
            "pronunciations": [],
            "examples": [],
            "image_src": None
        }

    def run(self):
        word = self.args_parser.get_word()
        self.set_current_word(word)
        self.print_UI()

    def get_example_of_definitions(self):
        """
            Get examples of the definition the user chose
        """
        entry = self.word_info["definitions"][self.current_def_index]
        definition_dict = entry["definitions"][0]
        # import json
        # print(json.dumps(definition_dict, indent=2, sort_keys=True))
        word_example = definition_dict["examples"]
        return word_example

    def get_definitions(self):
        if not self.definitions:
            self.definitions = oxford.Word.definitions()
        return self.definitions

    def get_pronunciations(self):
        return self.word_info["pronunciations"]

    def set_current_word(self, word):
        oxford.Word.get(word)

        self.word_info = oxford.Word.info()
        self.word_dict["name"] = oxford.Word.name()

        # Default pick
        self.word_dict["definitions"] = self.get_definitions()[
            self.current_def_index].capitalize()
        self.word_dict["examples"] = self.get_example_of_definitions()[
            self.current_example_index]
        self.word_dict["pronunciations"] = self.get_pronunciations()[
            self.current_pronounciation_index]

    def print_UI(self):

        print('Welcome to AnkiWord!')
        print()
        print('Your word: "{}"'.format(self.word_dict["name"].capitalize()))
        print('Definition:', self.word_dict["definitions"])
        print('Example:', self.word_dict["examples"])
        if self.word_dict["pronunciations"]['ipa']:
            print('IPA:', self.word_dict["pronunciations"]['ipa'], end=' --- ')
            print('Current audio file is',
                  'NAmE.' if self.current_pronounciation_index else 'BrE.')
        if self.word_dict["image_src"]:
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
        print('Option [1-4]: ')


if __name__ == "__main__":
    app = App()
    app.run()
