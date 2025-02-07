import os
import subprocess
import asyncio

from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.utils.exceptions import ChatNotFound, TelegramAPIError

created_at = datetime.now().strftime("%Y-%m-%d")

# Configuration
TOKEN = '7358033109:AAG4xjX108GURH3CtYpD4tS9FztMKhBuzt4'  # Replace with your actual bot token
CHAT_ID = '@triumf_post'  # Replace with your channel's chat ID
MESSAGE_ID = '2'
OWNER_USER_ID = 663153232
DB_NAME = 'triumf'
DB_USER = 'husan'
DB_PASSWORD = 'TopGun'
DB_HOST = 'localhost'
DB_PORT = '5432'
BACKUP_DIR = '/home/triumf/backup'
BACKUP_FILENAME = f"{BACKUP_DIR}/triumf_backup_{created_at}.sql"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def backup_database(chat, thread_id=None):
    try:
        # Create backup directory if it doesn't exist
        os.makedirs(BACKUP_DIR, exist_ok=True)

        # Backup command
        backup_command = f"PGPASSWORD={DB_PASSWORD} pg_dump -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} -Fc > {BACKUP_FILENAME}"
        subprocess.run(backup_command, shell=True, check=True)

        # Send the backup file to the specified chat
        with open(BACKUP_FILENAME, "rb") as backup_file:
            await bot.send_document(chat_id=chat, document=backup_file, caption=f"Backup completed at {created_at}", message_thread_id=thread_id)
        
        # Notify the owner of successful backup
        await bot.send_message(OWNER_USER_ID, text=f"Backup successfully completed and sent to chat https://t.me/triumf_post/2.")
        
        # Send a test success message to the group
        await bot.send_message(chat_id=chat, text="Database backup completed successfully.", message_thread_id=thread_id)

        # Delete the backup file after sending
        os.remove(BACKUP_FILENAME)

    except subprocess.CalledProcessError as e:
        await bot.send_message(OWNER_USER_ID, text=f"Backup failed: {e}")
    except ChatNotFound as e:
        await bot.send_message(OWNER_USER_ID, text=f"Chat not found: {e}")
    except TelegramAPIError as e:
        await bot.send_message(OWNER_USER_ID, text=f"Telegram API error: {e}")
    except Exception as e:
        await bot.send_message(OWNER_USER_ID, text=f"Unexpected error: {e}")

async def main():
    await backup_database(CHAT_ID, MESSAGE_ID)
    session = await bot.get_session()
    await session.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
