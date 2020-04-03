import argparse


class WordParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Word Look-up and Ankifying.')
        self.parser.add_argument('word', metavar='w', type=str, nargs='+',
                                 help='Word need to be looked up and ankified.')
        self.args = None

    def parse(self):
        self.args = self.parser.parse_args()

    def _process_word_args(self, word_array):
        full_word = '-'.join(word_array).strip().lower()

        return full_word

    def get_word(self):
        return self._process_word_args(self.args.word)
