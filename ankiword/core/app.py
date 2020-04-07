import sys
from os import system, name
import json
import socket

from ankiword.core.ankiconnect import AnkiConnector
from ankiword.ui.image_picker import ImagePicker
from ankiword.utils.bing_image_fetcher import BingImageFetcher
import ankiword.dict.oxford as oxford
from ankiword.utils.parser import ArgsParser
from ankiword.models.PictureWordModel import PictureWordModel


def pretty_print_dict(d):
    print(json.dumps(d, indent=4, sort_keys=True))


class App:

    def __init__(self):
        self.args_parser = ArgsParser()
        self.anki_connector = AnkiConnector()
        self.anki_deck_names = list(self.anki_connector.get_decks().keys())
        self.anki_model_names = list(self.anki_connector.get_models().keys())

        # Cached info so that user can change option if they want.
        # Since Word doesn't cache itself but parse the soup_data everytime
        self.word = None
        self.word_info = None
        self.definitions = None
        self.image_array = None

        # Pick the first defintion and its first example
        self.current_def_index = 0
        self.current_example_index = 0
        # Pick American pronounciation first.
        self.current_pronunciation_index = 1
        self.anki_deck_name_index = 0
        self.anki_model_name_index = 0
        self.image_url = None

    @classmethod
    def get_int_input(cls, lower, higher):
        n = -1
        while True:
            try:
                n = int(input('Option[1-{0}]: '.format(higher)))
                if n < lower or n > higher:
                    raise ValueError
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

    def pick_name(self, _type="mdl"):
        n = self.print_property(_type)
        self.pick_property(_type, n)

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

    def print_property(self, prop):
        print_dict_option = {
            "prn": {
                "txt": "Pronunciations",
                "func": self.get_pronunciations,
                "idx": self.current_pronunciation_index,
                "cb": self.print_UI
            },
            "def": {
                "txt": "Definitions",
                "func": self.get_definitions,
                "idx": self.current_def_index,
                "cb": self.print_UI
            },
            "exm": {
                "txt": "Examples",
                "func": self.get_examples_of_definitions,
                "idx": self.current_example_index
            },
            "mdl": {
                "txt": "Model Names:",
                "data": self.anki_model_names,
                "idx": self.anki_model_name_index},
            "dck": {
                "txt": "Deck Names:",
                "data": self.anki_deck_names,
                "idx": self.anki_deck_name_index
            }
        }

        current_opt = print_dict_option[prop]
        self.clear()
        print('Your word: "{}"'.format(self.word.capitalize()))
        print('{}:'.format(current_opt["txt"]))
        print()
        if "data" not in current_opt.keys():
            array = current_opt["func"]().copy()
        else:
            array = current_opt["data"].copy()
        array.append("Back")

        for i in range(len(array)):
            if i == current_opt["idx"]:
                print('*', end=' ')
            p = array[i]
            # print(p)
            if isinstance(p, dict):
                p = p["prefix"]
            print('{0}. {1}'.format(i+1, p))

        return i+1

    def pick_property(self, prop, back_index):
        """
            Return False when user want to go back to previous UI
        """
        callbacks = {
            "exm": self.pick_definition,
            "def": self.print_UI,
            "prn": self.print_UI,
            "mdl": self.print_anki,
            "dck": self.print_anki
        }
        n = self.get_int_input(1, back_index)
        # n is zero-based
        if n == back_index-1:
            print(callbacks[prop])
            callbacks[prop]()
        elif prop == "def":
            self.current_def_index = n
            # Set to the first one just in case
            self.current_example_index = 0
        elif prop == "prn":
            self.current_pronunciation_index = n
        elif prop == "exm":
            self.current_example_index = n
        elif prop == "dck":
            self.anki_deck_name_index = n
        elif prop == "mdl":
            self.anki_model_name_index = n

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
        if not self.image_url:
            options.insert(-2, ("img", "Add picture for word"))

        for i in range(len(options)):
            print("{0}. {1}".format(i+1, options[i][1]))

        n = self.get_int_input(1, len(options))
        action = options[n][0]
        if action == "def":
            n = self.print_property("def")
            self.pick_property("def", n)
            n = self.print_property("exm")
            self.pick_property("exm", n)
        elif action == "prn":
            n = self.print_property("prn")
            self.pick_property("prn", n)
        elif action == "img":
            self.pick_image()
        elif action == "ext":
            self.stop()
        elif action == "sav":
            self.print_anki()
        self.print_UI()

    def pick_image(self):
        if not self.image_array:
            socket.setdefaulttimeout(2)
            img_fetcher = BingImageFetcher()
            img_array = img_fetcher.download_from_word(self.word)
            print('Download finished.')
            print('Opening window to choose image...')
            socket.setdefaulttimeout(None)

        img_picker = ImagePicker(img_array)
        img_picker.run()
        self.image_url = img_picker.retrieve_result()

    def print_anki_decks(self):
        mdls = self.anki_connector.get_decks()
        names = mdls.keys()
        for i in range(len(names)):
            print('{0}. {1}'.format(i+1, names[i]))

    def print_anki(self):
        self.clear()
        print('Current model name:',
              self.anki_model_names[self.anki_model_name_index])
        print('Current deck name:',
              self.anki_deck_names[self.anki_deck_name_index])
        options = [("mdl", "Choose model name"), ("dck", "Choose card name"),
                   ("uld", "Upload note to anki"), ("bck", "Back")]
        for i in range(len(options)):
            print('{0}. {1}'.format(i+1, options[i][1]))
        n = self.get_int_input(1, i+1)
        action = options[n][0]
        if action in ["mdl", "dck"]:
            n = self.print_property(action)
            self.pick_property(action, n)
            self.print_anki()
        elif action == "uld":

            if self.image_url:
                img_filename = '_'+self.image_url.split('/')[-1]
                base64_img = self.anki_connector.convert_image_to_base64(
                    self.image_url)
                print('Uploading picture to storage...')
                print(self.anki_connector.store_media_file(
                    img_filename, data=base64_img))

            if self.get_current_pronunciation():
                sound_url = self.get_current_pronunciation()["url"]
                audio_filename = '_' + sound_url.split('/')[-1]
                print('Uploading audio to storage...')
                print(self.anki_connector.store_media_file(
                    audio_filename, sound_url))

            note = PictureWordModel(self.word, self.get_current_definition(
            ), self.get_current_pronunciation(), audio_filename, img_filename)
            print(self.anki_connector.add_note(
                self.anki_deck_names[self.anki_deck_name_index],
                self.anki_deck_names[self.anki_model_name_index],
                note.get_fields()))
            input()

        else:
            self.print_UI()


if __name__ == "__main__":
    app = App()
    app.run()
