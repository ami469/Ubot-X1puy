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

@userbot.on_message(filters.me & filters.command("ping", prefixes="."))
async def ping_handler(client, message):
    await message.reply("🏓 Pong!")

@userbot.on_message(filters.me & filters.command("alive", prefixes="."))
async def alive_handler(client, message):
    await message.reply(f"🤖 Bot aktif!\n🔥 Owner: <b>{OWNER_NAME}</b>", parse_mode=ParseMode.HTML)

@userbot.on_message(filters.me & filters.command("spam", prefixes="."))
async def spam_handler(client, message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        return await message.reply("❌ Format: .spam 5 Halo")
    count = int(args[1])
    text = args[2]
    for _ in range(count):
        await message.reply(text)

@userbot.on_message(filters.me & filters.command("delayspam", prefixes="."))
async def delayspam_handler(client, message):
    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        return await message.reply("⚠️ Format: `.delayspam <jumlah> <delay> <pesan>`")
    try:
        count = int(args[1])
        delay = float(args[2])
        text = args[3]
        async def spam_job():
            job = {"chat_id": message.chat.id, "text": text, "count": count}
            active_delayspam.append(job)
            try:
                for _ in range(count):
                    await client.send_message(message.chat.id, text)
                    await asyncio.sleep(delay)
            except CancelledError:
                await client.send_message(message.chat.id, "⛔ Delay spam dihentikan.")
            finally:
                active_delayspam.remove(job)
        task = asyncio.create_task(spam_job())
        delayspam_tasks.append(task)
    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")

@userbot.on_message(filters.me & filters.command("listdelayspam", prefixes="."))
async def list_handler(client, message):
    if not active_delayspam:
        return await message.reply("✅ Tidak ada delayspam aktif.")
    text = "📋 <b>DelaySpam Aktif:</b>\n\n"
    for i, job in enumerate(active_delayspam, 1):
        text += f"{i}. Chat ID: <code>{job['chat_id']}</code>\n"
        text += f"   Pesan: <code>{job['text']}</code>\n"
        text += f"   Sisa: ~{job['count']} pesan\n\n"
    await message.reply(text, parse_mode=ParseMode.HTML)

@userbot.on_message(filters.me & filters.command("stopdelayspam", prefixes="."))
async def stop_handler(client, message):
    count = 0
    for task in delayspam_tasks:
        if not task.done():
            task.cancel()
            count += 1
    active_delayspam.clear()
    delayspam_tasks.clear()
    await message.reply(f"🛑 Berhasil hentikan {count} spam.")

@userbot.on_message(filters.me & filters.command("restart", prefixes="."))
async def restart_handler(client, message):
    await message.reply("🔄 Restarting...")
    await asyncio.sleep(1)
    os.execv(sys.executable, [sys.executable] + sys.argv)

@userbot.on_message(filters.me & filters.command("help", prefixes="."))
async def help_handler(client, message):
    await message.reply("📋 Commands Menu!", reply_markup=get_help_page(1), parse_mode=ParseMode.HTML)

@userbot.on_callback_query()
async def userbot_callback(client, query):
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
    await message.reply("📋 Commands Menu!", reply_markup=get_help_page(1), parse_mode=ParseMode.HTML)

@bot.on_callback_query()
async def bot_callback(client, query):
    await userbot_callback(client, query)

async def main():
    print("🤖 Menjalankan Userbot & Bot Token...")
    await userbot.start()
    await bot.start()
    await idle()
    print("⛔ Bot dihentikan.")

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())