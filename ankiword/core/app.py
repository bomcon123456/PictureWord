from ankiword.utils.parser import WordParser
import ankiword.dict.oxford as oxford
from ankiword.utils.bing_image_fetcher import BingImageFetcher
from ankiword.ui.image_picker import ImagePicker


class App:
    def __init__(self):
        self.word_parser = WordParser()
        self.fetcher = BingImageFetcher()

    def run(self):
        inputs = self.word_parser.get_word()
        print(inputs)
        lookup = oxford.Word()
        lookup.get(inputs)

        word_name = lookup.name()
        definitions = lookup.definitions()
        pronounciations = lookup.pronunciations()
        examples = lookup.examples()

        print(word_name)
        print(definitions)
        print(pronounciations)
        print(examples)

        my_array = self.fetcher.download_from_word(word_name)
        app = ImagePicker(my_array)
        app.run()
        image_path = app.retrieve_result()
        print(image_path)
