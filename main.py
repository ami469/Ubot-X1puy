import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from keep_alive import keep_alive

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_NAME = os.environ.get("OWNER_NAME", "Userbot Owner")

userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_help_page(page=1):
    if page == 1:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Ping", callback_data="ping"), InlineKeyboardButton("Alive", callback_data="alive")],
            [InlineKeyboardButton("Spam", callback_data="spam"), InlineKeyboardButton("List/Stop", callback_data="help_liststop")],
            [InlineKeyboardButton("➡️", callback_data="help_page2")]
        ])
    elif page == 2:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Restart", callback_data="restart"), InlineKeyboardButton("Gcast", callback_data="gcast")],
            [InlineKeyboardButton("⬅️", callback_data="help_page1")]
        ])

@userbot.on_message(filters.me & filters.command("ping", prefixes="."))
async def ping_handler(client, message):
    await message.reply("🏓 Pong!")

@userbot.on_message(filters.me & filters.command("alive", prefixes="."))
async def alive_handler(client, message):
    await message.reply(f"🤖 Bot aktif!\n🔥 Owner: <b>{OWNER_NAME}</b>", parse_mode=ParseMode.HTML)

@userbot.on_message(filters.me & filters.command("help", prefixes="."))
async def help_handler(client, message):
    await message.reply("📋 Commands Menu!", reply_markup=get_help_page())

@userbot.on_callback_query()
async def userbot_callback(client, query):
    if query.data == "help_page1":
        await query.message.edit_reply_markup(get_help_page(page=1))
    elif query.data == "help_page2":
        await query.message.edit_reply_markup(get_help_page(page=2))
    else:
        await query.answer(f"Command: {query.data}", show_alert=True)

# BOT TOKEN HANDLERS
@bot.on_message(filters.command("start"))
async def bot_start(client, message):
    await message.reply("👋 Selamat datang!
Gunakan /help untuk melihat menu.", reply_markup=get_help_page(1))

@bot.on_message(filters.command("help"))
async def bot_help(client, message):
    await message.reply("📋 Commands Menu!", reply_markup=get_help_page(1))

@bot.on_callback_query()
async def bot_callback(client, query):
    if query.data == "help_page1":
        await query.message.edit_reply_markup(get_help_page(page=1))
    elif query.data == "help_page2":
        await query.message.edit_reply_markup(get_help_page(page=2))
    else:
        await query.answer(f"Command: {query.data}", show_alert=True)

async def main():
    print("🤖 Menjalankan Userbot & Bot Token...")
    await userbot.start()
    print("✅ Userbot aktif")
    await bot.start()
    print("✅ Bot token aktif")
    await idle()
    print("⛔ Idle selesai")
    await userbot.stop()
    await bot.stop()

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())