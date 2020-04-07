class PictureWordModel:
    def __init__(self, word, GPE, IPA=None, sound_name=None, picture_name=None):
        self.word = word
        self.GPE = GPE
        self.sound_name = sound_name
        self.IPA = IPA
        self.picture_name = picture_name

    def get_fields(self):
        picture = ''
        if self.picture_name:
            picture = '<img src="{0}">'.format(self.picture_name)
        pronun = ''
        if self.IPA:
            pronun = self.IPA + '\n'
        if self.sound_name:
            pronun += '[sound:{}]'.format(self.sound_name)
        return {
            "Word": self.word,
            "Picture": picture,
            "Gender, Personal Connection, Extra Info (Back side)": self.GPE,
            "Pronunciation (Recording and/or IPA)": pronun,
            "Test Spelling? (y = yes, blank = no)": "y"
        }
