class Player:

    """
    Initialize Player object with Member ID
    """
    def __init__(self, id, num_guesses):
        self.id = id
        self.remaining_guesses = num_guesses

    """
    Uses up a guess, returns false if no guesses remain, returns true otherwise
    """
    def guess(self):
        self.remaining_guesses -= 1
        if self.remaining_guesses < 0:
            return False
        return True

    def set_guesses(self, num):
        self.remaining_guesses = num
