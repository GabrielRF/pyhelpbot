import os
from io import StringIO
from contextlib import redirect_stdout

import telebot
from loguru import logger


MESSAGE_SIZE_LIMIT = 500
MESSAGE_LINES_LIMIT = 15
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]


bot = telebot.TeleBot(TELEGRAM_TOKEN)


def pydoc_link(search):
    return f"https://docs.python.org/3/search.html?q={search}&check\\_keywords=yes&area=default"


def build_response(arg, message):
    add_doc_link = False

    message_lines = message.split("\n")
    if len(message_lines) > MESSAGE_LINES_LIMIT:
        message = '\n'.join(message_lines[:MESSAGE_LINES_LIMIT])
        add_doc_link = True

    if len(message) > MESSAGE_SIZE_LIMIT:
        message = message[:MESSAGE_SIZE_LIMIT]
        add_doc_link = True

    message = message.strip()
    if add_doc_link:
        return (
            "```\n"
            f"{message}\n"
            "...\n"
            "```\n"
            f"Link para busca na documentação: {pydoc_link(arg)}"
        )

    return f"```\n{message}\n```"


@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith("/help"))
def main(message):
    try:
        _, arg = message.text.split()
    except ValueError:
        logger.error("Missing argument, text={}", message.text)
        bot.reply_to(message, "Missing argument")
        return

    logger.info("/help, arg={}", arg)

    with StringIO() as buf:
        with redirect_stdout(buf):
            help(arg)
            help_message = buf.getvalue()

    response = build_response(arg, help_message)
    logger.debug("Help message, arg={}, response_size={}, response={!r}",
                 arg, len(response), response)

    bot.reply_to(message, response, parse_mode="Markdown")


bot.polling()
