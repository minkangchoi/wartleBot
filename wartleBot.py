import os
import time
import asyncio
from tracemalloc import start
from alphabet import Alphabet

import discord
from datetime import datetime, time, timedelta
from dotenv import load_dotenv
from discord.ext import commands

from letter import LetterStatus
from letter import Letter
from word import Word
from user import User
from alphabet import Alphabet

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='!')

# GLOBAL VARIABLES
word_of_the_day = "unlawful"
game_over = True
word_length = 8
num_guesses = 3
guess_history = [] # Array of array of letters
users = {}
# Arrays for !list
alphabet = Alphabet()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    client.loop.create_task(background_task())

    # CREATE ASSIGNABLE CHANNEL ID LATER
    global channel
    channel = client.get_channel(935648191959933002)


@client.command()
async def guess(ctx, arg):
    if is_registered(ctx.author.id):
        if game_over:
            await ctx.channel.send('The wordle of the day was already guessed!\nPlease wait ') #Add time until next wordle
        else:
            correct_word.reset_matched()

            # Check for correct length
            if len(arg) != word_length:
                await channel.send("Wrong length")
                return

            # Check that word exists
            if not word_exists(arg):
                await channel.send("Word doesnt exist")
                return

            # Case if word is correct
            if arg == correct_word.word_string:
                await channel.send("You guessed the word!")
                change_game_over_state(True)
                return

            # Check if user had guesses remaining
            if users[ctx.author.id].guess():
                # Print number of guesses remaining
                await channel.send("**" + str(ctx.author) + "** has **" + str(users[ctx.author.id].remaining_guesses) + "** guesses left!")

                # Check guess against correct word
                return_letters = correct_word.check_word(arg)

                # Print result of guess
                await channel.send(Word.print(return_letters))

                # Add to guess history
                global guess_history
                guess_history.append(format_guess_history(ctx, return_letters))

                # Add letter colors to !list arrays
                update_alphabet(return_letters)

                return

            else:
                await channel.send("No more guesses remaining!")
    else:
        await not_registered_msg(ctx)


"""
Lists Green, yellow, white, and black letters
"""
@client.command()
async def list(ctx):
    if is_registered(ctx.author.id):
        green_array = []
        yellow_array = []
        white_array = []
        black_array = []
        for letter in alphabet.alphabet_dict:
            if alphabet.alphabet_dict[letter] == LetterStatus.GREEN:
                green_array.append(letter)
            elif alphabet.alphabet_dict[letter] == LetterStatus.YELLOW:
                yellow_array.append(letter)
            elif alphabet.alphabet_dict[letter] == LetterStatus.WHITE:
                white_array.append(letter)
            elif alphabet.alphabet_dict[letter] == LetterStatus.BLACK:
                black_array.append(letter)

        await print_list(":green_square:: ", green_array)
        await print_list(":yellow_square:: ", yellow_array)
        await print_list(":white_large_square:: ", white_array)
        await print_list(":black_large_square:: ", black_array)
        
    else:
        await not_registered_msg(ctx)

async def print_list(emoji, arr):
    print_arr = emoji
    for letter in arr:
        print_arr += "**" + letter + "** "
    await channel.send(print_arr + "\n")


"""
Prints history of guessed words for the day
"""
@client.command()
async def history(ctx):
    if is_registered(ctx.author.id):
        if len(guess_history) > 0:
            for guess in guess_history:
                await channel.send("***" + guess['author'] + "*** guessed:\n")
                await channel.send(Word.print(guess['guess']))
        else:
            await channel.send("No guesses yet!")
    else:
        await not_registered_msg(ctx)


"""
Command to register users for the game
"""
@client.command()
async def join(ctx):
    if not users.get(ctx.author.id):
        await ctx.channel.send(str(ctx.author) + " joined the game!")
        users[ctx.author.id] = User(ctx.author.id, num_guesses)
    else:
        await ctx.channel.send("You already joined you naughty boy :hot_face:")


"""
Command to return number of guesses remaining for user
"""
@client.command()
async def remaining(ctx):
    if is_registered(ctx.author.id):
        await channel.send("**" + str(ctx.author) + "** has **" + str(users[ctx.author.id].remaining_guesses) + "** guesses left!")
    else:
        await not_registered_msg(ctx)


async def not_registered_msg(ctx):
    await ctx.channel.send('Join for the game by using !join, baka >///<')


async def start_new_wordle():
    change_game_over_state(False)

    begin_emoji = ":white_square_button:" * word_length
    await channel.send("Today's Wartle has begun!\n" + begin_emoji)

    # Set word of the day randlomly here
    global correct_word
    correct_word = Word(word_of_the_day)

    # Reset guesses for each registered user
    for user in users.values():
        user.set_guesses(num_guesses)
    
    # Reset guess history
    global guess_history
    guess_history.clear()


async def background_task():
    now = datetime.utcnow()
    while True:
        await start_new_wordle()
        await asyncio.sleep(50000)


def update_alphabet(return_word):
    for letter in return_word:
        # If letter is already black, change it to whatever the guess color was
        if alphabet.alphabet_dict[letter.char] == LetterStatus.BLACK:
            alphabet.alphabet_dict[letter.char] = letter.status

        elif letter.status == LetterStatus.GREEN:
            alphabet.alphabet_dict[letter.char] = LetterStatus.GREEN


def is_registered(id):
    return users.get(id)


def word_exists(word):
    return True

def format_guess_history(ctx, guess):
    return {
        'author': str(ctx.author),
        'guess': guess
    }


def change_game_over_state(val):
    global game_over
    game_over = val

    # if now.time() > WHEN:  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
    #     tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
    #     seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
    #     await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
    # while True:
    #     now = datetime.utcnow() # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
    #     target_time = datetime.combine(now.date(), WHEN)  # 6:00 PM today (In UTC)
    #     seconds_until_target = (target_time - now).total_seconds()
    #     await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
    #     await called_once_a_day()  # Call the helper function that sends the message
    #     tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
    #     seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
    #     await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start a new iteration

client.run(TOKEN)
