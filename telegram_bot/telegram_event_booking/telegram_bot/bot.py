import os
import sys
import django
from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_booking.settings')

# Set up Django environment
django.setup()

from events.models import Event  # Import after Django setup

# Telegram bot token
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Welcome to the University Event Bot! Use /events to see upcoming events and /bookticket <event_id> to get a ticket.')

async def events(update: Update, context: CallbackContext) -> None:
    try:
        # Use sync_to_async to handle Django ORM queries
        events = await sync_to_async(lambda: list(Event.objects.all()))()
        if events:
            message = "Upcoming Events:\n\n"
            for event in events:
                message += (f"Event ID: {event.id}\n"
                            f"Event Name: {event.name}\n"
                            f"Starting on: {event.start_date.strftime('%d-%m-%Y (Timing: %H:%M IST)')} \nEnding on: {event.end_date.strftime('%d-%m-%Y (Timing: %H:%M IST)')}\n"
                            f"Location: {event.location}\n"
                            f"/bookticket {event.id}\n\n")
        else:
            message = "No upcoming events at the moment."
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Error retrieving events: {e}")

async def bookticket(update: Update, context: CallbackContext) -> None:
    if context.args:
        event_id = context.args[0]
        try:
            # Use sync_to_async to handle Django ORM queries
            event = await sync_to_async(lambda: Event.objects.get(id=event_id))()
            message = (f"✔️ Your ticket for {event.name} has been successfully booked.\n\n"
                       f"Details:\n"
                       f"Start Date: {event.start_date.strftime('%d-%m-%Y (Timing: %H:%M IST)')}\n"
                       f"End Date: {event.end_date.strftime('%d-%m-%Y (Timing: %H:%M IST)')}\n"
                       f"Location: {event.location}\n\n"
                       f"For more details visit http://127.0.0.1:8000/events/")
            await update.message.reply_text(message)
        except Event.DoesNotExist:
            await update.message.reply_text("Event not found. Please make sure you used the correct event ID.")
        except Exception as e:
            await update.message.reply_text(f"Error processing ticket: {e}")
    else:
        await update.message.reply_text("No event ID provided. Use /bookticket <event_id> to get your ticket.")

def main():
    # Set up the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("events", events))
    application.add_handler(CommandHandler("bookticket", bookticket))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
