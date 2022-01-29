from letter import Letter, LetterStatus


class Word:
    
    word_string = ""
    word = []

    """
    Custom class constructor with a string input, converts into an array of Letters
    """
    def __init__(self, word):
        self.word_string = word
        for i in range(0, len(word)):
            self.word.append(Letter(i, word[i], LetterStatus.BLACK))

    """
    Returns array of Letters of input with correctness
    """
    def check_word(self, text):
        
        results = []

        for i in range(0, len(text)):
            results.append(Letter(i, text[i], LetterStatus.WHITE))

        # Green pass
        for i in range(0, len(text)):
            if text[i] == self.word[i].char:
                results[i].status = LetterStatus.GREEN
                self.word[i].matched = True
                results[i].matched = True

        # Yellow pass
        for i in range(0, len(text)):
            if not results[i].matched:
                for j in range(0, len(self.word)):
                    if text[i] == self.word[j].char and i != j and not self.word[j].matched:
                        results[i].status = LetterStatus.YELLOW
                        self.word[j].matched = True
                        break
                    
        return results

    def reset_matched(self):
        for letter in self.word:
            letter.matched = False


    """
    Static Method to print a word
    """
    @staticmethod
    def print(array):
        results = ""

        # First pass for emoji
        for letter in array:
            if letter.status == LetterStatus.GREEN:
                results += ":green_square:"
            elif letter.status == LetterStatus.YELLOW:
                results += ":yellow_square:"
            elif letter.status == LetterStatus.WHITE:
                results += ":white_large_square:"
            else:
                return "ur trash"

        # Second pass for letters
        results += '\n'
        for letter in array:
            results += letter.char + "     "
        # results += "```"

        return results
