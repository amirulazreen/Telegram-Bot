import package
from typing import Final
import logging
from telegram import Update
from telegram.ext import Application, Updater, CommandHandler, MessageHandler, CallbackContext, filters, ContextTypes
import asyncio
import nest_asyncio


TOKEN: Final = package.token
BOT_USERNAME: Final = package.bot
chat = package.chat_id


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

def main() -> None:
    nest_asyncio.apply()

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", package.start))
    application.add_handler(CommandHandler("help", package.help))
    application.add_handler(CommandHandler("glist", package.glist))
    application.add_handler(CommandHandler("stat", package.stat))
    application.add_handler(CommandHandler("set", package.set_timer))
    application.add_handler(CommandHandler("unset", package.unset))
    application.add_handler(CommandHandler("graph", graphs.graph))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(package.load_data())
    print("Bot running...")
    main()
