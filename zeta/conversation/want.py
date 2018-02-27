from enum import Enum
import logging

from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import ParseMode
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import RegexHandler
from telegram.ext import Filters
from telegram.ext import ConversationHandler

from zeta import constants

logger = logging.getLogger(__name__)

RADARR_MAX_RESULTS = 10


class State(Enum):
    SEARCH_PLEX = 2
    SEARCH_RADARR = 3
    CHOOSE_RADARR = 4


def start(bot, update):
    update.message.reply_text("What are you looking for?")
    return State.SEARCH_PLEX


def search_plex(bot, update, user_data):
    user = update.message.from_user
    term = update.message.text
    user_data[State.SEARCH_RADARR] = term
    update.message.reply_text(
        f"'{term}' sounds interesting {user.first_name}, let me take a look what we have on Plex.")
    movies = bot.plex.library.section('Movies')
    template = bot.j2_env.get_template('plex_movie_search_result.html')
    results = movies.search(term)
    if not results:
        update.message.reply_text(f"Seams like there is nothing, hold on...")
        return search_radarr(bot, update, user_data)
    msg = template.render(plex=bot.plex, results=results, user=user)
    update.message.reply_text(
        f"{msg}\nIs it here?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True),
    )

    return State.SEARCH_RADARR


def search_radarr(bot, update, user_data):
    update.message.reply_text(f"Lets look at on the interwebs.")
    results = bot.radarr.search(user_data[State.SEARCH_RADARR])
    user_data[State.CHOOSE_RADARR] = results

    template = bot.j2_env.get_template('radarr_movie_search_result.html')
    user = update.message.from_user
    msg = template.render(results=results[:RADARR_MAX_RESULTS], user=user)
    update.message.reply_text(
        f"{msg}\n Which one?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(
            [[i for i in map(str, range(1, RADARR_MAX_RESULTS + 1))]],
            one_time_keyboard=True,
        )
    )
    return State.CHOOSE_RADARR


def target_choosen(bot, update, user_data):
    index = int(update.message.text)
    if index > RADARR_MAX_RESULTS:
        update.message.reply_text(
            f"I'm expecting a number from 1-10, can you do that for me {user.first_name}.")
        return State.CHOOSE_RADARR

    update.message.reply_text("On it...")
    movie = user_data[State.CHOOSE_RADARR][index - 1]
    result = bot.radarr.add_movie(movie)
    if result.status_code == 201:
        update.message.reply_text("Okay movie added.")
    elif result.status_code == 400:
        update.message.reply_text("That's already there!")
    else:
        update.message.reply_text("Something went wrong :(")

    return ConversationHandler.END


def unknown_target(bot, update):
    user = update.message.from_user
    update.message.reply_text(
        f"I'm expecting a number from 1-10, can you do that for me {user.first_name}.")
    return State.CHOOSE_RADARR


def cancel(bot, update):
    update.message.reply_text(constants.CONV_END, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


command = 'want'
conversation = ConversationHandler(
    entry_points=[CommandHandler(command, start)],
    states={
        State.SEARCH_PLEX: [
            MessageHandler(Filters.text, search_plex, pass_user_data=True),
        ],
        State.SEARCH_RADARR: [
            RegexHandler(constants.YES_PATTERN, cancel),
            MessageHandler(Filters.text, search_radarr, pass_user_data=True),
        ],
        State.CHOOSE_RADARR: [
            RegexHandler(constants.INT_PATTERN, target_choosen, pass_user_data=True),
            MessageHandler(Filters.text, unknown_target),
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
