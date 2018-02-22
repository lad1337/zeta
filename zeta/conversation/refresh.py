from enum import Enum


from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import RegexHandler
from telegram.ext import ConversationHandler


class State(Enum):
    WHAT = 1
    ON_PLEX = 1


def start(bot, update):
    update.message.reply_text("What do you want to refresh?")
    return State.WHAT


def on_plex(bot, update):
    term = update.message.text
    update.message.reply_text(f"Refreshing {term}")
    return ConversationHandler.END


def cancel(bot, update):
    update.message.reply_text(
        'Bye! I hope we can talk again some day.',
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END

conversation = ConversationHandler(
    entry_points=[CommandHandler('refresh', start)],
    states={
        State.WHAT: [MessageHandler(Filters.all, on_plex)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
