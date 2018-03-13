from enum import Enum
import logging

from telegram import ReplyKeyboardMarkup
from telegram import ParseMode
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import RegexHandler
from telegram.ext import Filters
from telegram.ext import ConversationHandler

from zeta import constants
from zeta.factory import Cancel
from zeta.factory import UnknownTarget

logger = logging.getLogger(__name__)

RADARR_MAX_RESULTS = 10


class State(Enum):
    SEARCH_PLEX = 2
    SEARCH_RADARR = 3
    CHOOSE_RADARR = 4
    SEARCH_OTHER = 5


def start(bot, update):
    update.message.reply_text("What are you looking for?")
    return State.SEARCH_PLEX


def search_plex(bot, update, user_data):
    user = update.message.from_user
    term = update.message.text
    user_data[State.SEARCH_RADARR] = term
    update.message.reply_text(
        f"'{term}' sounds interesting {user.first_name}, let me take a look what we have.")
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
        reply_markup=constants.YES_NO_KEYBOARD,
    )

    return State.SEARCH_RADARR


def search_radarr(bot, update, user_data):
    update.message.reply_text(f"Lets look around.")
    results = bot.radarr.search(user_data[State.SEARCH_RADARR])
    if not results:
        update.message.reply_text(
            "Couldn't find anything, do you want to look for something else?",
            reply_markup=constants.YES_NO_KEYBOARD,
        )
        return State.SEARCH_OTHER
    user_data[State.CHOOSE_RADARR] = results

    template = bot.j2_env.get_template('radarr_movie_search_result.html')
    user = update.message.from_user
    msg = template.render(results=results[:RADARR_MAX_RESULTS], user=user)
    update.message.reply_text(
        f"{msg}\n Which one?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(
            [
                [i for i in map(str, range(1, min(RADARR_MAX_RESULTS + 1, len(results))))],
                ['/cancel'],
            ],
            one_time_keyboard=True,
        )
    )
    return State.CHOOSE_RADARR


def target_chosen(bot, update, user_data):
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


command = 'want'
conversation = ConversationHandler(
    entry_points=[CommandHandler(command, start)],
    states={
        State.SEARCH_PLEX: [
            MessageHandler(Filters.text, search_plex, pass_user_data=True),
        ],
        State.SEARCH_RADARR: [
            RegexHandler(constants.YES_PATTERN, Cancel()),
            MessageHandler(Filters.text, search_radarr, pass_user_data=True),
        ],
        State.CHOOSE_RADARR: [
            RegexHandler(constants.INT_PATTERN, target_chosen, pass_user_data=True),
            MessageHandler(Filters.text, UnknownTarget(State.CHOOSE_RADARR), pass_user_data=True),
        ],
        State.SEARCH_OTHER: [
            RegexHandler(constants.NO_PATTERN, Cancel(), pass_user_data=True),
            RegexHandler(constants.YES_PATTERN, start),
            MessageHandler(Filters.text, search_plex, pass_user_data=True),
        ]
    },
    fallbacks=[CommandHandler('cancel', Cancel(), pass_user_data=True)]
)
