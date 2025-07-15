import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from keep_alive import keep_alive
from asyncio import CancelledError

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
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Ping", callback_data="ping"),
             InlineKeyboardButton("Spam", callback_data="spam")],
            [InlineKeyboardButton("ListDelay", callback_data="listdelayspam"),
             InlineKeyboardButton("➡️", callback_data="help_page2")]
        ])
    elif page == 2:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Restart", callback_data="restart"),
             InlineKeyboardButton("Gcast", callback_data="gcast")],
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

@userbot.on_message(filters.me & filters.command("delayspam", prefixes="."))
async def delayspam_handler(client, message):
    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        return await message.reply("⚠️ Format: .delayspam jumlah delay teks")
    try:
        count = int(args[1])
        delay = float(args[2])
        text = args[3]
        job = {"chat_id": message.chat.id, "text": text, "count": count}
        active_delayspam.append(job)
        async def spam_job():
            try:
                for _ in range(count):
                    await client.send_message(message.chat.id, text)
                    await asyncio.sleep(delay)
            except CancelledError:
                await client.send_message(message.chat.id, "🛑 Delay spam dihentikan.")
            finally:
                active_delayspam.remove(job)
        task = asyncio.create_task(spam_job())
        delayspam_tasks.append(task)
    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")

@userbot.on_message(filters.me & filters.command("listdelayspam", prefixes="."))
async def listdelayspam_handler(client, message):
    if not active_delayspam:
        await message.reply("✅ Tidak ada delayspam aktif.")
    else:
        await message.reply(f"📌 DelaySpam Aktif:
{len(active_delayspam)} tugas berjalan.")

@userbot.on_message(filters.me & filters.command("stopdelayspam", prefixes="."))
async def stopdelayspam_handler(client, message):
    for task in delayspam_tasks:
        task.cancel()
    active_delayspam.clear()
    delayspam_tasks.clear()
    await message.reply("🛑 Semua delay spam dihentikan.")

@userbot.on_message(filters.me & filters.command("restart", prefixes="."))
async def restart_handler(client, message):
    await message.reply("🔄 Bot akan direstart...")
    os.execv(sys.executable, ['python'] + sys.argv)

@userbot.on_message(filters.me & filters.command("gcast", prefixes="."))
async def gcast_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Format: .gcast teks")
    text = message.text.split(maxsplit=1)[1]
    async for dialog in client.get_dialogs():
        try:
            await client.send_message(dialog.chat.id, text)
        except:
            continue
    await message.reply("✅ Gcast selesai.")

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
