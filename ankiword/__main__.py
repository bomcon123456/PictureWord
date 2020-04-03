from .utils.parser import WordParser


def main():
    word_parser = WordParser()

    word_parser.parse()
    print(word_parser.get_word())


if __name__ == '__main__':
    main()
