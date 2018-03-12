from enum import Enum


from telegram import ReplyKeyboardMarkup
from telegram import ParseMode
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import RegexHandler
from telegram.ext import ConversationHandler

from zeta import constants
from zeta.factory import Cancel
from zeta.factory import UnknownTarget


class State(Enum):
    SEARCH_PLEX = 1
    CHOOSE_PLEX = 2


def start(bot, update):
    update.message.reply_text("What do you want to refresh?")
    return State.SEARCH_PLEX


def on_plex(bot, update, user_data):
    user = update.message.from_user
    term = update.message.text
    movies = bot.plex.library.section('Movies')
    template = bot.j2_env.get_template('plex_movie_search_result.html')
    results = movies.search(term)
    if not results:
        update.message.reply_text(f"Seams like there is nothing, i can't help you.")
        return ConversationHandler.END
    user_data[State.CHOOSE_PLEX] = results
    msg = template.render(plex=bot.plex, results=results, user=user)
    update.message.reply_text(
        f"{msg}\nIs it here?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(
            [[i for i in map(str, range(1, len(results) + 1))]],
            one_time_keyboard=True
        ),
    )
    return State.CHOOSE_PLEX


def target_chosen(bot, update, user_data):
    index = int(update.message.text)
    results = user_data[State.CHOOSE_PLEX]
    if index > len(results):
        update.message.reply_text("That was to high, aim lower.")
        return State.CHOOSE_PLEX
    target = user_data[State.CHOOSE_PLEX][index - 1]
    target.refresh()
    update.message.reply_text(f"Refreshing...")
    return ConversationHandler.END


command = 'refresh'
conversation = ConversationHandler(
    entry_points=[CommandHandler(command, start)],
    states={
        State.SEARCH_PLEX: [MessageHandler(Filters.text, on_plex, pass_user_data=True)],
        State.CHOOSE_PLEX: [
            RegexHandler(constants.INT_PATTERN, target_chosen, pass_user_data=True),
            MessageHandler(Filters.text, UnknownTarget(State.CHOOSE_PLEX), pass_user_data=True),
        ]
    },
    fallbacks=[CommandHandler('cancel', Cancel(), pass_user_data=True)]
)
