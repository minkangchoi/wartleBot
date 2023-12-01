import json
import random
import requests
import discord
from discord.ext import commands
from .player import Player
from .word import Word
from .letter import LetterStatus
from .alphabet import Alphabet
from .leaderboard import Leaderboard

class Game:

    def __init__(self, guild_id, channel, bot, TENOR_TOKEN):
        # Init object for python
        self.bot = bot
        self.TENOR_TOKEN = TENOR_TOKEN

        """
        players: A dict with {<player_id>: Player Object} that stores all
            players registered for the game

        words_dict: A dict that hold all dictionary words with word_length

        channel: The channel to send output to
        """
        self.players = {}
        self.words_dict = {}
        self.common_words_dict = {}
        self.channel = channel 

        # Game Setup Variables
        self.friendly_mode = True
        self.correct_word = ""
        self.correct_word_object = None
        self.word_length = 9
        self.num_guesses = 3
        
        self.guess_history = []
        self.alphabet = None
        self.alphabet = Alphabet()
        self.game_over = True
        
        self.leaderboard = Leaderboard(guild_id)


    """
    Command to start the game
    """
    async def start_game(self, word_length):
        self.game_over = False
        self.players.clear()
        self.guess_history.clear()
        self.words_dict.clear()
        self.alphabet.reset()
        self.word_length = int(word_length)

        # Initialize word dictionary with words of string length
        with open('wartleBot/resources/output.json') as json_file:
            data = json.load(json_file)
        self.words_dict = data[str(self.word_length)]

        with open('wartleBot/resources/common_words.json') as json_file:
            data = json.load(json_file)
        self.common_words_dict = data[str(self.word_length)]

        # Select random word given length
        self.correct_word = random.choice(list(self.common_words_dict.keys()))
        print(self.correct_word)
        self.correct_word_object = Word(self.correct_word)

        # Print start message
        begin_emoji = ":white_square_button:" * self.word_length
        await self.print_to_channel(
            "Today's Wartle has begun!\n" + begin_emoji + "\n"
            "Reveal the **" + str(self.word_length) + "** letter word in **" + str(self.num_guesses) + "** guesses!\n" +
            "Use `!join` or `!j` to join the game!\n" +
            "Type `!rules` or `!coms` for for more info"
        )


    ########################## COMMAND FUCNTIONS #########################
    """
    Command to guess a word
    """
    async def guess(self, ctx, arg):
        if await self.has_joined(ctx):
            self.correct_word_object.reset_matched()

            # Convert to all lowercase
            arg = arg.lower()

            # Check for correct length
            if len(arg) != self.word_length:
                if(self.friendly_mode):
                    await self.print_to_channel("Word must be " + str(self.word_length) + " letters long!")
                else:
                    await self.print_to_channel("You idiot stupid idiot moron little stupid child it's not " + str(self.word_length) + " letters long")
                return

            # Check that word exists
            if not self.word_exists(arg):
                if(self.friendly_mode):
                    await self.print_to_channel(str(arg) + " is not a real word!")
                else:
                    await self.print_to_channel(str(arg) + " is not a real word you stupid idiot stupid moron stupid little moron child ")
                return

            # Case if word is correct
            if arg == self.correct_word:
                green_square_string = ":green_square:" * self.word_length
                final_print = "`"
                for letter in self.correct_word:
                    final_print += letter + "  "
                final_print += "`"
                
                await self.print_to_channel("**" + str(ctx.author) + " guessed the word!!**\n" + green_square_string + "\n" + final_print) 
                self.game_over = True

                # Get Tenor GIF for win
                await self.send_gif()
                return

            # Check if user had guesses remaining
            if self.players[ctx.author.id].guess():
                remaining_string = "**" + str(ctx.author) + "** has **" + str(self.players[ctx.author.id].remaining_guesses) + "** guesses left!"

                # Check guess against correct word
                return_letters = self.correct_word_object.check_word(arg)
                await self.print_to_channel(remaining_string + "\n" + Word.print(return_letters))

                # Add to guess history
                self.guess_history.append(self.format_guess_history(ctx, return_letters))

                # Add letter colors to !letters arrays
                self.update_alphabet(return_letters)
                return

            else:
                await self.print_to_channel("No more guesses remaining!")

    """
    Command to register users for the game
    """
    async def join(self, ctx):
        if not self.players.get(ctx.author.id):
            await self.print_to_channel("**" + str(ctx.author) + "** joined the game!\nYou have **" + str(self.num_guesses) + "** chances to guess the word")
            self.players[ctx.author.id] = Player(ctx.author.id, self.num_guesses)
        else:
            if self.friendly_mode:
                await self.print_to_channel("You've already joined the game!")
            else:
                await self.print_to_channel("You already joined you naughty boy :hot_face:")

    """
    Command to return number of guesses remaining for user
    """
    async def remaining(self, ctx):
        if await self.has_joined(ctx):
            await self.channel.send("**" + str(ctx.author) + "** has **" + str(self.players[ctx.author.id].remaining_guesses) + "** guesses left!")

    """
    Show correct letters in the right spot
    """
    async def correct(self, ctx):
        if await self.has_joined(ctx):
            self.correct_word_object.reset_matched()
            for guess in self.guess_history:
                for i in range(0, len(guess["guess"])):
                    if guess["guess"][i].status == LetterStatus.GREEN:
                        self.correct_word_object.word[i].status = LetterStatus.GREEN
            
            result_string = ""
            
            for letter in self.correct_word_object.word:
                if letter.status == LetterStatus.GREEN:
                    result_string += ":regional_indicator_" + letter.char + ":"
                else:
                    result_string += ":white_square_button:"
            
            await self.print_to_channel("Word with only green letters so far:\n" + result_string)

    """
    Prints history of guessed words for the game
    """
    async def history(self, ctx):
        if await self.has_joined(ctx):
            if len(self.guess_history) > 0:
                print_result = ""
                for guess in self.guess_history:
                    print_result += "***" + guess['author'] + "*** guessed:\n"
                    print_result += Word.print(guess['guess']) + "\n"
                await self.print_to_channel(print_result)
            else:
                await self.print_to_channel("No guesses yet!")

    """
    Lists Green, yellow, white, and black letters
    """
    async def letters(self, ctx):
        if await self.has_joined(ctx):
            green_array = []
            yellow_array = []
            white_array = []
            black_array = []
            for letter in self.alphabet.alphabet_dict:
                if self.alphabet.alphabet_dict[letter] == LetterStatus.GREEN:
                    green_array.append(letter)
                elif self.alphabet.alphabet_dict[letter] == LetterStatus.YELLOW:
                    yellow_array.append(letter)
                elif self.alphabet.alphabet_dict[letter] == LetterStatus.WHITE:
                    white_array.append(letter)
                elif self.alphabet.alphabet_dict[letter] == LetterStatus.BLACK:
                    black_array.append(letter)

            print_string = self.print_list(":green_square:: ", green_array)
            print_string += self.print_list(":yellow_square:: ", yellow_array)
            print_string += self.print_list(":white_large_square:: ", white_array)
            print_string += self.print_list(":black_large_square:: ", black_array)

            await self.print_to_channel(print_string)


    ########################## HELPER FUCNTIONS ##########################
    """
    Queries dictionary to see if word exists or not 
    """
    def word_exists(self, word):
        return self.words_dict.get(word) or self.common_words_dict.get(word)

    """
    Sends gif of word to channel
    """
    async def send_gif(self):
        response = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (self.correct_word, self.TENOR_TOKEN, 1))
        if response.status_code == 200:
            # load the GIFs using the urls for the smaller GIF sizes
            gif = json.loads(response.content)
            embed = discord.Embed()
            gif_url = gif['results'][0]['media'][0]['gif']['url']
            embed.set_image(url=gif_url)
            await self.channel.send(embed=embed)

    """
    Formats dictionary to put into guess_history list
    """
    def format_guess_history(self, ctx, guess):
        return {
            'author': str(ctx.author),
            'guess': guess
        }

    """
    Update the alphabet data structure for the letters command
    """
    def update_alphabet(self, return_word):
        for letter in return_word:
            # If letter is already black, change it to whatever the guess color was
            if self.alphabet.alphabet_dict[letter.char] == LetterStatus.BLACK:
                self.alphabet.alphabet_dict[letter.char] = letter.status

            elif letter.status == LetterStatus.GREEN:
                self.alphabet.alphabet_dict[letter.char] = LetterStatus.GREEN

    """
    Print format for letters function
    """
    def print_list(self, emoji, arr):
        print_arr = emoji
        for letter in arr:
            print_arr += "**" + letter + "** "
        return print_arr + "\n"

    """
    Check to see if player has already joined or not
    """
    async def has_joined(self, ctx):
        if not self.players.get(ctx.author.id):
            if self.friendly_mode:
                await self.channel.send("Join the game first using `!join` or `!j`")
            else:
                await self.channel.send('Join for the game by using !join, baka >///<')
            return False
        return True
        
    """
    Function to print strings to channel
    """
    async def print_to_channel(self, print_string):
        await self.channel.send(print_string)
