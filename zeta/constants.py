from telegram import ReplyKeyboardMarkup

YES_PATTERN = '^(Yes|yes|jo|sure)$'
NO_PATTERN = '^(No|no|nope)$'
INT_PATTERN = '^\d+$'

CONV_END = "I hope I could help and if you need anything else just let me know."

YES_NO_KEYBOARD = ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True)