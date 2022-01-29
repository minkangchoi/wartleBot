from enum import Enum


"""
GREEN: Correct letter in correct index
YELLOW: Correct letter in wrong index
BLACK: Wrong letter
WHITE: Unused letter
"""
class LetterStatus(Enum):
    GREEN = 1
    YELLOW = 2
    BLACK = 3
    WHITE = 4

class Letter:
    status = LetterStatus.WHITE
    index = 0
    char = ''
    matched = False

    def __init__(self, index, char, status):
        self.index = index
        self.char = char
        self.status = status
