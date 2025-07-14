import os
import sys
import asyncio
from asyncio import CancelledError
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_NAME = os.environ.get("OWNER_NAME", "Userbot Owner")

userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

active_delayspam = []
delayspam_tasks = []

def get_help_page(page=1):
    if page == 1:
        buttons = [
            [InlineKeyboardButton("Ping", callback_data="ping"), InlineKeyboardButton("Alive", callback_data="alive")],
            [InlineKeyboardButton("Spam", callback_data="spam"), InlineKeyboardButton("DelaySpam", callback_data="delayspam")],
            [InlineKeyboardButton("List/Stop", callback_data="delaycontrol")],
            [InlineKeyboardButton("➡️", callback_data="help_page2")]
        ]
    elif page == 2:
        buttons = [
            [InlineKeyboardButton("Restart", callback_data="restart")],
            [InlineKeyboardButton("⬅️", callback_data="help_page1")]
        ]
    return InlineKeyboardMarkup(buttons)

@userbot.on_message(filters.me & filters.command("help", prefixes="."))
async def help_handler(client, message):
    await message.reply("📋 <b>Commands Menu!</b>", reply_markup=get_help_page(1), parse_mode=ParseMode.HTML)

@userbot.on_callback_query()
async def handle_inline(client, query):
    data = query.data
    if data == "help_page1":
        await query.message.edit_reply_markup(get_help_page(1))
    elif data == "help_page2":
        await query.message.edit_reply_markup(get_help_page(2))
    else:
        await query.answer(f"Command: {data}", show_alert=False)

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("👋 Halo! Kirim /help untuk melihat perintah.")

@bot.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply("📋 <b>Commands Menu!</b>", reply_markup=get_help_page(1), parse_mode=ParseMode.HTML)

@bot.on_callback_query()
async def bot_inline(client, query):
    await handle_inline(client, query)

async def main():
    print("🤖 Menjalankan Userbot & Bot Token...")
    await userbot.start()
    await bot.start()
    await idle()
    await userbot.stop()
    await bot.stop()

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())