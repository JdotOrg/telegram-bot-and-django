import os
import sys
import django
from asgiref.sync import sync_to_async  # Import sync_to_async for compatibility with Django ORM
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
import uuid  # For generating unique ticket IDs
import barcode  # For generating unique ticket barcodes
from barcode.writer import ImageWriter  # To generate barcodes as images
from io import BytesIO  # For in-memory barcode generation
from django.core.files.base import ContentFile  # Save barcode images as Django file objects

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_booking.settings')

# Set up Django environment
django.setup()

from events.models import Event, Ticket  # Import models after Django setup

# Telegram bot token
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# States for Conversation Handler
ASK_NAME = range(1)

# /start bot command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the Galgotias University Event Booking Bot!\n\nGuide:\n"
        "Use /events to see upcoming events\n"
        "Use /bookticket <event_id> to book a ticket\n"
        "Use /myticket to view your booked tickets.\n"
        "Visit http://127.0.0.1:8000/ for more details."
    )

# /events bot command
async def events(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        events = await sync_to_async(lambda: list(Event.objects.all()))()
        if events:
            message = "Upcoming Events:\n\n"
            for event in events:
                message += (
                    f"Event ID: {event.id}\n"
                    f"Event Name: {event.name}\n"
                    f"Starting on: {event.start_date.strftime('%d-%m-%Y (Timing: %H:%M IST)')} \n"
                    f"Ending on: {event.end_date.strftime('%d-%m-%Y (Timing: %H:%M IST)')}\n"
                    f"Location: {event.location}\n"
                    f"/bookticket {event.id}\n\n"
                )
        else:
            message = "No upcoming events at the moment."
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Error retrieving events: {e}")

# /bookticket bot command: Entry point
async def bookticket_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.args:
        event_id = context.args[0]
        user_id = str(update.message.from_user.id)  # Telegram user ID
        try:
            # Check if the event exists
            event = await sync_to_async(lambda: Event.objects.get(id=event_id))()

            # Check if the user already booked a ticket for the event
            ticket_exists = await sync_to_async(
                lambda: Ticket.objects.filter(user_id=user_id, event=event).exists()
            )()
            if ticket_exists:
                await update.message.reply_text(
                    f"You have already booked a ticket for {event.name}. "
                    "Use /myticket to view your booked tickets."
                )
                return ConversationHandler.END

            # Save the event in user data and prompt for the user's name
            context.user_data['event'] = event
            await update.message.reply_text("Please provide your name:")
            return ASK_NAME
        except Event.DoesNotExist:
            await update.message.reply_text("Event not found. Please make sure you used the correct event ID.")
            return ConversationHandler.END
        except Exception as e:
            await update.message.reply_text(f"Error processing ticket: {e}")
            return ConversationHandler.END
    else:
        await update.message.reply_text("No event ID provided. Use /bookticket <event_id> to get your ticket.")
        return ConversationHandler.END

# Handle user name input and generate the ticket
async def generate_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        user_name = update.message.text
        context.user_data['user_name'] = user_name
        event = context.user_data['event']
        user_id = str(update.message.from_user.id)

        # Generate a unique ticket ID
        ticket_id = str(uuid.uuid4())[:8]

        # Generate a barcode
        barcode_writer = ImageWriter()
        barcode_class = barcode.get_barcode_class('code128')
        barcode_instance = barcode_class(ticket_id, writer=barcode_writer)
        barcode_buffer = BytesIO()
        barcode_instance.write(barcode_buffer)

        # Save barcode to ticket object
        barcode_file = ContentFile(barcode_buffer.getvalue())
        barcode_file.name = f"{ticket_id}.png"

        # Create the ticket
        await sync_to_async(
            lambda: Ticket.objects.create(
                user_id=user_id,
                user_name=user_name,
                event=event,
                ticket_id=ticket_id,
                barcode_image=barcode_file
            )
        )()

        # Send ticket confirmation
        message = (
            f"✔️ Your ticket for {event.name} has been successfully booked.\n\n"
            f"Details:\n"
            f"Name: {user_name}\n"
            f"Ticket ID: {ticket_id}\n"
            f"Start Date: {event.start_date.strftime('%d-%m-%Y (Timing: %H:%M IST)')}\n"
            f"End Date: {event.end_date.strftime('%d-%m-%Y (Timing: %H:%M IST)')}\n"
            f"Location: {event.location}\n\n"
            f"Your ticket barcode is attached below."
        )
        await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())

        # Send barcode image
        barcode_buffer.seek(0)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=barcode_buffer)

        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"Error generating ticket: {e}")
        return ConversationHandler.END

# /myticket bot command
async def myticket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    try:
        tickets = await sync_to_async(
            lambda: list(Ticket.objects.filter(user_id=user_id).select_related('event'))
        )()
        if tickets:
            user_name = tickets[0].user_name  # Retrieve user name from the first ticket
            message = f"Dear {user_name}, your ticket details are below:\n\n"
            for ticket in tickets:
                event = ticket.event
                message += (
                    f"Event: {event.name}\n"
                    f"Location: {event.location}\n"
                    f"Start Date: {event.start_date.strftime('%d-%m-%Y (Timing: %H:%M IST)')}\n"
                    f"End Date: {event.end_date.strftime('%d-%m-%Y (Timing: %H:%M IST)')}\n"
                    f"Ticket ID: {ticket.ticket_id}\n\n"
                )
                # Send ticket barcode image
                if ticket.barcode_image:
                    barcode_buffer = BytesIO(ticket.barcode_image.read())
                    barcode_buffer.seek(0)
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=barcode_buffer)

            await update.message.reply_text(message)
        else:
            await update.message.reply_text("You have not booked any tickets yet.")
    except Exception as e:
        await update.message.reply_text(f"Error retrieving tickets: {e}")

# Cancel conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Booking process canceled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Main program
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler for /bookticket
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("bookticket", bookticket_start)],
        states={ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_ticket)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("events", events))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("myticket", myticket))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
