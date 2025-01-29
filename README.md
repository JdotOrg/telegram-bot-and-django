# Introduction 
Developing a University Event Booking System using Python Django, React, and MySQL, integrated with a Telegram bot for ticket retrieval. Implemented a web interface to display event information, allowing users to select events and seamlessly retrieve free tickets through Telegram. 
__To use the project you are required to download the code instead of cloning__.

# Steps to setup
1. Download [python](https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe).
2. Open command prompt, and install required literaries and frameworks.
3. Enter following prompt to install `pip install django djangorestframework mysql-connector-python numpy pandas python-telegram-bot aiogram telethon python-dotenv python-barcode django-jet django-jet-reboot`.
4. Download [MySQL](https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.40.0.msi).
5. Install complete MySQL service which includes both server and clint.
6. Open command prompt, run `mysql -u root -p` to run MySQL.
7. Create database by enter following prompt `create database event_db;`

# Working
1. Create `.env` file inside `telegram_bot\telegram_event_booking\event_booking\`.
2. .env ```
DB_PASSWORD="your mysql password"
DJANGO_SECRET_KEY="your django secret key"
TELEGRAM_BOT_TOKEN="your telegram token"``` make sure to remove double colon ""
3. Open terminal in your VSCode and enter telegram_event_booking directory `cd telegram_bot/telegram_event_booking`.

# MySQL connection
1. After entering telegram_event_booking run `python manage.py makemigrations` then `python manage.py migrate`
2. Ensure all connection is satisfied.

# Hosting
1. After all migration is satisfied to host the server run python `manage.py runserver` inside telegram_event_booking directory.
2. Open web brower and open http://127.0.0.1:8000/ to view events, open http://127.0.0.1:8000/admin/ to open admin menu.
3. Once the Django webpage is hosting, create a new terminal.
4. Enter cd `telegram_bot\telegram_event_booking\telegram_bot` to enter telegram_bot where bot.py is located.
5. Enter `python bot.py` to run the bot.

### You are required to go through complete project to enter required tokens and password when needed. 
