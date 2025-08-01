import os
import sys
import asyncio
from asyncio import CancelledError
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from html import escape
from panel import keep_alive
from dotenv import load_dotenv
load_dotenv()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_NAME = os.environ.get("OWNER_NAME", "Userbot Owner")

userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

active_delayspam = []
delayspam_tasks = []
active_delayspamf = []
delayspamf_tasks = []

def get_help_text():
    return (
        "📚 <b>Commands Menu</b>\n\n"
        ".ping → Cek ping\n"
        ".alive → Status bot\n"
        ".spam jumlah teks → Spam cepat\n"
        ".delayspam jumlah delay teks → Spam lambat\n"
        ".listdelayspam → Lihat spam aktif\n"
        ".stopdelayspam → Hentikan semua spam\n"
        ".delayspamf dari_chat msg_id jumlah delay → Forward spam\n"
        ".listdelayspamf → Lihat spam forward aktif\n"
        ".stopdelayspamf → Hentikan spam forward\n"
        ".restart → Restart bot\n"
        ".gcast teks → Kirim ke semua chat"
    )

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

@userbot.on_message(filters.me & filters.command("spam", prefixes="."))
async def spam_handler(client, message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        return await message.reply("❌ Format: .spam 5 Halo")
    count = int(args[1])
    text = args[2]
    for _ in range(count):
        await message.reply(text)

@userbot.on_message(filters.me & filters.command("delayspamf", prefixes="."))
async def delayspamf_handler(client, message):
    try:
        args = message.text.split()
        if len(args) < 5:
            await message.reply("⚠️ Format: .delayspamf <from_chat_id> <msg_id> <jumlah> <delay>")
            return

        from_chat = int(args[1]) if args[1].lstrip("-").isdigit() else args[1]
        msg_id = int(args[2])
        jumlah = int(args[3])
        delay = float(args[4])

        to_chat = message.chat.id
        await message.delete()

        job = {
            "from_chat": from_chat,
            "msg_id": msg_id,
            "jumlah": jumlah,
            "to_chat": to_chat
        }
        active_delayspamf.append(job)

        async def forward_job():
            try:
                for _ in range(jumlah):
                    await client.forward_messages(
                        chat_id=to_chat,
                        from_chat_id=from_chat,
                        message_ids=msg_id
                    )
                    await asyncio.sleep(delay)
            except CancelledError:
                await client.send_message(to_chat, "⛔ Delay forward dihentikan.")
            finally:
                if job in active_delayspamf:
                    active_delayspamf.remove(job)

        task = asyncio.create_task(forward_job())
        delayspamf_tasks.append(task)

    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@userbot.on_message(filters.me & filters.command("listdelayspamf", prefixes="."))
async def list_delayspamf_handler(client, message):
    if not active_delayspamf:
        return await message.reply("✅ Tidak ada delayspam forward aktif.")

    text = "📋 <b>DelaySpam Forward Aktif:</b>\n\n"
    for i, job in enumerate(active_delayspamf, 1):
        text += (
            f"{i}. Dari: <code>{job['from_chat']}</code>\n"
            f"   Msg ID: <code>{job['msg_id']}</code>\n"
            f"   Ke: <code>{job['to_chat']}</code>\n"
            f"   Jumlah: <b>{job['jumlah']}</b>\n\n"
        )

    await message.reply(text, parse_mode=ParseMode.HTML)

@userbot.on_message(filters.me & filters.command("stopdelayspamf", prefixes="."))
async def stopf_handler(client, message):
    count = 0
    for task in delayspamf_tasks:
        if not task.done():
            task.cancel()
            count += 1
    active_delayspamf.clear()
    delayspamf_tasks.clear()
    await message.reply(f"🛑 Berhasil hentikan {count} forward spam.")

@userbot.on_message(filters.me & filters.command("delayspam", prefixes="."))
async def delayspam_handler(client, message):
    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        return await message.reply("⚠️ Format: .delayspam <jumlah> <delay> <pesan>")
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
        chat_id = escape(str(job["chat_id"]))
        msg = escape(str(job["text"]))
        count = escape(str(job["count"]))
        text += f"{i}. Chat ID: <code>{chat_id}</code>\n"
        text += f"   Pesan: <code>{msg}</code>\n"
        text += f"   Sisa: ~{count} pesan\n\n"
    
    MAX_LEN = 4000
    if len(text) > MAX_LEN:
        text = text[:MAX_LEN - 50] + "\n\n... (terpotong karena terlalu panjang)"

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

@userbot.on_message(filters.me & filters.command("gcast", prefixes="."))
async def gcast_handler(client, message):
    if len(message.text.split(maxsplit=1)) < 2:
        return await message.reply("⚠️ Format: .gcast pesan")
    text = message.text.split(maxsplit=1)[1]
    sent = 0
    async for dialog in client.get_dialogs():
        try:
            await client.send_message(dialog.chat.id, text)
            sent += 1
        except:
            continue
    await message.reply(f"📢 Gcast selesai! Terkirim ke {sent} chat.")

@userbot.on_message(filters.me & filters.command("help", prefixes="."))
async def help_handler(client, message):
    await message.reply(get_help_text(), reply_markup=get_help_page(1), parse_mode=ParseMode.HTML)

@userbot.on_callback_query()
async def userbot_callback(client, query):
    if query.data == "help_page1":
        await query.message.edit_reply_markup(get_help_page(1))
    elif query.data == "help_page2":
        await query.message.edit_reply_markup(get_help_page(2))
    else:
        await query.answer(f"Command: {query.data}", show_alert=True)

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("👋 Halo! Kirim /help untuk melihat perintah.")

@bot.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply(get_help_text(), reply_markup=get_help_page(1), parse_mode=ParseMode.HTML)

@bot.on_callback_query()
async def bot_callback(client, query):
    await userbot_callback(client, query)

if __name__ == "__main__":
    print("🤖 Menjalankan Userbot & Bot Token...")
    keep_alive()
    userbot.start()
    bot.start()
    print("✅ Semua aktif. Menunggu perintah...")
    idle()
    userbot.stop()
    bot.stop()
    print("⛔ Semua berhenti.")
