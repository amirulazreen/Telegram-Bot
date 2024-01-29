import pandas as pd 
from telegram import Update
from telegram.ext import Application, Updater, CommandHandler, MessageHandler, CallbackContext, filters, ContextTypes
import matplotlib.pyplot as plt
import pytz
from datetime import datetime, timedelta, time
import io
from io import BytesIO
import source, graphs

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Hello!\n"
        "I am a blood donations graph bot\n"
        "Use /help for more commands"
    )
    await update.message.reply_text(message)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "The following commands are available :\n"
        "/stat - Blood Donations stats\n"
        "/list - List of graphs available\n"
        "/graph <number> - Display graph e.g. graph 1\n"
        "/set - Set timer to display graphs\n"
        "/unset - Unset timer of displayed graphs"
    )
    await update.message.reply_text(message)

async def glist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Use /graph <number> to display graph:\n"
        "1 - Blood Donations Trend - Malaysia\n"
        "2 - Blood Donors Retention - Malaysia\n"
        "3 - Blood Donations Trend - States\n"
        "4 - Number Of Blood Donations per Hospital\n"
        "5 - Correlation Between Accessibility And Number of Blood Donations\n"
        "6 - Number of Blood Donations Based On Social Groups\n"
        "7 - Number of Blood Donations Based On Blood Type\n"
        "8 - Number Of Blood Donations Based On Age Groups\n"
        "9 - Blood Donors Retention Scatterplot"
    )
    await update.message.reply_text(message)

async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        f"As of {source.current_date}\n"
        f"Number of unique donors: {source.unique_donor:,.0f}\n"
        f"Number of hospitals collecting blood: {source.unique_hospital}\n"
        f"1 blood donation can save up to 3 lives"
    )
    await update.message.reply_text(message)

async def setup(context: ContextTypes.DEFAULT_TYPE) -> None:
    await source.load_data()
    job = context.job
    bot = context.bot

    buffer1 = await graphs.graph1(bot=bot)
    buffer2 = await graphs.graph2(bot=bot)
    buffer3 = await graphs.graph3(bot=bot)

    await bot.send_photo(job.chat_id, photo=buffer1)
    await bot.send_photo(job.chat_id, photo=buffer2)
    await bot.send_photo(job.chat_id, photo=buffer3)

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    try:
        input_time_str = context.args[0]
        input_time = datetime.strptime(input_time_str, "%I:%M%p").time()

        gmt8_timezone = pytz.timezone('Asia/Singapore')
        current_time = datetime.utcnow() + timedelta(hours=8)
        current_time = current_time.time()

        time_until_first_execution = (datetime.combine(datetime.today(), input_time) - datetime.combine(datetime.today(), current_time))
        if time_until_first_execution.total_seconds() < 0:
            time_until_first_execution += timedelta(days=1)

        context.job_queue.run_once(setup, time_until_first_execution.total_seconds(), chat_id=chat_id, name=str(chat_id))

        interval_seconds = 24*60*60

        context.job_queue.run_repeating(setup, interval=interval_seconds, chat_id=chat_id, name=str(chat_id))

        text = f"Following graphs will be displayed every day at {input_time.strftime('%I:%M%p')}\n" \
              "Blood Donation Trend - Malaysia\n" \
              "Blood Donors Retention\n" \
              "Blood Donation Trend - States"

        await update.effective_message.reply_text(text)

    except (IndexError, ValueError) as e:
        await update.effective_message.reply_text("Use /set <HH:MMam/pm>")

async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)

async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        graph_number = context.args[0]

        if graph_number == '1':
            buffer = await graphs.graph1(bot=context.bot, update=update, context=context)
        elif graph_number == '2':
            buffer = await graphs.graph2(bot=context.bot, update=update, context=context)
        elif graph_number == '3':
            buffer = await graphs.graph3(bot=context.bot, update=update, context=context)
        elif graph_number == '4':
            buffer = await graphs.graph4(bot=context.bot, update=update, context=context)
        elif graph_number == '5':
            buffer = await graphs.graph5(bot=context.bot, update=update, context=context)
        elif graph_number == '6':
            buffer = await graphs.graph6(bot=context.bot, update=update, context=context)
        elif graph_number == '7':
            buffer = await graphs.graph7(bot=context.bot, update=update, context=context)
        elif graph_number == '8':
            buffer = await graphs.graph8(bot=context.bot, update=update, context=context)
        elif graph_number == '9':
            buffer = await graphs.graph9(bot=context.bot, update=update, context=context)
        else:
            await update.message.reply_text("Invalid graph number.")
            return

        await context.bot.send_photo(update.effective_chat.id, photo=buffer)

    else:
        await update.message.reply_text("Use /graph <number> e.g. graph 1")
