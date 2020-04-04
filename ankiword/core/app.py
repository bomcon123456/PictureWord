from ankiword.utils.parser import WordParser
import ankiword.dict.oxford as oxford
from ankiword.utils.bing_image_fetcher import BingImageFetcher


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

        self.fetcher.download_from_word(word_name)
        print('niehehe')
