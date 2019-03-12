import logging

from jinja2 import Environment
from jinja2 import FileSystemLoader
from plexapi.server import PlexServer
from requests import Session
from telegram.ext import Filters
from telegram.ext import Updater
from telegram.ext import DispatcherHandlerStop
from telegram.ext import MessageHandler
from telegram import ReplyKeyboardMarkup

from zeta.config import settings
from zeta.conversation import want
from zeta.conversation import refresh
from zeta.radarr import Client as RadarrClient


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


logger = logging.getLogger(__name__)


ENTRY_KEYBOARD = ReplyKeyboardMarkup(
    [[f"/{want.command}"], [f"/{refresh.command}"]],
    one_time_keyboard=True,
)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)
    if update is not None and update.message.from_user.id in settings.admins:
        update.message.reply_text(error)


def how_can_i_help(bot, update):
    update.message.reply_text("How can i help you?", reply_markup=ENTRY_KEYBOARD)


def check_user_permission(bot, update):
    if update.message.from_user.id not in settings.allowed:
        raise DispatcherHandlerStop


def main():
    logger.debug(f"CONFIG: \n{settings}")
    updater = Updater(settings.token)
    bot = updater.bot
    # add central connections we need to the bot


    plex_session = Session()
    plex_session.verify = False
    bot.plex = PlexServer(settings.plex_baseurl, settings.plex_token, session=plex_session)
    bot.radarr = RadarrClient(settings.radarr_baseurl, settings.radarr_apikey)
    bot.j2_env = Environment(loader=FileSystemLoader(settings.template_dir))

    # add all handlers
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.all, check_user_permission), group=0)

    dp.add_handler(want.conversation, group=1)
    dp.add_handler(refresh.conversation, group=1)
    dp.add_handler(MessageHandler(Filters.all, how_can_i_help), group=1)

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
