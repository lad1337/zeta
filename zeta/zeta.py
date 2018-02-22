import logging
import os

from telegram.ext import Updater

from zeta.conversation import want
from zeta.conversation import refresh


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


logger = logging.getLogger(__name__)


CONFIG = {k.replace('ZETA_', ''): v for k, v in os.environ.items() if k.startswith('ZETA')}


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    logger.debug("CONFIG: \n{}".format(CONFIG))
    updater = Updater(CONFIG['TOKEN'])
    dp = updater.dispatcher
    dp.add_handler(want.conversation)
    dp.add_handler(refresh.conversation)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
