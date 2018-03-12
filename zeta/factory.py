
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from zeta.constants import CONV_END


def UnknownTarget(state, start=1, stop=10):
    def unknown_target(bot, update, user_data):
        user = update.message.from_user
        update.message.reply_text(
            f"I'm expecting a number from {start}-{stop}, can you do that for me {user.first_name}.")
        return state
    return unknown_target


def Cancel(msg=CONV_END):
    def cancel(bot, update, user_data):
        update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END
    return cancel