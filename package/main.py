from typing import Final
import logging
from telegram import Update
from telegram.ext import Application, Updater, CommandHandler, MessageHandler, CallbackContext, filters, ContextTypes
import asyncio
import nest_asyncio
import keys, commands, source


TOKEN: Final = keys.token
BOT_USERNAME: Final = keys.bot
chat = keys.chat_id


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

def main() -> None:
    nest_asyncio.apply()

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", commands.start))
    application.add_handler(CommandHandler("help", commands.help))
    application.add_handler(CommandHandler("glist", commands.glist))
    application.add_handler(CommandHandler("stat", commands.stat))
    application.add_handler(CommandHandler("set", commands.set_timer))
    application.add_handler(CommandHandler("unset", commands.unset))
    application.add_handler(CommandHandler("graph", commands.graph))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(source.load_data())
    print("Bot running...")
    main()
