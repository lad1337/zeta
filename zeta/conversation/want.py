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

from zeta.constants import CONV_END
from zeta.constants import YES_PATTERN

logger = logging.getLogger(__name__)


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
    user_data['want_term'] = term
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
        f"{msg}\n Is it here?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True),
    )

    return State.SEARCH_RADARR


def search_radarr(bot, update, user_data):
    update.message.reply_text(f"Lets look at on the interwebs.")
    return State.CHOOSE_RADARR


def cancel(bot, update):
    update.message.reply_text(CONV_END, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


command = 'want'
conversation = ConversationHandler(
    entry_points=[CommandHandler(command, start)],
    states={
        State.SEARCH_PLEX: [
            MessageHandler(Filters.text, search_plex, pass_user_data=True),
        ],
        State.SEARCH_RADARR: [
            RegexHandler(YES_PATTERN, cancel),
            MessageHandler(Filters.text, search_radarr, pass_user_data=True),
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
