import string
from wartleBot.game.letter import LetterStatus

class Alphabet:

    alphabet_dict = {}

    def __init__(self):
        self.alphabet_dict = dict.fromkeys(list(string.ascii_lowercase), LetterStatus.BLACK)
    
    def reset(self):
        for key in self.alphabet_dict:
            self.alphabet_dict[key] = LetterStatus.BLACK
